"""
Appointment API endpoints.
"""

import io
import time
from typing import Dict, List

from fastapi import APIRouter, Depends, File, HTTPException, Query, UploadFile
from fastapi.responses import JSONResponse

from src.application.dtos.appointment_dto import (
    AppointmentFilterDTO,
    AppointmentListResponseDTO,
    AppointmentResponseDTO,
    AppointmentUpdateDTO,
    DashboardStatsDTO,
    ExcelUploadResponseDTO,
    FilterOptionsDTO,
)
from src.application.services.address_normalization_service import (
    AddressNormalizationService,
)
from src.application.services.appointment_service import AppointmentService
from src.application.services.excel_parser_service import ExcelParserService
from src.infrastructure.config import Settings, get_settings
from src.infrastructure.container import get_appointment_repository
from src.infrastructure.repositories.appointment_repository import (
    AppointmentRepository,
)
from src.presentation.api.responses import (
    BaseResponse,
    DataResponse,
    ListResponse,
)

router = APIRouter()


# Dependency to get appointment service
async def get_appointment_service(
    appointment_repository: AppointmentRepository = Depends(
        get_appointment_repository
    ),
    settings: Settings = Depends(get_settings),
) -> AppointmentService:
    """Get appointment service instance."""
    try:
        # Use settings to get the correct model and API key
        address_service = AddressNormalizationService(
            api_key=settings.openrouter_api_key,
            model=settings.openrouter_model,
            base_url=settings.openrouter_base_url,
        )
        excel_parser = ExcelParserService(address_service)
    except ValueError:
        # OpenRouter not configured, continue without address normalization
        excel_parser = ExcelParserService()
    return AppointmentService(appointment_repository, excel_parser)


@router.post(
    "/upload",
    response_model=ExcelUploadResponseDTO,
    summary="Upload Excel file with appointments",
    description="Upload and process Excel file containing appointment data",
)
async def upload_excel_file(
    file: UploadFile = File(...),
    replace_existing: bool = Query(
        False, description="Replace existing appointments"
    ),
    service: AppointmentService = Depends(get_appointment_service),
) -> ExcelUploadResponseDTO:
    """
    Upload Excel file with appointments.

    Args:
        file: Excel file to upload
        replace_existing: Whether to replace existing appointments
        service: Appointment service instance

    Returns:
        ExcelUploadResponseDTO: Upload result
    """
    # Validate file
    if not file.filename:
        raise HTTPException(
            status_code=400, detail="Nome do arquivo é obrigatório"
        )

    # Check file extension
    allowed_extensions = [".xlsx", ".xls", ".csv"]
    if not any(
        file.filename.lower().endswith(ext) for ext in allowed_extensions
    ):
        raise HTTPException(
            status_code=400,
            detail=f"Formato de arquivo não suportado. Formatos permitidos: {', '.join(allowed_extensions)}",
        )

    # Check file size (max 10MB)
    max_size = 10 * 1024 * 1024  # 10MB
    if file.size and file.size > max_size:
        raise HTTPException(
            status_code=400,
            detail="Arquivo muito grande. Tamanho máximo: 10MB",
        )

    try:
        # Read file content
        start_time = time.time()
        content = await file.read()
        file_stream = io.BytesIO(content)

        # Process file
        result = await service.import_appointments_from_excel(
            file_stream, file.filename, replace_existing
        )

        # Calculate processing time
        processing_time = time.time() - start_time

        return ExcelUploadResponseDTO(
            success=result["success"],
            message=result["message"],
            filename=file.filename,
            total_rows=result["total_rows"],
            valid_rows=result["valid_rows"],
            invalid_rows=result["invalid_rows"],
            imported_appointments=result["imported_appointments"],
            errors=result["errors"],
            processing_time=processing_time,
        )

    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Erro interno do servidor: {str(e)}"
        )


@router.get(
    "/",
    response_model=AppointmentListResponseDTO,
    summary="Get appointments with filters",
    description="Get appointments with optional filters and pagination",
)
async def get_appointments(
    nome_unidade: str = Query(None, description="Filtrar por nome da unidade"),
    nome_marca: str = Query(None, description="Filtrar por nome da marca"),
    data_inicio: str = Query(None, description="Data de início (YYYY-MM-DD)"),
    data_fim: str = Query(None, description="Data de fim (YYYY-MM-DD)"),
    status: str = Query(None, description="Filtrar por status"),
    driver_id: str = Query(None, description="Filtrar por ID do motorista"),
    page: int = Query(1, ge=1, description="Número da página"),
    page_size: int = Query(50, ge=1, le=100, description="Itens por página"),
    service: AppointmentService = Depends(get_appointment_service),
) -> AppointmentListResponseDTO:
    """
    Get appointments with filters and pagination.

    Args:
        nome_unidade: Filter by unit name
        nome_marca: Filter by brand name
        data_inicio: Start date filter
        data_fim: End date filter
        status: Status filter
        page: Page number
        page_size: Items per page
        service: Appointment service instance

    Returns:
        AppointmentListResponseDTO: Filtered appointments
    """
    try:
        result = await service.get_appointments_with_filters(
            nome_unidade=nome_unidade,
            nome_marca=nome_marca,
            data_inicio=data_inicio,
            data_fim=data_fim,
            status=status,
            driver_id=driver_id,
            page=page,
            page_size=page_size,
        )

        # Convert to response DTOs
        appointments = [
            AppointmentResponseDTO(**apt) for apt in result["appointments"]
        ]

        return AppointmentListResponseDTO(
            success=result["success"],
            message=result.get("message"),
            appointments=appointments,
            pagination=result["pagination"],
        )

    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Erro interno do servidor: {str(e)}"
        )


