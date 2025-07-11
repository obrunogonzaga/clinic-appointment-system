# Architecture

This document provides a comprehensive architectural overview of the Clinic Appointment Scheduling System, detailing the system design, technology choices, and implementation patterns.

## System Architecture Overview

The system follows a three-tier architecture with clear separation of concerns:

```
                      +-------------------+                       
                      |      Frontend     |                       
                      | (React SPA)       |                       
                      +---------+---------+                       
                                |                                 
                                | HTTP API                         
                                |                                 
                      +---------v---------+                       
                      |      Backend      |                       
                      | (Python API)      |                       
                      +---------+---------+                       
                                |                                 
                                | Database Queries                 
                                |                                 
                      +---------v---------+                       
                      |    Database      |                        
                      | (MongoDB)        |                        
                      +-------------------+                       
```

### Architectural Principles

1. **Clean Architecture** - Domain models remain framework-agnostic
2. **Containerization** - Docker isolates services while enabling easy scaling
3. **API-First Design** - OpenAPI specification drives implementation
4. **Stateless Services** - Horizontal scaling enabled via JWT tokens

## Backend: Clean Architecture Implementation

The backend follows Clean Architecture principles with three distinct layers:

### Domain Layer (Core Business Logic)
- **Entities:** `Patient`, `Appointment`, `Schedule`, `Clinic`
- **Value Objects:** `TimeSlot`, `ContactInfo`, `Address`
- **Domain Services:** Appointment conflict resolution, scheduling rules
- **Repository Interfaces:** Abstract data access contracts

### Application Layer (Use Cases)
- **Use Cases:** `CreateAppointment`, `RescheduleAppointment`, `GenerateReport`
- **DTOs:** Data transfer objects for API communication
- **Application Services:** Orchestrate domain operations
- **Event Handlers:** Process domain events (notifications, audit logs)

### Infrastructure Layer (Technical Implementation)
- **Database:** MongoDB repositories and connection management
- **Web Framework:** FastAPI controllers and middleware
- **External Services:** Email/SMS providers, PDF generation
- **Configuration:** Environment variables and settings management

## Frontend Architecture

### React Component Hierarchy
```
App
├── Layout
│   ├── Header
│   ├── Navigation
│   └── Footer
├── Pages
│   ├── Dashboard
│   ├── Patients
│   ├── Schedule
│   └── Reports
└── Components
    ├── Common (Button, Modal, Table)
    ├── Forms (PatientForm, AppointmentForm)
    └── Charts (ScheduleChart, ReportsChart)
```

### State Management
- **React Query** - Server state management and caching
- **Zustand** - Client-side state management
- **React Hook Form** - Form state and validation

### Key Frontend Features
- **Responsive Design** - Mobile-first approach with Tailwind CSS
- **Real-time Updates** - WebSocket integration for live schedule changes
- **Offline Support** - Service worker for basic functionality
- **Accessibility** - WCAG 2.1 AA compliance

## Technology Stack

### Backend Foundation
- **Python 3.11** - Balance of performance and development speed
- **FastAPI** - High-performance API framework with automatic OpenAPI docs
- **MongoDB 6.0** - Flexible document storage for healthcare data
- **Pydantic** - Data validation and settings management
- **Motor** - Async MongoDB driver for Python

### Frontend Ecosystem
- **React 18** - Component-based UI development with concurrent features
- **Vite 4** - Fast development toolchain and build system
- **TanStack Table** - Powerful data table implementation
- **PDF-LIB** - Client-side PDF generation and manipulation
- **Tailwind CSS** - Utility-first CSS framework

### DevOps Pipeline
- **Docker Compose** - Local development environment orchestration
- **GitHub Actions** - CI/CD workflows and automated testing
- **Prometheus** - Metrics collection and monitoring
- **Grafana** - Operational dashboards and alerting

## Data Processing Architecture

### File Processing Pipeline
```
[CSV Upload] → [Validation] → [Normalization] → [MongoDB]
       ↑           ↓               ↓
[Error Log] ← [Rejection]   [PDF Generation]
```

### Data Flow
1. **Upload** - Multi-format file support (CSV, XLS, XLSX)
2. **Validation** - Schema validation and business rule checking
3. **Transformation** - Data normalization and enrichment
4. **Storage** - Atomic operations with rollback capability
5. **Notification** - Real-time updates to connected clients

## Security Architecture

### Authentication & Authorization
- **JWT Tokens** - Stateless authentication with refresh tokens
- **RBAC** (Role-Based Access Control) - Granular permission system
- **OAuth 2.0** - Integration with external identity providers
- **Session Management** - Secure token storage and rotation

### Data Protection
- **Encryption at Rest** - MongoDB encryption with customer-managed keys
- **Encryption in Transit** - TLS 1.3 for all communications
- **Data Masking** - PII protection in logs and non-production environments
- **Audit Logging** - Comprehensive activity tracking for HIPAA compliance

### Infrastructure Security
- **Container Security** - Distroless images and vulnerability scanning
- **Network Isolation** - Service mesh with mTLS
- **Secrets Management** - HashiCorp Vault integration
- **Rate Limiting** - API protection against abuse

## Containerization Strategy

### Docker Services
```yaml
services:
  backend:
    - Python FastAPI application
    - Health checks and graceful shutdown
    - Multi-stage build for optimization
  
  frontend:
    - Nginx serving React build
    - Gzip compression and caching
    - Security headers configuration
  
  database:
    - MongoDB with replica set
    - Persistent volume mounting
    - Backup and restore capabilities
  
  monitoring:
    - Prometheus metrics collection
    - Grafana dashboard visualization
    - Alert manager for notifications
```

### Deployment Patterns
- **Blue-Green Deployment** - Zero-downtime releases
- **Health Checks** - Kubernetes readiness and liveness probes
- **Auto-scaling** - Horizontal pod autoscaling based on metrics
- **Circuit Breakers** - Fault tolerance and graceful degradation
