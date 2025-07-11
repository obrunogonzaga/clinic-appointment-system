# Code Patterns & Development Guidelines

This document provides comprehensive coding patterns, conventions, and best practices for the Clinic Appointment Scheduling System. It serves as a reference for maintaining code quality, consistency, and architectural integrity across the entire codebase.

## Python Backend Patterns

### Code Style & Standards

#### PEP 8 Compliance
```python
# Good: Clear naming and proper spacing
class AppointmentService:
    def __init__(self, repository: AppointmentRepository) -> None:
        self._repository = repository
    
    async def create_appointment(
        self, 
        patient_id: str, 
        datetime: datetime,
        duration_minutes: int = 30
    ) -> Appointment:
        """Create a new appointment with conflict checking."""
        if await self._has_conflict(datetime, duration_minutes):
            raise AppointmentConflictError("Time slot unavailable")
        
        appointment = Appointment(
            patient_id=patient_id,
            scheduled_at=datetime,
            duration=timedelta(minutes=duration_minutes)
        )
        return await self._repository.save(appointment)
```

#### Type Hints & Annotations
```python
from typing import Optional, List, Dict, Any, Protocol
from datetime import datetime, timedelta

# Use Protocol for dependency injection
class AppointmentRepository(Protocol):
    async def save(self, appointment: Appointment) -> Appointment: ...
    async def find_by_id(self, id: str) -> Optional[Appointment]: ...
    async def find_conflicts(
        self, 
        start: datetime, 
        end: datetime
    ) -> List[Appointment]: ...

# Generic types for reusable patterns
T = TypeVar('T')

class Repository(Generic[T]):
    async def save(self, entity: T) -> T: ...
    async def find_by_id(self, id: str) -> Optional[T]: ...
```

### Clean Architecture Implementation

#### Domain Layer Patterns
```python
# Domain Entity
@dataclass(frozen=True)
class Patient:
    id: PatientId
    name: str
    email: Email
    phone: PhoneNumber
    created_at: datetime
    
    def update_contact_info(self, email: Email, phone: PhoneNumber) -> 'Patient':
        """Return new instance with updated contact info."""
        return replace(self, email=email, phone=phone)
    
    def can_schedule_appointment(self, appointment_time: datetime) -> bool:
        """Business rule: patients can't schedule same-day appointments."""
        return appointment_time.date() > datetime.now().date()

# Value Objects
@dataclass(frozen=True)
class Email:
    value: str
    
    def __post_init__(self):
        if not self._is_valid_email(self.value):
            raise ValueError(f"Invalid email: {self.value}")
    
    @staticmethod
    def _is_valid_email(email: str) -> bool:
        return "@" in email and "." in email.split("@")[1]

# Domain Service
class AppointmentSchedulingService:
    def __init__(self, conflict_checker: ConflictChecker) -> None:
        self._conflict_checker = conflict_checker
    
    def schedule_appointment(
        self, 
        patient: Patient, 
        requested_time: datetime,
        duration: timedelta
    ) -> Result[Appointment, SchedulingError]:
        """Core business logic for appointment scheduling."""
        if not patient.can_schedule_appointment(requested_time):
            return Err(SchedulingError.SAME_DAY_NOT_ALLOWED)
        
        if self._conflict_checker.has_conflict(requested_time, duration):
            return Err(SchedulingError.TIME_CONFLICT)
        
        appointment = Appointment.create(
            patient_id=patient.id,
            scheduled_at=requested_time,
            duration=duration
        )
        return Ok(appointment)
```

#### Application Layer Patterns
```python
# Use Case Implementation
class CreateAppointmentUseCase:
    def __init__(
        self,
        patient_repo: PatientRepository,
        appointment_repo: AppointmentRepository,
        scheduling_service: AppointmentSchedulingService,
        event_publisher: EventPublisher
    ) -> None:
        self._patient_repo = patient_repo
        self._appointment_repo = appointment_repo
        self._scheduling_service = scheduling_service
        self._event_publisher = event_publisher
    
    async def execute(self, command: CreateAppointmentCommand) -> AppointmentDto:
        """Execute the create appointment use case."""
        # 1. Validate input
        patient = await self._patient_repo.find_by_id(command.patient_id)
        if not patient:
            raise PatientNotFoundError(command.patient_id)
        
        # 2. Apply business logic
        result = self._scheduling_service.schedule_appointment(
            patient=patient,
            requested_time=command.scheduled_at,
            duration=timedelta(minutes=command.duration_minutes)
        )
        
        if result.is_err():
            raise AppointmentSchedulingError(result.unwrap_err())
        
        # 3. Persist changes
        appointment = result.unwrap()
        saved_appointment = await self._appointment_repo.save(appointment)
        
        # 4. Publish events
        await self._event_publisher.publish(
            AppointmentCreatedEvent(appointment_id=saved_appointment.id)
        )
        
        return AppointmentDto.from_entity(saved_appointment)

# Command/Query Objects
@dataclass(frozen=True)
class CreateAppointmentCommand:
    patient_id: str
    scheduled_at: datetime
    duration_minutes: int
    notes: Optional[str] = None

@dataclass(frozen=True)
class AppointmentDto:
    id: str
    patient_id: str
    scheduled_at: datetime
    duration_minutes: int
    status: str
    
    @classmethod
    def from_entity(cls, appointment: Appointment) -> 'AppointmentDto':
        return cls(
            id=str(appointment.id),
            patient_id=str(appointment.patient_id),
            scheduled_at=appointment.scheduled_at,
            duration_minutes=int(appointment.duration.total_seconds() / 60),
            status=appointment.status.value
        )
```

