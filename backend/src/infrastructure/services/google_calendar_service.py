"""
Google Calendar service for syncing appointments with driver calendars.
"""

import logging
from datetime import datetime, timedelta
from pathlib import Path
from typing import Optional

from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

from src.infrastructure.config import Settings

logger = logging.getLogger(__name__)

SCOPES = ["https://www.googleapis.com/auth/calendar"]


class GoogleCalendarService:
    """
    Service for managing Google Calendar events for driver appointments.

    Uses a Service Account for authentication, allowing the system to
    create/update/delete events on driver calendars.
    """

    def __init__(self, settings: Settings):
        """
        Initialize Google Calendar service.

        Args:
            settings: Application settings
        """
        self.settings = settings
        self.enabled = settings.google_calendar_enabled
        self.default_calendar_id = settings.google_calendar_default_id
        self._service = None

        if self.enabled:
            self._initialize_service()

    def _initialize_service(self):
        """Initialize the Google Calendar API service."""
        credentials_path = self.settings.google_calendar_credentials_path

        if not credentials_path:
            logger.warning("Google Calendar credentials path not configured")
            self.enabled = False
            return

        creds_file = Path(credentials_path)
        if not creds_file.exists():
            logger.warning(
                f"Google Calendar credentials not found: {credentials_path}"
            )
            self.enabled = False
            return

        try:
            credentials = (
                service_account.Credentials.from_service_account_file(
                    str(creds_file), scopes=SCOPES
                )
            )
            self._service = build("calendar", "v3", credentials=credentials)
            logger.info("Google Calendar service initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize Google Calendar service: {e}")
            self.enabled = False

    def _get_calendar_id(
        self, driver_calendar_id: Optional[str]
    ) -> Optional[str]:
        """Get the calendar ID to use for a driver."""
        return driver_calendar_id or self.default_calendar_id

    async def create_event(
        self,
        driver_calendar_id: Optional[str],
        appointment_id: str,
        patient_name: str,
        appointment_date: datetime,
        appointment_time: str,
        address: Optional[str] = None,
        phone: Optional[str] = None,
        notes: Optional[str] = None,
    ) -> Optional[str]:
        """
        Create a calendar event for an appointment.

        Args:
            driver_calendar_id: Google Calendar ID of the driver
            appointment_id: System appointment ID (stored in event for reference)
            patient_name: Patient name
            appointment_date: Date of appointment
            appointment_time: Time in HH:MM format
            address: Collection address
            phone: Patient phone
            notes: Additional notes

        Returns:
            Google Calendar event ID if created, None otherwise
        """
        if not self.enabled or not self._service:
            logger.debug(
                "Google Calendar not enabled, skipping event creation"
            )
            return None

        calendar_id = self._get_calendar_id(driver_calendar_id)
        if not calendar_id:
            logger.warning("No calendar ID available for event creation")
            return None

        try:
            hours, minutes = map(int, appointment_time.split(":"))
            start_datetime = appointment_date.replace(
                hour=hours, minute=minutes, second=0, microsecond=0
            )
            end_datetime = start_datetime + timedelta(hours=1)

            description_parts = [f"Paciente: {patient_name}"]
            if phone:
                description_parts.append(f"Telefone: {phone}")
            if notes:
                description_parts.append(f"Observações: {notes}")
            description_parts.append(f"\nID Sistema: {appointment_id}")

            event = {
                "summary": f"Coleta - {patient_name}",
                "location": address or "",
                "description": "\n".join(description_parts),
                "start": {
                    "dateTime": start_datetime.isoformat(),
                    "timeZone": "America/Sao_Paulo",
                },
                "end": {
                    "dateTime": end_datetime.isoformat(),
                    "timeZone": "America/Sao_Paulo",
                },
                "extendedProperties": {
                    "private": {
                        "appointment_id": appointment_id,
                    }
                },
            }

            created_event = (
                self._service.events()
                .insert(calendarId=calendar_id, body=event)
                .execute()
            )

            event_id = created_event.get("id")
            logger.info(
                f"Created calendar event {event_id} for appointment {appointment_id}"
            )
            return event_id

        except HttpError as e:
            logger.error(f"Failed to create calendar event: {e}")
            return None
        except Exception as e:
            logger.error(f"Unexpected error creating calendar event: {e}")
            return None

    async def update_event(
        self,
        event_id: str,
        driver_calendar_id: Optional[str],
        patient_name: str,
        appointment_date: datetime,
        appointment_time: str,
        address: Optional[str] = None,
        phone: Optional[str] = None,
        notes: Optional[str] = None,
        appointment_id: Optional[str] = None,
    ) -> bool:
        """
        Update an existing calendar event.

        Args:
            event_id: Google Calendar event ID
            driver_calendar_id: Google Calendar ID of the driver
            patient_name: Patient name
            appointment_date: Date of appointment
            appointment_time: Time in HH:MM format
            address: Collection address
            phone: Patient phone
            notes: Additional notes
            appointment_id: System appointment ID

        Returns:
            True if updated successfully, False otherwise
        """
        if not self.enabled or not self._service:
            return False

        calendar_id = self._get_calendar_id(driver_calendar_id)
        if not calendar_id or not event_id:
            return False

        try:
            hours, minutes = map(int, appointment_time.split(":"))
            start_datetime = appointment_date.replace(
                hour=hours, minute=minutes, second=0, microsecond=0
            )
            end_datetime = start_datetime + timedelta(hours=1)

            description_parts = [f"Paciente: {patient_name}"]
            if phone:
                description_parts.append(f"Telefone: {phone}")
            if notes:
                description_parts.append(f"Observações: {notes}")
            if appointment_id:
                description_parts.append(f"\nID Sistema: {appointment_id}")

            event = {
                "summary": f"Coleta - {patient_name}",
                "location": address or "",
                "description": "\n".join(description_parts),
                "start": {
                    "dateTime": start_datetime.isoformat(),
                    "timeZone": "America/Sao_Paulo",
                },
                "end": {
                    "dateTime": end_datetime.isoformat(),
                    "timeZone": "America/Sao_Paulo",
                },
            }

            self._service.events().update(
                calendarId=calendar_id, eventId=event_id, body=event
            ).execute()

            logger.info(f"Updated calendar event {event_id}")
            return True

        except HttpError as e:
            logger.error(f"Failed to update calendar event: {e}")
            return False
        except Exception as e:
            logger.error(f"Unexpected error updating calendar event: {e}")
            return False

    async def delete_event(
        self, event_id: str, driver_calendar_id: Optional[str]
    ) -> bool:
        """
        Delete a calendar event.

        Args:
            event_id: Google Calendar event ID
            driver_calendar_id: Google Calendar ID of the driver

        Returns:
            True if deleted successfully, False otherwise
        """
        if not self.enabled or not self._service:
            return False

        calendar_id = self._get_calendar_id(driver_calendar_id)
        if not calendar_id or not event_id:
            return False

        try:
            self._service.events().delete(
                calendarId=calendar_id, eventId=event_id
            ).execute()

            logger.info(f"Deleted calendar event {event_id}")
            return True

        except HttpError as e:
            if e.resp.status == 404:
                logger.warning(
                    f"Calendar event {event_id} not found (already deleted)"
                )
                return True
            logger.error(f"Failed to delete calendar event: {e}")
            return False
        except Exception as e:
            logger.error(f"Unexpected error deleting calendar event: {e}")
            return False

    async def move_event(
        self,
        event_id: str,
        old_calendar_id: Optional[str],
        new_calendar_id: Optional[str],
    ) -> Optional[str]:
        """
        Move an event from one calendar to another (when driver changes).

        Args:
            event_id: Google Calendar event ID
            old_calendar_id: Current calendar ID
            new_calendar_id: New calendar ID

        Returns:
            New event ID if moved successfully, None otherwise
        """
        if not self.enabled or not self._service:
            return None

        source_calendar = self._get_calendar_id(old_calendar_id)
        dest_calendar = self._get_calendar_id(new_calendar_id)

        if not source_calendar or not dest_calendar or not event_id:
            return None

        if source_calendar == dest_calendar:
            return event_id

        try:
            moved_event = (
                self._service.events()
                .move(
                    calendarId=source_calendar,
                    eventId=event_id,
                    destination=dest_calendar,
                )
                .execute()
            )

            new_event_id = moved_event.get("id")
            logger.info(
                f"Moved calendar event from {source_calendar} to {dest_calendar}"
            )
            return new_event_id

        except HttpError as e:
            logger.error(f"Failed to move calendar event: {e}")
            return None
        except Exception as e:
            logger.error(f"Unexpected error moving calendar event: {e}")
            return None