@router.get(
    "/filter-options",
    response_model=FilterOptionsDTO,
    summary="Get filter options",
    description="Get available filter options for appointments",
)
async def get_filter_options(
    service: AppointmentService = Depends(get_appointment_service),
) -> FilterOptionsDTO:
    """
    Get available filter options.

    Args:
        service: Appointment service instance

    Returns:
        FilterOptionsDTO: Available filter options
    """
    try:
        result = await service.get_filter_options()

        return FilterOptionsDTO(
            success=result["success"],
            message=result.get("message"),
            units=result["units"],
            brands=result["brands"],
            statuses=result["statuses"],
        )

    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Erro interno do servidor: {str(e)}"
        )


@router.get(
    "/stats",
    response_model=DashboardStatsDTO,
    summary="Get dashboard statistics",
    description="Get appointment statistics for dashboard",
)
async def get_dashboard_stats(
    service: AppointmentService = Depends(get_appointment_service),
) -> DashboardStatsDTO:
    """
    Get dashboard statistics.

    Args:
        service: Appointment service instance

    Returns:
        DashboardStatsDTO: Dashboard statistics
    """
    try:
        result = await service.get_dashboard_stats()

        return DashboardStatsDTO(
            success=result["success"],
            message=result.get("message"),
            stats=result["stats"],
        )

    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Erro interno do servidor: {str(e)}"
        )


@router.get(
    "/{appointment_id}",
    response_model=DataResponse[AppointmentResponseDTO],
    summary="Get appointment by ID",
    description="Get a specific appointment by ID",
)
async def get_appointment(
    appointment_id: str,
    service: AppointmentService = Depends(get_appointment_service),
) -> DataResponse[AppointmentResponseDTO]:
    """
    Get appointment by ID.

    Args:
        appointment_id: Appointment ID
        service: Appointment service instance

    Returns:
        DataResponse[AppointmentResponseDTO]: Appointment data
    """
    try:
        # Get appointment repository directly for this simple operation
        repo = await get_appointment_repository()
        appointment = await repo.find_by_id(appointment_id)

        if not appointment:
            raise HTTPException(
                status_code=404, detail="Agendamento não encontrado"
            )

        return DataResponse(
            success=True,
            message="Agendamento encontrado",
            data=AppointmentResponseDTO(**appointment.model_dump()),
        )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Erro interno do servidor: {str(e)}"
        )


@router.put(
    "/{appointment_id}/status",
    response_model=DataResponse[AppointmentResponseDTO],
    summary="Update appointment status",
    description="Update the status of an appointment",
)
async def update_appointment_status(
    appointment_id: str,
    new_status: str = Query(..., description="Novo status"),
    service: AppointmentService = Depends(get_appointment_service),
) -> DataResponse[AppointmentResponseDTO]:
    """
    Update appointment status.

    Args:
        appointment_id: Appointment ID
        new_status: New status value
        service: Appointment service instance

    Returns:
        DataResponse[AppointmentResponseDTO]: Updated appointment
    """
    try:
        result = await service.update_appointment_status(
            appointment_id, new_status
        )

        if not result["success"]:
            raise HTTPException(
                status_code=(
                    400 if "não encontrado" not in result["message"] else 404
                ),
                detail=result["message"],
            )

        return DataResponse(
            success=True,
            message=result["message"],
            data=AppointmentResponseDTO(**result["appointment"]),
        )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Erro interno do servidor: {str(e)}"
        )


@router.delete(
    "/{appointment_id}",
    response_model=BaseResponse,
    summary="Delete appointment",
    description="Delete an appointment by ID",
)
async def delete_appointment(
    appointment_id: str,
    service: AppointmentService = Depends(get_appointment_service),
) -> BaseResponse:
    """
    Delete appointment.

    Args:
        appointment_id: Appointment ID
        service: Appointment service instance

    Returns:
        BaseResponse: Delete result
    """
    try:
        result = await service.delete_appointment(appointment_id)

        if not result["success"]:
            raise HTTPException(
                status_code=(
                    404 if "não encontrado" in result["message"] else 400
                ),
                detail=result["message"],
            )

        return BaseResponse(success=True, message=result["message"])

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Erro interno do servidor: {str(e)}"
        )


