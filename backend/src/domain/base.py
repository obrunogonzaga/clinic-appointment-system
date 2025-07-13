"""
Base classes for domain entities and value objects.
"""

from abc import ABC
from datetime import datetime
from typing import Any, Dict, Optional
from uuid import UUID, uuid4

from pydantic import BaseModel, Field


class ValueObject(BaseModel, ABC):
    """
    Base class for value objects.

    Value objects are immutable and defined by their attributes.
    Two value objects with the same attributes are considered equal.
    """

    class Config:
        frozen = True  # Make immutable
        use_enum_values = True
        json_encoders = {
            datetime: lambda v: v.isoformat(),
            UUID: lambda v: str(v),
        }


class Entity(BaseModel, ABC):
    """
    Base class for domain entities.

    Entities have a unique identity that persists through their lifecycle.
    Two entities with different IDs are different, even if all other attributes are the same.
    """

    id: UUID = Field(default_factory=uuid4, description="Unique identifier")
    created_at: datetime = Field(
        default_factory=datetime.utcnow,
        description="Creation timestamp",
    )
    updated_at: Optional[datetime] = Field(
        default=None,
        description="Last update timestamp",
    )

    class Config:
        use_enum_values = True
        json_encoders = {
            datetime: lambda v: v.isoformat(),
            UUID: lambda v: str(v),
        }
        validate_assignment = True
        arbitrary_types_allowed = True

    def __eq__(self, other: object) -> bool:
        """
        Entities are equal if they have the same ID.

        Args:
            other: Another object to compare with

        Returns:
            bool: True if both have the same ID
        """
        if not isinstance(other, Entity):
            return False
        return self.id == other.id

    def __hash__(self) -> int:
        """
        Hash based on ID for use in sets and dictionaries.

        Returns:
            int: Hash of the entity ID
        """
        return hash(self.id)

    def mark_as_updated(self) -> None:
        """Update the updated_at timestamp to current time."""
        self.updated_at = datetime.utcnow()

    def to_dict(self) -> Dict[str, Any]:
        """
        Convert entity to dictionary representation.

        Returns:
            Dict[str, Any]: Dictionary representation of the entity
        """
        return self.model_dump(mode="json")

    def to_json(self) -> str:
        """
        Convert entity to JSON string.

        Returns:
            str: JSON representation of the entity
        """
        return self.model_dump_json()


class AggregateRoot(Entity):
    """
    Base class for aggregate roots.

    Aggregate roots are entities that serve as the entry point to an aggregate.
    They ensure consistency of changes being made within the aggregate boundary.
    """

    _domain_events: list[object] = []

    def add_domain_event(self, event: object) -> None:
        """
        Add a domain event to be dispatched.

        Args:
            event: Domain event to add
        """
        self._domain_events.append(event)

    def get_domain_events(self) -> list[object]:
        """
        Get all pending domain events.

        Returns:
            list[object]: List of domain events
        """
        return self._domain_events.copy()

    def clear_domain_events(self) -> None:
        """Clear all pending domain events."""
        self._domain_events.clear()


class DomainException(Exception):
    """
    Base exception for domain-specific errors.
    """

    def __init__(self, message: str, code: Optional[str] = None) -> None:
        """
        Initialize domain exception.

        Args:
            message: Error message
            code: Optional error code for categorization
        """
        super().__init__(message)
        self.code = code


class EntityNotFoundException(DomainException):
    """Exception raised when an entity is not found."""

    def __init__(self, entity_type: str, entity_id: Any) -> None:
        """
        Initialize entity not found exception.

        Args:
            entity_type: Type of entity that was not found
            entity_id: ID of the entity that was not found
        """
        super().__init__(
            f"{entity_type} with ID {entity_id} not found",
            code="ENTITY_NOT_FOUND",
        )
        self.entity_type = entity_type
        self.entity_id = entity_id


class DomainValidationException(DomainException):
    """Exception raised when domain validation fails."""

    def __init__(self, message: str, field: Optional[str] = None) -> None:
        """
        Initialize domain validation exception.

        Args:
            message: Validation error message
            field: Optional field name that failed validation
        """
        super().__init__(message, code="VALIDATION_ERROR")
        self.field = field
