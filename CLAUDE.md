# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Status

**Current Phase**: Planning and Documentation Complete - Ready for Implementation

This is a Clinic Appointment Scheduling System that is currently in the planning phase. The implementation has not yet begun, but comprehensive documentation and architecture planning is complete.

## Development Commands

**CRITICAL QUALITY REQUIREMENTS:**
- **ALWAYS run `make lint` before committing any changes and fix all errors**
- **ALWAYS ensure test coverage stays at 80% or higher**
- **NEVER commit code that fails linting or has coverage below 80%**

Use the following commands for quality checks:

**Quality Check Commands (REQUIRED before commits):**
```bash
# Check all linting and fix issues
make lint

# Run all tests with coverage
make test

# Check specific parts
make lint-backend      # Backend linting only
make lint-frontend     # Frontend linting only
make test-backend      # Backend tests with coverage (requires 80%+)
make test-frontend     # Frontend tests with coverage (requires 80%+)
```

**Backend (Python/FastAPI):**
```bash
# Setup virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Run development server
uvicorn main:app --reload --host 0.0.0.0 --port 8000

# Run tests
pytest

# Run linting
black .
flake8 .
isort .
mypy .
```

**Frontend (React/TypeScript):**
```bash
# Install dependencies
npm install

# Run development server
npm run dev

# Build for production
npm run build

# Run tests
npm test

# Run linting
npm run lint
npm run type-check
```

**Docker (Full Stack):**
```bash
# Build and run all services
docker-compose up --build

# Run in detached mode
docker-compose up -d

# Stop services
docker-compose down
```

## Architecture Overview

### Three-Tier Architecture
- **Frontend**: React 18 SPA with TypeScript, Vite, Tailwind CSS
- **Backend**: Python FastAPI with Clean Architecture principles
- **Database**: MongoDB 6.0 with async Motor driver

### Backend Clean Architecture Layers
```
src/
├── domain/           # Business entities and rules
├── application/      # Use cases and DTOs
├── infrastructure/   # Database, external services
└── presentation/     # FastAPI controllers and routes
```

### Frontend Structure
```
src/
├── components/       # Reusable UI components
├── pages/           # Top-level page components
├── hooks/           # Custom React hooks
├── services/        # API integration layer
├── types/           # TypeScript type definitions
└── utils/           # Utility functions
```

## Key Business Domain

### Core Entities
- **Patient**: Healthcare facility clients
- **Appointment**: Scheduled healthcare consultations
- **User**: System users (admin, doctor, nurse, receptionist)
- **Schedule**: Time-based appointment organization

### Primary Features
1. **Excel Data Import**: Upload and process appointment sheets
2. **Appointment Management**: Create, update, cancel appointments
3. **Data Filtering**: Filter by "Nome da Unidade" and "Nome da Marca"
4. **PDF Report Generation**: Generate reports using "Template Rota Domiciliar"
5. **Role-Based Access Control**: Admin, Doctor, Nurse, Receptionist roles

## Technology Stack Details

### Backend Dependencies
- **FastAPI**: Web framework with automatic OpenAPI docs
- **Motor**: Async MongoDB driver
- **Pydantic**: Data validation and serialization
- **PyJWT**: JWT token handling
- **Passlib**: Password hashing
- **Pandas**: Excel file processing
- **ReportLab**: PDF generation

### Frontend Dependencies
- **React Query/TanStack Query**: Server state management
- **Zustand**: Client state management
- **React Hook Form**: Form handling
- **Zod**: Schema validation
- **TanStack Table**: Data table component
- **PDF-LIB**: Client-side PDF manipulation
- **Date-fns**: Date manipulation

### DevOps Stack
- **Docker & Docker Compose**: Containerization
- **MongoDB**: Primary database
- **Nginx**: Frontend serving and reverse proxy
- **Prometheus & Grafana**: Monitoring and metrics

## Development Patterns

### Backend Patterns
- **Clean Architecture**: Separation of concerns with domain-driven design
- **Repository Pattern**: Abstract data access layer
- **Use Case Pattern**: Business logic encapsulation
- **Result Pattern**: Functional error handling instead of exceptions
- **Dependency Injection**: Testable, loosely coupled components

### Frontend Patterns
- **Custom Hooks**: Business logic abstraction
- **Compound Components**: Flexible, reusable UI components
- **Render Props**: Component composition patterns
- **Error Boundaries**: Graceful error handling
- **Code Splitting**: Lazy loading for performance

## Security Considerations

### Authentication & Authorization
- JWT tokens with refresh token rotation
- Role-based access control (RBAC)
- Password hashing with bcrypt
- Session management and timeout

### Data Protection
- HIPAA compliance for healthcare data
- Data encryption at rest and in transit
- Input validation and sanitization
- Audit logging for compliance

### API Security
- Rate limiting
- CORS configuration
- Request/response validation
- SQL injection prevention (using ODM)

## File Processing

### Excel Import Pipeline
1. **Upload**: Multi-format support (CSV, XLS, XLSX)
2. **Validation**: Schema validation and business rules
3. **Transformation**: Data normalization and enrichment
4. **Storage**: Atomic operations with rollback capability

### PDF Generation
- Template-based reports using "Template Rota Domiciliar.pdf"
- Client-side PDF manipulation with PDF-LIB
- Server-side PDF generation with ReportLab
- Batch report generation capabilities

## Sample Data

The project includes sample Excel files in `docs/sample-sheets/` that demonstrate the expected data format for appointment imports:
- Portuguese language appointment data
- Fields include unit names, brand names, patient info, appointment times
- Used for testing import functionality

## Next Implementation Steps

1. **Backend Setup**: Initialize FastAPI project structure
2. **Database Setup**: Configure MongoDB with proper indexes
3. **Authentication**: Implement JWT-based user authentication
4. **Core API**: Build appointment CRUD operations
5. **Frontend Setup**: Initialize React project with TypeScript
6. **Integration**: Connect frontend to backend APIs
7. **File Processing**: Implement Excel import functionality
8. **PDF Generation**: Build report generation system
9. **Testing**: Unit and integration tests
10. **Deployment**: Docker containerization and CI/CD

## Important Notes

- All text and user-facing content should be in **Portuguese** (Brazilian Portuguese)
- The system handles Brazilian healthcare terminology and formats
- Date/time formats should follow Brazilian standards
- Phone number formats should support Brazilian patterns
- The UI should be intuitive for healthcare staff with varying technical skills

## Compliance Requirements

- **HIPAA**: Healthcare data privacy and security
- **GDPR**: Data protection for international users  
- **WCAG 2.1 AA**: Accessibility compliance
- **Audit Trails**: Comprehensive logging for compliance

When implementing features, always consider these compliance requirements and ensure proper data handling, logging, and access controls are in place.