#### Infrastructure Layer Patterns
```python
# Repository Implementation
class MongoAppointmentRepository:
    def __init__(self, database: AsyncIOMotorDatabase) -> None:
        self._collection = database.appointments
    
    async def save(self, appointment: Appointment) -> Appointment:
        """Save appointment to MongoDB."""
        document = {
            "_id": str(appointment.id),
            "patient_id": str(appointment.patient_id),
            "scheduled_at": appointment.scheduled_at,
            "duration_seconds": int(appointment.duration.total_seconds()),
            "status": appointment.status.value,
            "created_at": appointment.created_at,
            "updated_at": datetime.utcnow()
        }
        
        await self._collection.replace_one(
            {"_id": document["_id"]},
            document,
            upsert=True
        )
        
        return appointment
    
    async def find_by_id(self, appointment_id: str) -> Optional[Appointment]:
        """Find appointment by ID."""
        document = await self._collection.find_one({"_id": appointment_id})
        if not document:
            return None
        
        return self._document_to_entity(document)
    
    def _document_to_entity(self, document: Dict[str, Any]) -> Appointment:
        """Convert MongoDB document to domain entity."""
        return Appointment(
            id=AppointmentId(document["_id"]),
            patient_id=PatientId(document["patient_id"]),
            scheduled_at=document["scheduled_at"],
            duration=timedelta(seconds=document["duration_seconds"]),
            status=AppointmentStatus(document["status"]),
            created_at=document["created_at"]
        )

# FastAPI Controller
class AppointmentController:
    def __init__(self, create_appointment_use_case: CreateAppointmentUseCase) -> None:
        self._create_appointment_use_case = create_appointment_use_case
    
    @router.post("/appointments", response_model=AppointmentResponse)
    async def create_appointment(
        self,
        request: CreateAppointmentRequest,
        current_user: User = Depends(get_current_user)
    ) -> AppointmentResponse:
        """Create a new appointment."""
        try:
            command = CreateAppointmentCommand(
                patient_id=request.patient_id,
                scheduled_at=request.scheduled_at,
                duration_minutes=request.duration_minutes,
                notes=request.notes
            )
            
            appointment_dto = await self._create_appointment_use_case.execute(command)
            
            return AppointmentResponse(
                success=True,
                data=appointment_dto,
                message="Appointment created successfully"
            )
        
        except AppointmentSchedulingError as e:
            raise HTTPException(
                status_code=400,
                detail=f"Scheduling error: {e.message}"
            )
        except Exception as e:
            logger.exception("Unexpected error creating appointment")
            raise HTTPException(
                status_code=500,
                detail="Internal server error"
            )
```

### Error Handling Patterns
```python
# Custom Exception Hierarchy
class DomainError(Exception):
    """Base class for domain-specific errors."""
    pass

class AppointmentError(DomainError):
    """Base class for appointment-related errors."""
    pass

class AppointmentConflictError(AppointmentError):
    """Raised when appointment conflicts with existing booking."""
    def __init__(self, conflicting_appointment_id: str) -> None:
        self.conflicting_appointment_id = conflicting_appointment_id
        super().__init__(f"Appointment conflicts with {conflicting_appointment_id}")

# Result Pattern for Error Handling
from typing import Union, Generic, TypeVar

T = TypeVar('T')
E = TypeVar('E')

class Result(Generic[T, E]):
    def __init__(self, value: Union[T, E], is_success: bool) -> None:
        self._value = value
        self._is_success = is_success
    
    def is_ok(self) -> bool:
        return self._is_success
    
    def is_err(self) -> bool:
        return not self._is_success
    
    def unwrap(self) -> T:
        if not self._is_success:
            raise ValueError("Called unwrap on error result")
        return self._value
    
    def unwrap_err(self) -> E:
        if self._is_success:
            raise ValueError("Called unwrap_err on success result")
        return self._value

def Ok(value: T) -> Result[T, E]:
    return Result(value, True)

def Err(error: E) -> Result[T, E]:
    return Result(error, False)
```

### Testing Patterns
```python
# Unit Test Example
class TestAppointmentSchedulingService:
    def setup_method(self):
        self.mock_conflict_checker = Mock(spec=ConflictChecker)
        self.service = AppointmentSchedulingService(self.mock_conflict_checker)
    
    def test_schedule_appointment_success(self):
        # Arrange
        patient = Patient(
            id=PatientId("patient-123"),
            name="John Doe",
            email=Email("john@example.com"),
            phone=PhoneNumber("+1234567890"),
            created_at=datetime.now()
        )
        requested_time = datetime.now() + timedelta(days=1)
        duration = timedelta(minutes=30)
        
        self.mock_conflict_checker.has_conflict.return_value = False
        
        # Act
        result = self.service.schedule_appointment(patient, requested_time, duration)
        
        # Assert
        assert result.is_ok()
        appointment = result.unwrap()
        assert appointment.patient_id == patient.id
        assert appointment.scheduled_at == requested_time
        assert appointment.duration == duration
    
    def test_schedule_appointment_same_day_error(self):
        # Arrange
        patient = Patient(...)
        requested_time = datetime.now()  # Same day
        duration = timedelta(minutes=30)
        
        # Act
        result = self.service.schedule_appointment(patient, requested_time, duration)
        
        # Assert
        assert result.is_err()
        assert result.unwrap_err() == SchedulingError.SAME_DAY_NOT_ALLOWED

# Integration Test Example
@pytest.mark.asyncio
class TestCreateAppointmentUseCase:
    async def test_create_appointment_integration(self, test_db):
        # Arrange
        patient_repo = MongoPatientRepository(test_db)
        appointment_repo = MongoAppointmentRepository(test_db)
        event_publisher = InMemoryEventPublisher()
        
        use_case = CreateAppointmentUseCase(
            patient_repo, appointment_repo, 
            AppointmentSchedulingService(...), event_publisher
        )
        
        patient = await patient_repo.save(Patient(...))
        command = CreateAppointmentCommand(
            patient_id=str(patient.id),
            scheduled_at=datetime.now() + timedelta(days=1),
            duration_minutes=30
        )
        
        # Act
        result = await use_case.execute(command)
        
        # Assert
        assert result.patient_id == str(patient.id)
        
        # Verify persistence
        saved_appointment = await appointment_repo.find_by_id(result.id)
        assert saved_appointment is not None
        
        # Verify events
        events = event_publisher.get_published_events()
        assert len(events) == 1
        assert isinstance(events[0], AppointmentCreatedEvent)
```

## React Frontend Patterns

### Component Architecture

