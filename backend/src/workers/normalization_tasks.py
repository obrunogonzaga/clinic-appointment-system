"""Background tasks for appointment data normalization."""

import logging
from typing import Dict, Optional

from arq import Retry

from src.domain.entities.appointment import NormalizationStatus
from src.infrastructure.config import get_settings
from src.infrastructure.container import Container

settings = get_settings()


logger = logging.getLogger(__name__)


async def normalize_appointment(ctx: Dict, appointment_id: str) -> Dict:
    """
    Background task to normalize appointment address and document data.

    Args:
        ctx: ARQ context dictionary
        appointment_id: ID of the appointment to normalize

    Returns:
        Dictionary with normalization results

    Raises:
        Retry: If normalization should be retried
    """
    logger.info("Starting normalization for appointment %s", appointment_id)

    try:
        # Initialize container and get dependencies
        container = Container()
        appointment_repo = container.appointment_repository

        # Initialize normalization services
        from src.application.services.address_normalization_service import (
            AddressNormalizationService,
        )
        from src.application.services.document_normalization_service import (
            DocumentNormalizationService,
        )

        address_service = AddressNormalizationService()
        document_service = DocumentNormalizationService()

        # Mark as processing
        await appointment_repo.update(
            appointment_id,
            {
                "normalization_status": NormalizationStatus.PROCESSING.value,
            },
        )

        # Fetch appointment
        appointment = await appointment_repo.find_by_id(appointment_id)
        if not appointment:
            logger.error("Appointment %s not found", appointment_id)
            return {
                "success": False,
                "error": "Appointment not found",
            }

        update_data: Dict[str, Optional[str]] = {}
        errors: list[str] = []

        # Normalize address if enabled and not already normalized
        if (
            settings.address_normalization_enabled
            and appointment.endereco_completo
            and not appointment.endereco_normalizado
        ):
            try:
                logger.info(
                    "Normalizing address for appointment %s", appointment_id
                )
                normalized_address = await address_service.normalize_address(
                    appointment.endereco_completo
                )
                if normalized_address:
                    update_data["endereco_normalizado"] = normalized_address
                    logger.info(
                        "Address normalized for appointment %s", appointment_id
                    )
            except Exception as exc:
                error_msg = f"Address normalization failed: {exc}"
                logger.warning(
                    "Address normalization failed for %s: %s",
                    appointment_id,
                    exc,
                )
                errors.append(error_msg)

        # Normalize documents if enabled and not already normalized
        if (
            settings.address_normalization_enabled  # Use same setting
            and appointment.documento_completo
            and not appointment.documento_normalizado
        ):
            try:
                logger.info(
                    "Normalizing documents for appointment %s", appointment_id
                )
                normalized_docs = await document_service.normalize_documents(
                    appointment.documento_completo
                )
                if normalized_docs:
                    update_data["documento_normalizado"] = normalized_docs

                    # Extract CPF and RG if present
                    if normalized_docs.get("cpf"):
                        update_data["cpf"] = normalized_docs["cpf"]
                    if normalized_docs.get("rg"):
                        update_data["rg"] = normalized_docs["rg"]

                    logger.info(
                        "Documents normalized for appointment %s",
                        appointment_id,
                    )
            except Exception as exc:
                error_msg = f"Document normalization failed: {exc}"
                logger.warning(
                    "Document normalization failed for %s: %s",
                    appointment_id,
                    exc,
                )
                errors.append(error_msg)

        # Update appointment with normalization results
        if errors:
            # Partial failure - some normalizations failed
            update_data["normalization_status"] = (
                NormalizationStatus.FAILED.value
            )
            update_data["normalization_error"] = "; ".join(errors)
            logger.warning(
                "Normalization completed with errors for %s: %s",
                appointment_id,
                errors,
            )
        elif update_data:
            # Success - at least one field normalized
            update_data["normalization_status"] = (
                NormalizationStatus.COMPLETED.value
            )
            update_data["normalization_error"] = None
            logger.info(
                "Normalization completed successfully for %s", appointment_id
            )
        else:
            # Nothing to normalize or normalization disabled
            update_data["normalization_status"] = (
                NormalizationStatus.SKIPPED.value
            )
            update_data["normalization_error"] = None
            logger.info("Normalization skipped for %s", appointment_id)

        await appointment_repo.update(appointment_id, update_data)

        # Sync client if CPF was extracted during normalization
        if update_data.get("cpf") and update_data.get("normalization_status") == NormalizationStatus.COMPLETED.value:
            try:
                from src.application.services.client_service import ClientService
                from src.infrastructure.repositories.client_repository import ClientRepository

                # Get updated appointment with new CPF
                updated_appointment = await appointment_repo.find_by_id(appointment_id)
                if updated_appointment:
                    client_repo = ClientRepository(container._database)
                    client_service = ClientService(client_repo, appointment_repo)
                    client_id = await client_service.upsert_from_appointment(updated_appointment)

                    if client_id:
                        logger.info(
                            "Client synced for appointment %s: %s",
                            appointment_id,
                            client_id,
                        )
            except Exception as client_exc:
                logger.warning(
                    "Failed to sync client after normalization for %s: %s",
                    appointment_id,
                    client_exc,
                )

        return {
            "success": True,
            "appointment_id": appointment_id,
            "fields_normalized": list(update_data.keys()),
            "errors": errors if errors else None,
        }

    except Exception as exc:
        logger.error(
            "Unexpected error normalizing appointment %s: %s",
            appointment_id,
            exc,
            exc_info=True,
        )

        # Mark as failed
        try:
            container = Container()
            appointment_repo = container.appointment_repository
            await appointment_repo.update(
                appointment_id,
                {
                    "normalization_status": NormalizationStatus.FAILED.value,
                    "normalization_error": str(exc),
                },
            )
        except Exception as update_exc:
            logger.error(
                "Failed to update normalization status: %s", update_exc
            )

        # Retry if this is a temporary error
        if "timeout" in str(exc).lower() or "connection" in str(exc).lower():
            logger.info("Retrying normalization for %s", appointment_id)
            raise Retry(defer=60)  # Retry after 60 seconds

        return {
            "success": False,
            "appointment_id": appointment_id,
            "error": str(exc),
        }
