"""
Service responsible for generating PDF reports based on a static template.

Current focus: "Rota Domiciliar" report (driver route by day).
"""

from __future__ import annotations

from datetime import datetime, timedelta
from io import BytesIO
from typing import List, Optional, Tuple

from pypdf import PdfReader, PdfWriter  # type: ignore[import-not-found]
from reportlab.lib.pagesizes import A4  # type: ignore[import-not-found]
from reportlab.lib.units import mm  # type: ignore[import-not-found]
from reportlab.pdfbase import pdfmetrics  # type: ignore[import-not-found]
from reportlab.pdfbase.ttfonts import TTFont  # type: ignore[import-not-found]
from reportlab.pdfgen import canvas  # type: ignore[import-not-found]

from src.domain.entities.appointment import Appointment
from src.infrastructure.repositories.appointment_repository import (
    AppointmentRepository,
)
from src.infrastructure.repositories.driver_repository import DriverRepository


class RouteReportService:
    """Generate route reports overlaying content on a static PDF template."""

    def __init__(
        self,
        appointment_repository: AppointmentRepository,
        driver_repository: DriverRepository,
        template_path: str = "docs/template/Template Rota Domiciliar.pdf",
    ) -> None:
        self.appointment_repository = appointment_repository
        self.driver_repository = driver_repository
        self.template_path = template_path

        # Register a font with good Latin support
        try:
            pdfmetrics.registerFont(TTFont("DejaVu", "DejaVuSans.ttf"))
            self.font_main = "DejaVu"
        except Exception:
            # Fallback to default
            self.font_main = "Helvetica"

    async def generate_driver_day_report(
        self,
        driver_id: str,
        date: datetime,
        nome_unidade: Optional[str] = None,
        nome_marca: Optional[str] = None,
        status: Optional[str] = None,
    ) -> bytes:
        """Generate PDF for a single driver on a specific date.

        Returns raw PDF bytes.
        """
        # Load driver
        driver = await self.driver_repository.find_by_id(driver_id)
        if driver is None:
            raise ValueError("Motorista não encontrado")

        # Date range (midnight to 23:59:59)
        start = datetime(year=date.year, month=date.month, day=date.day)
        end = start + timedelta(days=1) - timedelta(seconds=1)

        # Fetch appointments
        appointments = await self.appointment_repository.find_by_filters(
            nome_unidade=nome_unidade,
            nome_marca=nome_marca,
            data_inicio=start,
            data_fim=end,
            status=status,
            driver_id=driver_id,  # type: ignore[arg-type]
            skip=0,
            limit=10_000,
        )

        # Fallback: if there is no appointment assigned to the driver, try the
        # same filters without driver_id so the report is not empty. This helps
        # while the assignment flow isn't used.
        if not appointments:
            appointments = await self.appointment_repository.find_by_filters(
                nome_unidade=nome_unidade,
                nome_marca=nome_marca,
                data_inicio=start,
                data_fim=end,
                status=status,
                skip=0,
                limit=10_000,
            )

        # Sort by unit, then time
        def time_key(a: Appointment) -> Tuple[str, int, int]:
            try:
                h, m = (a.hora_agendamento or "00:00").split(":")
                return (a.nome_unidade or "", int(h), int(m))
            except Exception:
                return (a.nome_unidade or "", 0, 0)

        appointments.sort(key=time_key)

        # Prepare overlay pages (one appointment per page to match card layout)
        overlay_pages: List[BytesIO] = []

        def draw_card(ap: Appointment) -> BytesIO:
            buf = BytesIO()
            c = canvas.Canvas(buf, pagesize=A4)
            page_width_pt, _ = A4

            # Helpers for fonts
            def set_bold(size: int) -> None:
                try:
                    c.setFont("Helvetica-Bold", size)
                except Exception:
                    c.setFont(self.font_main, size)

            def set_regular(size: int) -> None:
                c.setFont(self.font_main, size)

            # Header fields
            # Data (esquerda)
            set_bold(18)
            c.drawString(26 * mm, 275 * mm, start.strftime("%d/%m/%Y"))

            # Centro: "<Unidade ou Marca> <Motorista>" como no modelo
            header_center = (
                f"{(ap.nome_unidade or ap.nome_marca or '').strip()} "
                f"{driver.nome_completo}"
            ).strip()
            set_bold(22)
            c.drawCentredString(page_width_pt / 2, 275 * mm, header_center)

            # Horário grande (HH:MM) à esquerda
            set_bold(92)
            c.drawCentredString(
                65 * mm,
                220 * mm,
                (ap.hora_agendamento or "").rjust(5),
            )

            # Body fields
            set_regular(20)
            nome = ap.nome_paciente
            telefone = ap.telefone or "-"
            unidade_ou_marca = ap.nome_unidade or ap.nome_marca or "-"
            obs = ap.carro or "-"
            conf_parts: list[str] = []
            if ap.canal_confirmacao:
                conf_parts.append(ap.canal_confirmacao)
            if ap.data_confirmacao:
                conf_parts.append(ap.data_confirmacao.strftime("%d/%m/%Y"))
            if ap.hora_confirmacao:
                conf_parts.append(ap.hora_confirmacao)
            obs_coleta = " ".join(conf_parts) if conf_parts else "-"

            # Nome (esquerda) / Telefone (direita)
            c.drawString(26 * mm, 188 * mm, _truncate(c, nome, 120 * mm))
            c.drawRightString(185 * mm, 188 * mm, telefone)

            # Unidade/Marca centralizada logo abaixo
            c.setFont(self.font_main, 22)
            c.drawCentredString(
                page_width_pt / 2,
                170 * mm,
                _truncate(c, unidade_ou_marca, 150 * mm),
            )

            # Endereço normalizado (se disponível)
            endereco_linha = self._format_address(ap)
            if endereco_linha:
                c.setFont(self.font_main, 14)
                c.drawString(26 * mm, 130 * mm, "Endereço:")
                c.setFont(self.font_main, 12)
                c.drawString(
                    26 * mm, 120 * mm, _truncate(c, endereco_linha, 160 * mm)
                )

            # Observações (menor, discretas) — ficam mais abaixo
            c.setFont(self.font_main, 12)
            obs_y = 105 * mm if endereco_linha else 148 * mm
            c.drawString(26 * mm, obs_y, _truncate(c, obs, 120 * mm))
            c.drawRightString(
                193 * mm,
                obs_y,
                _truncate(c, obs_coleta, 60 * mm),
            )

            # Pequenos marcadores '-' perto do rodapé, esquerda e direita
            c.setFont(self.font_main, 18)
            c.drawString(26 * mm, 22 * mm, "-")
            c.drawRightString(193 * mm, 22 * mm, "-")

            c.showPage()
            c.save()
            buf.seek(0)
            return buf

        for ap in appointments:
            overlay_pages.append(draw_card(ap))

        # If no appointments, still create a single page with a short message
        if not overlay_pages:
            buf = BytesIO()
            c = canvas.Canvas(buf, pagesize=A4)
            c.setFont(self.font_main, 12)
            c.drawString(
                30 * mm,
                270 * mm,
                f"Motorista: {driver.nome_completo}",
            )
            c.drawString(
                160 * mm,
                270 * mm,
                f"Data: {start.strftime('%d/%m/%Y')}",
            )
            c.setFont(self.font_main, 11)
            c.drawString(30 * mm, 250 * mm, "Sem agendamentos com os filtros.")
            c.showPage()
            c.save()
            buf.seek(0)
            overlay_pages.append(buf)

        # Merge overlay on top of template pages
        result_pdf = BytesIO()
        writer = PdfWriter()
        # Try multiple candidate paths for the template
        candidates = [
            self.template_path,
            "../docs/template/Template Rota Domiciliar.pdf",
            "/app/../docs/template/Template Rota Domiciliar.pdf",
        ]
        template_page = None
        for cand in candidates:
            try:
                template_reader = PdfReader(cand)
                template_page = template_reader.pages[0]
                break
            except Exception:
                continue
        if template_page is None:
            # Fallback: return overlay-only PDF
            for overlay in overlay_pages:
                overlay_reader = PdfReader(overlay)
                writer.add_page(overlay_reader.pages[0])
            writer.write(result_pdf)
            return result_pdf.getvalue()

        # Overlay each rendered page directly onto a fresh copy of the
        # template's first page, then append to the final writer
        for overlay in overlay_pages:
            overlay_reader = PdfReader(overlay)

            # Add a new page cloned from template
            writer.add_page(template_page)
            page = writer.pages[-1]

            try:
                page.merge_page(overlay_reader.pages[0])
            except AttributeError:
                # pypdf >=4 alternative API
                page.merge_transformed_page(
                    overlay_reader.pages[0],
                    [1, 0, 0, 1, 0, 0],
                )

        writer.write(result_pdf)
        return result_pdf.getvalue()

    def _format_address(self, appointment: Appointment) -> Optional[str]:
        """
        Format address for display on route report.

        Prioritizes normalized address components, falls back to complete address.
        """
        if appointment.endereco_normalizado:
            addr = appointment.endereco_normalizado
            parts = []

            # Rua e número
            if addr.get("rua") and addr.get("numero"):
                parts.append(f"{addr['rua']}, {addr['numero']}")
            elif addr.get("rua"):
                parts.append(addr["rua"])

            # Complemento
            if addr.get("complemento"):
                parts.append(addr["complemento"])

            # Bairro
            if addr.get("bairro"):
                parts.append(addr["bairro"])

            # Cidade e estado
            cidade_estado = []
            if addr.get("cidade"):
                cidade_estado.append(addr["cidade"])
            if addr.get("estado"):
                cidade_estado.append(addr["estado"])
            if cidade_estado:
                parts.append(" - ".join(cidade_estado))

            # CEP
            if addr.get("cep"):
                parts.append(f"CEP: {addr['cep']}")

            if parts:
                return " | ".join(parts)

        # Fallback para endereço completo ou endereço de coleta
        return appointment.endereco_completo or appointment.endereco_coleta


def _truncate(c: canvas.Canvas, text: str, max_width: float) -> str:
    """Truncate text to fit in the given width with ellipsis if needed."""
    if not text:
        return ""
    w = c.stringWidth(text)
    if w <= max_width:
        return text
    ell = "…"
    for i in range(len(text), 0, -1):
        t = text[:i] + ell
        if c.stringWidth(t) <= max_width:
            return t
    return text[:1]