#### Functional Components with TypeScript
```typescript
// Component Props Interface
interface AppointmentCardProps {
  appointment: Appointment;
  onEdit?: (appointment: Appointment) => void;
  onCancel?: (appointmentId: string) => void;
  className?: string;
}

// Functional Component with Proper Typing
const AppointmentCard: React.FC<AppointmentCardProps> = ({
  appointment,
  onEdit,
  onCancel,
  className = ''
}) => {
  const [isLoading, setIsLoading] = useState(false);
  const [showDetails, setShowDetails] = useState(false);
  
  const handleCancel = useCallback(async () => {
    if (!onCancel) return;
    
    setIsLoading(true);
    try {
      await onCancel(appointment.id);
    } catch (error) {
      console.error('Failed to cancel appointment:', error);
    } finally {
      setIsLoading(false);
    }
  }, [appointment.id, onCancel]);
  
  return (
    <div className={`bg-white rounded-lg shadow-md p-4 ${className}`}>
      <div className="flex justify-between items-start">
        <div>
          <h3 className="text-lg font-semibold text-gray-900">
            {appointment.patient.name}
          </h3>
          <p className="text-sm text-gray-600">
            {format(appointment.scheduledAt, 'PPp')}
          </p>
        </div>
        
        <div className="flex space-x-2">
          {onEdit && (
            <Button
              variant="outline"
              size="sm"
              onClick={() => onEdit(appointment)}
            >
              Edit
            </Button>
          )}
          {onCancel && (
            <Button
              variant="destructive"
              size="sm"
              onClick={handleCancel}
              disabled={isLoading}
            >
              {isLoading ? 'Canceling...' : 'Cancel'}
            </Button>
          )}
        </div>
      </div>
      
      {showDetails && (
        <div className="mt-4 pt-4 border-t border-gray-200">
          <p className="text-sm text-gray-700">{appointment.notes}</p>
        </div>
      )}
    </div>
  );
};

## Database & Data Access Patterns

### MongoDB Integration Patterns
```python
# Database Connection Management
class DatabaseManager:
    def __init__(self, connection_string: str) -> None:
        self._client: Optional[AsyncIOMotorClient] = None
        self._database: Optional[AsyncIOMotorDatabase] = None
        self._connection_string = connection_string
    
    async def connect(self) -> None:
        """Establish database connection."""
        self._client = AsyncIOMotorClient(self._connection_string)
        self._database = self._client.clinic_db
        
        # Test connection
        await self._client.admin.command('ping')
        logger.info("Connected to MongoDB")
    
    async def disconnect(self) -> None:
        """Close database connection."""
        if self._client:
            self._client.close()
            logger.info("Disconnected from MongoDB")
    
    @property
    def database(self) -> AsyncIOMotorDatabase:
        if not self._database:
            raise RuntimeError("Database not connected")
        return self._database

# Index Management
class IndexManager:
    def __init__(self, database: AsyncIOMotorDatabase) -> None:
        self._database = database
    
    async def create_indexes(self) -> None:
        """Create all required indexes."""
        # Appointment indexes
        appointments = self._database.appointments
        await appointments.create_index("patient_id")
        await appointments.create_index("scheduled_at")
        await appointments.create_index([("scheduled_at", 1), ("status", 1)])
        
        # Patient indexes
        patients = self._database.patients
        await patients.create_index("email", unique=True)
        await patients.create_index("phone")
        
        # Compound index for conflict checking
        await appointments.create_index([
            ("scheduled_at", 1),
            ("duration_seconds", 1),
            ("status", 1)
        ])
        
        logger.info("Database indexes created")

# Query Builder Pattern
class AppointmentQueryBuilder:
    def __init__(self) -> None:
        self._filters: Dict[str, Any] = {}
        self._sort: List[Tuple[str, int]] = []
        self._limit: Optional[int] = None
        self._skip: Optional[int] = None
    
    def by_patient(self, patient_id: str) -> 'AppointmentQueryBuilder':
        self._filters["patient_id"] = patient_id
        return self
    
    def by_date_range(self, start: datetime, end: datetime) -> 'AppointmentQueryBuilder':
        self._filters["scheduled_at"] = {
            "$gte": start,
            "$lte": end
        }
        return self
    
    def by_status(self, status: AppointmentStatus) -> 'AppointmentQueryBuilder':
        self._filters["status"] = status.value
        return self
    
    def sort_by_date(self, ascending: bool = True) -> 'AppointmentQueryBuilder':
        direction = 1 if ascending else -1
        self._sort.append(("scheduled_at", direction))
        return self
    
    def limit(self, count: int) -> 'AppointmentQueryBuilder':
        self._limit = count
        return self
    
    def skip(self, count: int) -> 'AppointmentQueryBuilder':
        self._skip = count
        return self
    
    def build(self) -> Dict[str, Any]:
        """Build the final query."""
        query = {"filter": self._filters}
        
        if self._sort:
            query["sort"] = self._sort
        if self._limit:
            query["limit"] = self._limit
        if self._skip:
            query["skip"] = self._skip
        
        return query

# Usage Example
class MongoAppointmentRepository:
    async def find_upcoming_appointments(
        self, 
        patient_id: str, 
        days_ahead: int = 30
    ) -> List[Appointment]:
        """Find upcoming appointments for a patient."""
        start_date = datetime.now()
        end_date = start_date + timedelta(days=days_ahead)
        
        query = (AppointmentQueryBuilder()
                .by_patient(patient_id)
                .by_date_range(start_date, end_date)
                .by_status(AppointmentStatus.SCHEDULED)
                .sort_by_date(ascending=True)
                .build())
        
        cursor = self._collection.find(
            query["filter"],
            sort=query.get("sort"),
            limit=query.get("limit"),
            skip=query.get("skip")
        )
        
        documents = await cursor.to_list(length=None)
        return [self._document_to_entity(doc) for doc in documents]
```

### Data Migration Patterns
```python
# Migration Base Class
from abc import ABC, abstractmethod

class Migration(ABC):
    @property
    @abstractmethod
    def version(self) -> str:
        """Migration version identifier."""
        pass
    
    @property
    @abstractmethod
    def description(self) -> str:
        """Migration description."""
        pass
    
    @abstractmethod
    async def up(self, database: AsyncIOMotorDatabase) -> None:
        """Apply the migration."""
        pass
    
    @abstractmethod
    async def down(self, database: AsyncIOMotorDatabase) -> None:
        """Rollback the migration."""
        pass

# Example Migration
class AddPatientPhoneIndexMigration(Migration):
    @property
    def version(self) -> str:
        return "001_add_patient_phone_index"
    
    @property
    def description(self) -> str:
        return "Add index on patient phone field for faster lookups"
    
    async def up(self, database: AsyncIOMotorDatabase) -> None:
        await database.patients.create_index("phone")
        logger.info(f"Applied migration: {self.description}")
    
    async def down(self, database: AsyncIOMotorDatabase) -> None:
        await database.patients.drop_index("phone_1")
        logger.info(f"Rolled back migration: {self.description}")

# Migration Runner
class MigrationRunner:
    def __init__(self, database: AsyncIOMotorDatabase) -> None:
        self._database = database
        self._migrations: List[Migration] = []
    
    def add_migration(self, migration: Migration) -> None:
        self._migrations.append(migration)
    
    async def run_migrations(self) -> None:
        """Run all pending migrations."""
        # Ensure migrations collection exists
        migrations_collection = self._database.migrations
        
        for migration in sorted(self._migrations, key=lambda m: m.version):
            # Check if migration already applied
            existing = await migrations_collection.find_one({
                "version": migration.version
            })
            
            if existing:
                logger.info(f"Migration {migration.version} already applied")
                continue
            
            try:
                await migration.up(self._database)
                
                # Record migration as applied
                await migrations_collection.insert_one({
                    "version": migration.version,
                    "description": migration.description,
                    "applied_at": datetime.utcnow()
                })
                
                logger.info(f"Successfully applied migration: {migration.version}")
            
            except Exception as e:
                logger.error(f"Failed to apply migration {migration.version}: {e}")
                raise
