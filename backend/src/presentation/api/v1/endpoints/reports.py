"""Report endpoints."""

from datetime import datetime
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi.responses import Response

from src.application.services.report_service import RouteReportService
from src.infrastructure.repositories.appointment_repository import (
    AppointmentRepository,
)
from src.infrastructure.repositories.driver_repository import DriverRepository

router = APIRouter()


async def get_report_service() -> RouteReportService:
    from src.infrastructure.container import container

    return RouteReportService(
        appointment_repository=container.appointment_repository,
        driver_repository=container.driver_repository,
    )


@router.get(
    "/route",
    summary="Gera relatório de Rota Domiciliar",
    response_class=Response,
)
async def generate_route_report(
    driver_id: str = Query(..., description="ID do motorista"),
    date: str = Query(..., description="Data no formato YYYY-MM-DD"),
    nome_unidade: Optional[str] = Query(None),
    nome_marca: Optional[str] = Query(None),
    status: Optional[str] = Query(None),
    service: RouteReportService = Depends(get_report_service),
) -> Response:
    try:
        dt = datetime.fromisoformat(date)
    except Exception:
        raise HTTPException(
            status_code=400, detail="Data inválida. Use YYYY-MM-DD"
        )

    try:
        pdf_bytes = await service.generate_driver_day_report(
            driver_id=driver_id,
            date=dt,
            nome_unidade=nome_unidade,
            nome_marca=nome_marca,
            status=status,
        )
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Erro ao gerar relatório: {str(e)}"
        )

    headers = {
        "Content-Disposition": f"attachment; filename=rota_{driver_id}_{dt.strftime('%Y%m%d')}.pdf"
    }
    return Response(
        content=pdf_bytes, media_type="application/pdf", headers=headers
    )