@router.put(
    "/{appointment_id}",
    response_model=DataResponse[AppointmentResponseDTO],
    summary="Update appointment",
    description="Update appointment data (currently supports driver assignment)",
)
async def update_appointment(
    appointment_id: str,
    update_data: AppointmentUpdateDTO,
    service: AppointmentService = Depends(get_appointment_service),
) -> DataResponse[AppointmentResponseDTO]:
    """
    Update appointment.

    Args:
        appointment_id: Appointment ID
        update_data: Data to update
        service: Appointment service instance

    Returns:
        DataResponse: Update result
    """
    try:
        # For now, only support driver updates
        result = await service.update_appointment_driver(
            appointment_id, update_data.driver_id
        )

        if not result["success"]:
            raise HTTPException(
                status_code=(
                    404 if "não encontrado" in result["message"] else 400
                ),
                detail=result["message"],
            )

        return DataResponse(
            success=True,
            message=result["message"],
            data=AppointmentResponseDTO(**result["appointment"]),
        )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Erro interno do servidor: {str(e)}"
        )


@router.put(
    "/{appointment_id}/collector",
    response_model=DataResponse[AppointmentResponseDTO],
    summary="Update appointment collector",
    description="Update the collector assigned to an appointment",
)
async def update_appointment_collector(
    appointment_id: str,
    collector_id: str = Query(None, description="ID da coletora"),
    service: AppointmentService = Depends(get_appointment_service),
) -> DataResponse[AppointmentResponseDTO]:
    """
    Update appointment collector.

    Args:
        appointment_id: Appointment ID
        collector_id: Collector ID
        service: Appointment service instance

    Returns:
        DataResponse: Update result
    """
    try:
        result = await service.update_appointment_collector(
            appointment_id, collector_id
        )

        if not result["success"]:
            raise HTTPException(
                status_code=(
                    404 if "não encontrado" in result["message"] else 400
                ),
                detail=result["message"],
            )

        return DataResponse(
            success=True,
            message=result["message"],
            data=AppointmentResponseDTO(**result["appointment"]),
        )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Erro interno do servidor: {str(e)}"
        )


@router.post(
    "/normalize-addresses",
    response_model=BaseResponse,
    summary="Normalize addresses",
    description="Re-normalize addresses for appointments using OpenRouter AI",
)
async def normalize_addresses(
    appointment_ids: List[str] = Query(
        None, description="Lista de IDs específicos para normalizar (opcional)"
    ),
    service: AppointmentService = Depends(get_appointment_service),
    settings: Settings = Depends(get_settings),
) -> BaseResponse:
    """
    Normalize addresses for existing appointments.

    Args:
        appointment_ids: Optional list of specific appointment IDs to normalize.
                        If not provided, will process all appointments with endereco_completo.
        service: Appointment service instance

    Returns:
        BaseResponse: Normalization result with summary
    """
    try:
        # Check if OpenRouter is configured
        try:
            address_service = AddressNormalizationService(
                api_key=settings.openrouter_api_key,
                model=settings.openrouter_model,
                base_url=settings.openrouter_base_url,
            )
        except ValueError:
            raise HTTPException(
                status_code=503,
                detail="Serviço de normalização não configurado. Configure a variável OPENROUTER_API_KEY.",
            )

        # Get appointments to normalize
        repo = await get_appointment_repository()

        if appointment_ids:
            # Normalize specific appointments
            appointments = []
            for app_id in appointment_ids:
                appointment = await repo.find_by_id(app_id)
                if appointment:
                    appointments.append(appointment)
        else:
            # Normalize all appointments with endereco_completo but no endereco_normalizado
            all_appointments = await repo.find_by_filters(skip=0, limit=10000)
            appointments = [
                app
                for app in all_appointments
                if app.endereco_completo and not app.endereco_normalizado
            ]

        if not appointments:
            return BaseResponse(
                success=True,
                message="Nenhum agendamento encontrado para normalização",
            )

        # Normalize addresses
        normalized_count = 0
        error_count = 0

        for appointment in appointments:
            try:
                if appointment.endereco_completo:
                    normalized = await address_service.normalize_address(
                        appointment.endereco_completo
                    )

                    if normalized:
                        # Update the appointment with normalized address
                        updated_appointment = appointment.model_copy(
                            update={"endereco_normalizado": normalized}
                        )

                        # Save to database
                        await repo.update(appointment.id, updated_appointment)
                        normalized_count += 1
                    else:
                        error_count += 1

            except Exception as e:
                print(
                    f"Erro normalizando endereço do agendamento {appointment.id}: {e}"
                )
                error_count += 1

        message = f"Normalização concluída. {normalized_count} endereços normalizados"
        if error_count > 0:
            message += f", {error_count} erros encontrados"

        return BaseResponse(success=True, message=message)

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Erro interno do servidor: {str(e)}"
        )