```

## Security Patterns

### Authentication & Authorization
```python
# JWT Token Management
from jose import JWTError, jwt
from passlib.context import CryptContext
from datetime import datetime, timedelta

class AuthenticationService:
    def __init__(self, secret_key: str, algorithm: str = "HS256") -> None:
        self._secret_key = secret_key
        self._algorithm = algorithm
        self._pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
    
    def hash_password(self, password: str) -> str:
        """Hash a password using bcrypt."""
        return self._pwd_context.hash(password)
    
    def verify_password(self, plain_password: str, hashed_password: str) -> bool:
        """Verify a password against its hash."""
        return self._pwd_context.verify(plain_password, hashed_password)
    
    def create_access_token(
        self, 
        data: Dict[str, Any], 
        expires_delta: Optional[timedelta] = None
    ) -> str:
        """Create a JWT access token."""
        to_encode = data.copy()
        
        if expires_delta:
            expire = datetime.utcnow() + expires_delta
        else:
            expire = datetime.utcnow() + timedelta(minutes=15)
        
        to_encode.update({"exp": expire})
        encoded_jwt = jwt.encode(to_encode, self._secret_key, algorithm=self._algorithm)
        return encoded_jwt
    
    def verify_token(self, token: str) -> Optional[Dict[str, Any]]:
        """Verify and decode a JWT token."""
        try:
            payload = jwt.decode(token, self._secret_key, algorithms=[self._algorithm])
            return payload
        except JWTError:
            return None

# Role-Based Access Control
from enum import Enum
from functools import wraps

class Role(Enum):
    ADMIN = "admin"
    DOCTOR = "doctor"
    NURSE = "nurse"
    RECEPTIONIST = "receptionist"

class Permission(Enum):
    READ_APPOINTMENTS = "read:appointments"
    WRITE_APPOINTMENTS = "write:appointments"
    DELETE_APPOINTMENTS = "delete:appointments"
    READ_PATIENTS = "read:patients"
    WRITE_PATIENTS = "write:patients"
    ADMIN_USERS = "admin:users"

# Role-Permission Mapping
ROLE_PERMISSIONS = {
    Role.ADMIN: [
        Permission.READ_APPOINTMENTS,
        Permission.WRITE_APPOINTMENTS,
        Permission.DELETE_APPOINTMENTS,
        Permission.READ_PATIENTS,
        Permission.WRITE_PATIENTS,
        Permission.ADMIN_USERS,
    ],
    Role.DOCTOR: [
        Permission.READ_APPOINTMENTS,
        Permission.WRITE_APPOINTMENTS,
        Permission.READ_PATIENTS,
        Permission.WRITE_PATIENTS,
    ],
    Role.NURSE: [
        Permission.READ_APPOINTMENTS,
        Permission.WRITE_APPOINTMENTS,
        Permission.READ_PATIENTS,
    ],
    Role.RECEPTIONIST: [
        Permission.READ_APPOINTMENTS,
        Permission.WRITE_APPOINTMENTS,
        Permission.READ_PATIENTS,
    ],
}

# Authorization Decorator
def require_permission(permission: Permission):
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            # Get current user from context (FastAPI dependency)
            current_user = kwargs.get('current_user')
            if not current_user:
                raise HTTPException(status_code=401, detail="Not authenticated")
            
            user_permissions = ROLE_PERMISSIONS.get(current_user.role, [])
            if permission not in user_permissions:
                raise HTTPException(
                    status_code=403, 
                    detail="Insufficient permissions"
                )
            
            return await func(*args, **kwargs)
        return wrapper
    return decorator

# Usage in FastAPI endpoints
@router.delete("/appointments/{appointment_id}")
@require_permission(Permission.DELETE_APPOINTMENTS)
async def delete_appointment(
    appointment_id: str,
    current_user: User = Depends(get_current_user)
) -> Dict[str, str]:
    # Implementation here
    pass
```

### Input Validation & Sanitization
```python
# Custom Pydantic Validators
from pydantic import BaseModel, validator, Field
import re
from typing import Optional

class PatientCreateRequest(BaseModel):
    name: str = Field(..., min_length=2, max_length=100)
    email: str = Field(..., regex=r'^[\w\.-]+@[\w\.-]+\.\w+$')
    phone: str = Field(..., min_length=10, max_length=15)
    date_of_birth: Optional[date] = None
    
    @validator('name')
    def validate_name(cls, v):
        # Remove extra whitespace and validate format
        v = ' '.join(v.split())
        if not re.match(r'^[a-zA-Z\s\-\']+$', v):
            raise ValueError('Name can only contain letters, spaces, hyphens, and apostrophes')
        return v
    
    @validator('phone')
    def validate_phone(cls, v):
        # Remove all non-digit characters
        digits_only = re.sub(r'\D', '', v)
        if len(digits_only) < 10 or len(digits_only) > 15:
            raise ValueError('Phone number must be between 10 and 15 digits')
        return digits_only
    
    @validator('date_of_birth')
    def validate_date_of_birth(cls, v):
        if v and v > date.today():
            raise ValueError('Date of birth cannot be in the future')
        if v and v < date(1900, 1, 1):
            raise ValueError('Date of birth cannot be before 1900')
        return v

# Rate Limiting
from collections import defaultdict
from time import time

class RateLimiter:
    def __init__(self, max_requests: int, window_seconds: int) -> None:
        self._max_requests = max_requests
        self._window_seconds = window_seconds
        self._requests: Dict[str, List[float]] = defaultdict(list)
    
    def is_allowed(self, identifier: str) -> bool:
        """Check if request is allowed for the given identifier."""
        now = time()
        window_start = now - self._window_seconds
        
        # Clean old requests
        self._requests[identifier] = [
            req_time for req_time in self._requests[identifier]
            if req_time > window_start
        ]
        
        # Check if under limit
        if len(self._requests[identifier]) < self._max_requests:
            self._requests[identifier].append(now)
            return True
        
        return False

# FastAPI Rate Limiting Middleware
from fastapi import Request, HTTPException
from starlette.middleware.base import BaseHTTPMiddleware

