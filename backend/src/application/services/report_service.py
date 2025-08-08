"""
Service responsible for generating PDF reports based on a static template.

Current focus: "Rota Domiciliar" report (driver route by day).
"""

from __future__ import annotations

from datetime import datetime, timedelta
from io import BytesIO
from typing import List, Optional, Tuple

from pypdf import PdfReader, PdfWriter
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import mm
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfgen import canvas
from src.domain.entities.appointment import Appointment
from src.infrastructure.repositories.appointment_repository import AppointmentRepository
from src.infrastructure.repositories.driver_repository import DriverRepository


class RouteReportService:
    """Generate route reports using a pre-defined PDF template as background."""

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

        # Fallback: if there is no appointment assigned to the driver, try the same
        # filters without driver_id so the report is not empty. This helps while the
        # assignment flow isn't used.
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

            # Helpers for fonts
            def set_bold(size: int) -> None:
                try:
                    c.setFont("Helvetica-Bold", size)
                except Exception:
                    c.setFont(self.font_main, size)

            def set_regular(size: int) -> None:
                c.setFont(self.font_main, size)

            # Header fields positioned over the header boxes
            set_bold(13)
            c.drawString(26 * mm, 248 * mm, start.strftime("%d/%m/%Y"))  # Data
            c.drawString(92 * mm, 248 * mm, (ap.nome_unidade or ap.nome_marca or ""))  # Região
            c.drawString(145 * mm, 248 * mm, driver.nome_completo)  # Motorista

            # Big time (HH:MM) left area
            set_bold(28)
            c.drawString(33 * mm, 226 * mm, (ap.hora_agendamento or "").rjust(5))

            # Body fields
            set_regular(12)
            nome = ap.nome_paciente
            telefone = ap.telefone or "-"
            unidade_ou_marca = ap.nome_unidade or ap.nome_marca or "-"
            obs = ap.observacoes or "-"
            conf_parts: list[str] = []
            if ap.canal_confirmacao:
                conf_parts.append(ap.canal_confirmacao)
            if ap.data_confirmacao:
                conf_parts.append(ap.data_confirmacao.strftime("%d/%m/%Y"))
            if ap.hora_confirmacao:
                conf_parts.append(ap.hora_confirmacao)
            obs_coleta = " ".join(conf_parts) if conf_parts else "-"

            # Nome / Telefone
            c.drawString(26 * mm, 206 * mm, _truncate(c, nome, 120 * mm))
            c.drawString(150 * mm, 206 * mm, telefone)

            # CEP (—), Rua (unidade/marca), Nº/Complemento em branco
            c.drawString(60 * mm, 191 * mm, _truncate(c, unidade_ou_marca, 110 * mm))

            # Observações
            c.drawString(26 * mm, 162 * mm, _truncate(c, obs, 120 * mm))
            c.drawString(148 * mm, 162 * mm, _truncate(c, obs_coleta, 45 * mm))

            c.showPage()
            c.save()
            buf.seek(0)
            return buf

        for ap in appointments:
            overlay_pages.append(draw_card(ap))

        # If no appointments, still create a single page with header and message
        if not overlay_pages:
            buf = BytesIO()
            c = canvas.Canvas(buf, pagesize=A4)
            c.setFont(self.font_main, 12)
            c.drawString(30 * mm, 270 * mm, f"Motorista: {driver.nome_completo}")
            c.drawString(160 * mm, 270 * mm, f"Data: {start.strftime('%d/%m/%Y')}")
            c.setFont(self.font_main, 11)
            c.drawString(
                30 * mm, 250 * mm, "Sem agendamentos para os filtros informados."
            )
            c.showPage()
            c.save()
            buf.seek(0)
            overlay_pages.append(buf)

        # Merge overlay on top of template pages
        result_pdf = BytesIO()
        writer = PdfWriter()
        try:
            template_reader = PdfReader(self.template_path)
            template_page = template_reader.pages[0]
        except Exception as exc:  # Template missing inside container
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
                page.merge_transformed_page(overlay_reader.pages[0], [1, 0, 0, 1, 0, 0])

        writer.write(result_pdf)
        return result_pdf.getvalue()


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