class RateLimitMiddleware(BaseHTTPMiddleware):
    def __init__(self, app, rate_limiter: RateLimiter):
        super().__init__(app)
        self._rate_limiter = rate_limiter
    
    async def dispatch(self, request: Request, call_next):
        # Use IP address as identifier (could also use user ID)
        client_ip = request.client.host
        
        if not self._rate_limiter.is_allowed(client_ip):
            raise HTTPException(
                status_code=429,
                detail="Rate limit exceeded"
            )
        
        response = await call_next(request)
        return response
```

## Logging & Monitoring Patterns

### Structured Logging
```python
import structlog
from typing import Any, Dict
import json
from datetime import datetime

# Configure structured logging
structlog.configure(
    processors=[
        structlog.stdlib.filter_by_level,
        structlog.stdlib.add_logger_name,
        structlog.stdlib.add_log_level,
        structlog.stdlib.PositionalArgumentsFormatter(),
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.StackInfoRenderer(),
        structlog.processors.format_exc_info,
        structlog.processors.UnicodeDecoder(),
        structlog.processors.JSONRenderer()
    ],
    context_class=dict,
    logger_factory=structlog.stdlib.LoggerFactory(),
    wrapper_class=structlog.stdlib.BoundLogger,
    cache_logger_on_first_use=True,
)

# Application Logger
class AppLogger:
    def __init__(self, name: str) -> None:
        self._logger = structlog.get_logger(name)
    
    def log_appointment_created(
        self, 
        appointment_id: str, 
        patient_id: str, 
        user_id: str
    ) -> None:
        self._logger.info(
            "Appointment created",
            event="appointment_created",
            appointment_id=appointment_id,
            patient_id=patient_id,
            user_id=user_id,
            timestamp=datetime.utcnow().isoformat()
        )
    
    def log_authentication_attempt(
        self, 
        email: str, 
        success: bool, 
        ip_address: str
    ) -> None:
        self._logger.info(
            "Authentication attempt",
            event="auth_attempt",
            email=email,
            success=success,
            ip_address=ip_address,
            timestamp=datetime.utcnow().isoformat()
        )
    
    def log_error(
        self, 
        error: Exception, 
        context: Dict[str, Any] = None
    ) -> None:
        self._logger.error(
            "Application error",
            event="error",
            error_type=type(error).__name__,
            error_message=str(error),
            context=context or {},
            timestamp=datetime.utcnow().isoformat()
        )

# Request Logging Middleware
class RequestLoggingMiddleware(BaseHTTPMiddleware):
    def __init__(self, app):
        super().__init__(app)
        self._logger = AppLogger("request")
    
    async def dispatch(self, request: Request, call_next):
        start_time = time()
        
        # Log request
        self._logger._logger.info(
            "Request started",
            event="request_started",
            method=request.method,
            url=str(request.url),
            client_ip=request.client.host,
            user_agent=request.headers.get("user-agent"),
            timestamp=datetime.utcnow().isoformat()
        )
        
        try:
            response = await call_next(request)
            duration = time() - start_time
            
            # Log response
            self._logger._logger.info(
                "Request completed",
                event="request_completed",
                method=request.method,
                url=str(request.url),
                status_code=response.status_code,
                duration_ms=round(duration * 1000, 2),
                timestamp=datetime.utcnow().isoformat()
            )
            
            return response
        
        except Exception as e:
            duration = time() - start_time
            
            self._logger._logger.error(
                "Request failed",
                event="request_failed",
                method=request.method,
                url=str(request.url),
                error=str(e),
                duration_ms=round(duration * 1000, 2),
                timestamp=datetime.utcnow().isoformat()
            )
            raise
```

### Health Checks & Metrics
```python
# Health Check System
from abc import ABC, abstractmethod
from enum import Enum
from dataclasses import dataclass
from typing import List, Dict, Any

class HealthStatus(Enum):
    HEALTHY = "healthy"
    UNHEALTHY = "unhealthy"
    DEGRADED = "degraded"

@dataclass
class HealthCheckResult:
    name: str
    status: HealthStatus
    message: str
    details: Dict[str, Any] = None
    duration_ms: float = 0

class HealthCheck(ABC):
    @property
    @abstractmethod
    def name(self) -> str:
        pass
    
    @abstractmethod
    async def check(self) -> HealthCheckResult:
        pass

# Database Health Check
class DatabaseHealthCheck(HealthCheck):
    def __init__(self, database: AsyncIOMotorDatabase) -> None:
        self._database = database
    
    @property
    def name(self) -> str:
        return "database"
    
    async def check(self) -> HealthCheckResult:
        start_time = time()
        
        try:
            # Simple ping to check connectivity
            await self._database.command("ping")
            
            # Check if we can query a collection
            count = await self._database.appointments.count_documents({})
            
            duration = (time() - start_time) * 1000
            
            return HealthCheckResult(
                name=self.name,
                status=HealthStatus.HEALTHY,
                message="Database is accessible",
                details={"appointment_count": count},
                duration_ms=duration
            )
        
        except Exception as e:
            duration = (time() - start_time) * 1000
            
            return HealthCheckResult(
                name=self.name,
                status=HealthStatus.UNHEALTHY,
                message=f"Database check failed: {str(e)}",
                duration_ms=duration
            )

# Health Check Service
class HealthCheckService:
    def __init__(self) -> None:
        self._checks: List[HealthCheck] = []
    
    def add_check(self, check: HealthCheck) -> None:
        self._checks.append(check)
    
    async def run_all_checks(self) -> Dict[str, Any]:
        """Run all health checks and return aggregated results."""
        results = []
        overall_status = HealthStatus.HEALTHY
        
        for check in self._checks:
            try:
                result = await check.check()
                results.append(result)
                
                if result.status == HealthStatus.UNHEALTHY:
                    overall_status = HealthStatus.UNHEALTHY
                elif result.status == HealthStatus.DEGRADED and overall_status == HealthStatus.HEALTHY:
                    overall_status = HealthStatus.DEGRADED
            
            except Exception as e:
                results.append(HealthCheckResult(
                    name=check.name,
                    status=HealthStatus.UNHEALTHY,
                    message=f"Health check failed: {str(e)}"
                ))
                overall_status = HealthStatus.UNHEALTHY
        
        return {
            "status": overall_status.value,
            "timestamp": datetime.utcnow().isoformat(),
            "checks": {
                result.name: {
                    "status": result.status.value,
                    "message": result.message,
                    "details": result.details,
                    "duration_ms": result.duration_ms
                }
                for result in results
            }
        }

# FastAPI Health Check Endpoint
@router.get("/health")
async def health_check(health_service: HealthCheckService = Depends()) -> Dict[str, Any]:
    """Health check endpoint."""
    return await health_service.run_all_checks()
```

## Deployment & DevOps Patterns

### Docker Best Practices
```dockerfile
# Multi-stage Dockerfile for Python backend
FROM python:3.11-slim as builder

# Install system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Create virtual environment
RUN python -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

# Copy requirements and install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Production stage
FROM python:3.11-slim as production

# Create non-root user
RUN groupadd -r appuser && useradd -r -g appuser appuser

# Copy virtual environment from builder
COPY --from=builder /opt/venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

# Set working directory
WORKDIR /app

# Copy application code
COPY --chown=appuser:appuser . .

# Switch to non-root user
USER appuser

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

# Expose port
EXPOSE 8000

# Start application
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
```

### Environment Configuration
```python
# Environment-based configuration
from pydantic import BaseSettings, Field
from typing import Optional

class Settings(BaseSettings):
    # Application settings
    app_name: str = Field(default="Clinic Appointment System")
    debug: bool = Field(default=False)
    version: str = Field(default="1.0.0")
    
    # Database settings
    mongodb_url: str = Field(..., env="MONGODB_URL")
    database_name: str = Field(default="clinic_db")
    
    # Security settings
    secret_key: str = Field(..., env="SECRET_KEY")
    access_token_expire_minutes: int = Field(default=30)
    
    # External services
    email_service_url: Optional[str] = Field(default=None, env="EMAIL_SERVICE_URL")
    sms_service_url: Optional[str] = Field(default=None, env="SMS_SERVICE_URL")
    
    # Monitoring
    log_level: str = Field(default="INFO")
    enable_metrics: bool = Field(default=True)
    
    class Config:
        env_file = ".env"
        case_sensitive = False

# Configuration factory
def get_settings() -> Settings:
    return Settings()

# Usage in FastAPI
from functools import lru_cache

@lru_cache()
def get_cached_settings() -> Settings:
    return Settings()

# Dependency injection
async def get_database_manager(
    settings: Settings = Depends(get_cached_settings)
) -> DatabaseManager:
    manager = DatabaseManager(settings.mongodb_url)
    await manager.connect()
    return manager
```

### CI/CD Pipeline Configuration
```yaml
# .github/workflows/ci-cd.yml
name: CI/CD Pipeline

on:
  push:
    branches: [ main, develop ]
  pull_request:
    branches: [ main ]

jobs:
  test:
    runs-on: ubuntu-latest
    
    services:
      mongodb:
        image: mongo:6.0
        ports:
          - 27017:27017
        options: >-
          --health-cmd "mongosh --eval 'db.runCommand(\"ping\")'"
          --health-interval 10s
          --health-timeout 5s
          --health-retries 5
    
    steps:
    - uses: actions/checkout@v3
    
    - name: Set up Python
      uses: actions/setup-python@v4
      with:
        python-version: '3.11'
    
    - name: Cache dependencies
      uses: actions/cache@v3
      with:
        path: ~/.cache/pip
        key: ${{ runner.os }}-pip-${{ hashFiles('**/requirements.txt') }}
    
    - name: Install dependencies
      run: |
        python -m pip install --upgrade pip
        pip install -r requirements.txt
        pip install -r requirements-dev.txt
    
    - name: Run linting
      run: |
        flake8 .
        black --check .
        isort --check-only .
    
    - name: Run type checking
      run: mypy .
    
    - name: Run tests
      env:
        MONGODB_URL: mongodb://localhost:27017/test_db
        SECRET_KEY: test-secret-key
      run: |
        pytest --cov=. --cov-report=xml
    
    - name: Upload coverage to Codecov
      uses: codecov/codecov-action@v3
      with:
        file: ./coverage.xml
  
  build-and-deploy:
    needs: test
    runs-on: ubuntu-latest
    if: github.ref == 'refs/heads/main'
    
    steps:
    - uses: actions/checkout@v3
    
    - name: Set up Docker Buildx
      uses: docker/setup-buildx-action@v2
    
    - name: Login to Container Registry
      uses: docker/login-action@v2
      with:
        registry: ghcr.io
        username: ${{ github.actor }}
        password: ${{ secrets.GITHUB_TOKEN }}
    
    - name: Build and push Docker image
      uses: docker/build-push-action@v4
      with:
        context: .
        push: true
        tags: |
          ghcr.io/${{ github.repository }}:latest
          ghcr.io/${{ github.repository }}:${{ github.sha }}
        cache-from: type=gha
        cache-to: type=gha,mode=max
    
    - name: Deploy to staging
      run: |
        # Add deployment script here
        echo "Deploying to staging environment"
```

export default AppointmentCard;
```

#### Custom Hooks for Business Logic
```typescript
// Custom Hook for Appointment Management
interface UseAppointmentsReturn {
  appointments: Appointment[];
  isLoading: boolean;
  error: string | null;
  createAppointment: (data: CreateAppointmentData) => Promise<void>;
  updateAppointment: (id: string, data: UpdateAppointmentData) => Promise<void>;
  cancelAppointment: (id: string) => Promise<void>;
  refetch: () => Promise<void>;
}

const useAppointments = (filters?: AppointmentFilters): UseAppointmentsReturn => {
  const [appointments, setAppointments] = useState<Appointment[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  
  const queryClient = useQueryClient();
  
  // Fetch appointments with React Query
  const {
    data,
    isLoading: queryLoading,
    error: queryError,
    refetch
  } = useQuery({
    queryKey: ['appointments', filters],
    queryFn: () => appointmentService.getAppointments(filters),
    staleTime: 5 * 60 * 1000, // 5 minutes
  });
  
  useEffect(() => {
    if (data) {
      setAppointments(data);
    }
    setIsLoading(queryLoading);
    setError(queryError?.message || null);
  }, [data, queryLoading, queryError]);
  
  const createAppointment = useCallback(async (data: CreateAppointmentData) => {
    try {
      const newAppointment = await appointmentService.createAppointment(data);
      
      // Optimistic update
      setAppointments(prev => [...prev, newAppointment]);
      
      // Invalidate cache
      queryClient.invalidateQueries({ queryKey: ['appointments'] });
      
      toast.success('Appointment created successfully');
    } catch (error) {
      setError(error instanceof Error ? error.message : 'Failed to create appointment');
      toast.error('Failed to create appointment');
      throw error;
    }
  }, [queryClient]);
  
  const updateAppointment = useCallback(async (
    id: string, 
    data: UpdateAppointmentData
  ) => {
    try {
      const updatedAppointment = await appointmentService.updateAppointment(id, data);
      
      setAppointments(prev => 
        prev.map(apt => apt.id === id ? updatedAppointment : apt)
      );
      
      queryClient.invalidateQueries({ queryKey: ['appointments'] });
      toast.success('Appointment updated successfully');
    } catch (error) {
      setError(error instanceof Error ? error.message : 'Failed to update appointment');
      toast.error('Failed to update appointment');
      throw error;
    }
  }, [queryClient]);
  
  const cancelAppointment = useCallback(async (id: string) => {
    try {
      await appointmentService.cancelAppointment(id);
      
      setAppointments(prev => prev.filter(apt => apt.id !== id));
      queryClient.invalidateQueries({ queryKey: ['appointments'] });
      toast.success('Appointment cancelled successfully');
    } catch (error) {
      setError(error instanceof Error ? error.message : 'Failed to cancel appointment');
      toast.error('Failed to cancel appointment');
      throw error;
    }
  }, [queryClient]);
  
  return {
    appointments,
    isLoading,
    error,
    createAppointment,
    updateAppointment,
    cancelAppointment,
    refetch
  };
};
```

#### State Management with Zustand
```typescript
// Global State Store
interface AppState {
  // User state
  user: User | null;
  isAuthenticated: boolean;
  
  // UI state
  sidebarOpen: boolean;
  theme: 'light' | 'dark';
  
  // Appointment state
  selectedDate: Date;
  viewMode: 'day' | 'week' | 'month';
  
  // Actions
  setUser: (user: User | null) => void;
  toggleSidebar: () => void;
  setTheme: (theme: 'light' | 'dark') => void;
  setSelectedDate: (date: Date) => void;
  setViewMode: (mode: 'day' | 'week' | 'month') => void;
}

const useAppStore = create<AppState>((set) => ({
  // Initial state
  user: null,
  isAuthenticated: false,
  sidebarOpen: false,
  theme: 'light',
  selectedDate: new Date(),
  viewMode: 'week',
  
  // Actions
  setUser: (user) => set({ user, isAuthenticated: !!user }),
  toggleSidebar: () => set((state) => ({ sidebarOpen: !state.sidebarOpen })),
  setTheme: (theme) => set({ theme }),
  setSelectedDate: (selectedDate) => set({ selectedDate }),
  setViewMode: (viewMode) => set({ viewMode }),
}));

// Persistent state with localStorage
const usePersistedStore = create<AppState>()((
  persist(
    (set) => ({
      // ... state and actions
    }),
    {
      name: 'clinic-app-storage',
      partialize: (state) => ({ 
        theme: state.theme,
        viewMode: state.viewMode 
      }),
    }
  )
));
```

### Form Handling Patterns
```typescript
// Form with React Hook Form and Zod Validation
import { useForm } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import { z } from 'zod';

const appointmentSchema = z.object({
  patientId: z.string().min(1, 'Patient is required'),
  scheduledAt: z.date().min(new Date(), 'Date must be in the future'),
  durationMinutes: z.number().min(15).max(240),
  notes: z.string().optional(),
  type: z.enum(['consultation', 'follow-up', 'procedure'])
});

type AppointmentFormData = z.infer<typeof appointmentSchema>;

interface AppointmentFormProps {
  initialData?: Partial<AppointmentFormData>;
  onSubmit: (data: AppointmentFormData) => Promise<void>;
  onCancel: () => void;
}

const AppointmentForm: React.FC<AppointmentFormProps> = ({
  initialData,
  onSubmit,
  onCancel
}) => {
  const {
    register,
    handleSubmit,
    formState: { errors, isSubmitting },
    setValue,
    watch
  } = useForm<AppointmentFormData>({
    resolver: zodResolver(appointmentSchema),
    defaultValues: {
      durationMinutes: 30,
      type: 'consultation',
      ...initialData
    }
  });
  
  const selectedDate = watch('scheduledAt');
  
  const handleFormSubmit = async (data: AppointmentFormData) => {
    try {
      await onSubmit(data);
    } catch (error) {
      console.error('Form submission error:', error);
    }
  };
  
  return (
    <form onSubmit={handleSubmit(handleFormSubmit)} className="space-y-6">
      <div>
        <label className="block text-sm font-medium text-gray-700">
          Patient
        </label>
        <PatientSelect
          {...register('patientId')}
          error={errors.patientId?.message}
        />
      </div>
      
      <div className="grid grid-cols-2 gap-4">
        <div>
          <label className="block text-sm font-medium text-gray-700">
            Date & Time
          </label>
          <DateTimePicker
            value={selectedDate}
            onChange={(date) => setValue('scheduledAt', date)}
            error={errors.scheduledAt?.message}
          />
        </div>
        
        <div>
          <label className="block text-sm font-medium text-gray-700">
            Duration (minutes)
          </label>
          <select
            {...register('durationMinutes', { valueAsNumber: true })}
            className="mt-1 block w-full rounded-md border-gray-300"
          >
            <option value={15}>15 minutes</option>
            <option value={30}>30 minutes</option>
            <option value={60}>1 hour</option>
            <option value={120}>2 hours</option>
          </select>
          {errors.durationMinutes && (
            <p className="mt-1 text-sm text-red-600">
              {errors.durationMinutes.message}
            </p>
          )}
        </div>
      </div>
      
      <div>
        <label className="block text-sm font-medium text-gray-700">
          Notes
        </label>
        <textarea
          {...register('notes')}
          rows={3}
          className="mt-1 block w-full rounded-md border-gray-300"
          placeholder="Additional notes..."
        />
      </div>
      
      <div className="flex justify-end space-x-3">
        <Button
          type="button"
          variant="outline"
          onClick={onCancel}
        >
          Cancel
        </Button>
        <Button
          type="submit"
          disabled={isSubmitting}
        >
          {isSubmitting ? 'Saving...' : 'Save Appointment'}
        </Button>
      </div>
    </form>
  );
};
```

### API Integration Patterns
```typescript
// API Service Layer
class AppointmentService {
  private baseURL = '/api/appointments';
  
  async getAppointments(filters?: AppointmentFilters): Promise<Appointment[]> {
    const params = new URLSearchParams();
    
    if (filters?.startDate) {
      params.append('start_date', filters.startDate.toISOString());
    }
    if (filters?.endDate) {
      params.append('end_date', filters.endDate.toISOString());
    }
    if (filters?.patientId) {
      params.append('patient_id', filters.patientId);
    }
    
    const response = await fetch(`${this.baseURL}?${params}`);
    
    if (!response.ok) {
      throw new Error(`Failed to fetch appointments: ${response.statusText}`);
    }
    
    const data = await response.json();
    return data.map(this.transformAppointment);
  }
  
  async createAppointment(data: CreateAppointmentData): Promise<Appointment> {
    const response = await fetch(this.baseURL, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        patient_id: data.patientId,
        scheduled_at: data.scheduledAt.toISOString(),
        duration_minutes: data.durationMinutes,
        notes: data.notes,
        type: data.type
      })
    });
    
    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.detail || 'Failed to create appointment');
    }
    
    const appointment = await response.json();
    return this.transformAppointment(appointment);
  }
  
  private transformAppointment(data: any): Appointment {
    return {
      id: data.id,
      patientId: data.patient_id,
      patient: data.patient,
      scheduledAt: new Date(data.scheduled_at),
      durationMinutes: data.duration_minutes,
      status: data.status,
      notes: data.notes,
      type: data.type,
      createdAt: new Date(data.created_at)
    };
  }
}

// React Query Integration
const appointmentService = new AppointmentService();

export const useAppointments = (filters?: AppointmentFilters) => {
  return useQuery({
    queryKey: ['appointments', filters],
    queryFn: () => appointmentService.getAppointments(filters),
    staleTime: 5 * 60 * 1000,
    cacheTime: 10 * 60 * 1000,
  });
};

export const useCreateAppointment = () => {
  const queryClient = useQueryClient();
  
  return useMutation({
    mutationFn: appointmentService.createAppointment,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['appointments'] });
      toast.success('Appointment created successfully');
    },
    onError: (error: Error) => {
      toast.error(error.message);
    }
  });
};
```

### Testing Patterns
```typescript
// Component Testing with React Testing Library
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';

const createTestQueryClient = () => new QueryClient({
  defaultOptions: {
    queries: { retry: false },
    mutations: { retry: false },
  },
});

const renderWithProviders = (component: React.ReactElement) => {
  const queryClient = createTestQueryClient();
  
  return render(
    <QueryClientProvider client={queryClient}>
      {component}
    </QueryClientProvider>
  );
};

describe('AppointmentCard', () => {
  const mockAppointment: Appointment = {
    id: '1',
    patientId: 'patient-1',
    patient: { id: 'patient-1', name: 'John Doe' },
    scheduledAt: new Date('2024-01-15T10:00:00Z'),
    durationMinutes: 30,
    status: 'scheduled',
    notes: 'Regular checkup',
    type: 'consultation',
    createdAt: new Date('2024-01-10T10:00:00Z')
  };
  
  it('renders appointment information correctly', () => {
    renderWithProviders(
      <AppointmentCard appointment={mockAppointment} />
    );
    
    expect(screen.getByText('John Doe')).toBeInTheDocument();
    expect(screen.getByText(/Jan 15, 2024/)).toBeInTheDocument();
  });
  
  it('calls onEdit when edit button is clicked', async () => {
    const onEdit = jest.fn();
    
    renderWithProviders(
      <AppointmentCard 
        appointment={mockAppointment} 
        onEdit={onEdit}
      />
    );
    
    const editButton = screen.getByRole('button', { name: /edit/i });
    await userEvent.click(editButton);
    
    expect(onEdit).toHaveBeenCalledWith(mockAppointment);
  });
  
  it('shows loading state when canceling appointment', async () => {
    const onCancel = jest.fn().mockImplementation(
      () => new Promise(resolve => setTimeout(resolve, 100))
    );
    
    renderWithProviders(
      <AppointmentCard 
        appointment={mockAppointment} 
        onCancel={onCancel}
      />
    );
    
    const cancelButton = screen.getByRole('button', { name: /cancel/i });
    await userEvent.click(cancelButton);
    
    expect(screen.getByText('Canceling...')).toBeInTheDocument();
    
    await waitFor(() => {
      expect(screen.getByText('Cancel')).toBeInTheDocument();
    });
  });
});

// Custom Hook Testing
import { renderHook, waitFor } from '@testing-library/react';
import { rest } from 'msw';
import { setupServer } from 'msw/node';

const server = setupServer(
  rest.get('/api/appointments', (req, res, ctx) => {
    return res(ctx.json([mockAppointment]));
  })
);

beforeAll(() => server.listen());
afterEach(() => server.resetHandlers());
afterAll(() => server.close());

describe('useAppointments', () => {
  it('fetches appointments successfully', async () => {
    const { result } = renderHook(() => useAppointments(), {
      wrapper: ({ children }) => (
        <QueryClientProvider client={createTestQueryClient()}>
          {children}
        </QueryClientProvider>
      ),
    });
    
    await waitFor(() => {
      expect(result.current.isLoading).toBe(false);
    });
    
    expect(result.current.appointments).toHaveLength(1);
    expect(result.current.appointments[0].id).toBe('1');
  });
});
```

### Performance Optimization Patterns
```typescript
// Memoization Patterns
const AppointmentList: React.FC<AppointmentListProps> = ({ appointments, onEdit, onCancel }) => {
  // Memoize expensive calculations
  const sortedAppointments = useMemo(() => {
    return appointments.sort((a, b) => 
      a.scheduledAt.getTime() - b.scheduledAt.getTime()
    );
  }, [appointments]);
  
  // Memoize callback functions
  const handleEdit = useCallback((appointment: Appointment) => {
    onEdit?.(appointment);
  }, [onEdit]);
  
  const handleCancel = useCallback((appointmentId: string) => {
    onCancel?.(appointmentId);
  }, [onCancel]);
  
  return (
    <div className="space-y-4">
      {sortedAppointments.map((appointment) => (
        <AppointmentCard
          key={appointment.id}
          appointment={appointment}
          onEdit={handleEdit}
          onCancel={handleCancel}
        />
      ))}
    </div>
  );
};

// Virtual Scrolling for Large Lists
import { FixedSizeList as List } from 'react-window';

const VirtualizedAppointmentList: React.FC<{ appointments: Appointment[] }> = ({ 
  appointments 
}) => {
  const Row = ({ index, style }: { index: number; style: React.CSSProperties }) => (
    <div style={style}>
      <AppointmentCard appointment={appointments[index]} />
    </div>
  );
  
  return (
    <List
      height={600}
      itemCount={appointments.length}
      itemSize={120}
      width="100%"
    >
      {Row}
    </List>
  );
};

// Code Splitting with Lazy Loading
const AppointmentModal = lazy(() => import('./AppointmentModal'));
const ReportsPage = lazy(() => import('../pages/ReportsPage'));

const App: React.FC = () => {
  return (
    <Router>
      <Suspense fallback={<LoadingSpinner />}>
        <Routes>
          <Route path="/appointments" element={<AppointmentsPage />} />
          <Route path="/reports" element={<ReportsPage />} />
        </Routes>
      </Suspense>
    </Router>
  );
};
```
