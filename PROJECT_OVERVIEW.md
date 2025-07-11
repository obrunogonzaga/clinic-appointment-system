# Project Overview: Clinic Appointment Scheduling System

This document provides a high-level overview of the Clinic Appointment Scheduling System (v2) to guide its reimplementation or further development.

## 1. Architecture

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

Key architectural principles:
1. **Clean Architecture** - Domain models remain framework-agnostic
2. **Containerization** - Docker isolates services while enabling easy scaling
3. **API-First Design** - OpenAPI specification drives implementation
4. **Stateless Services** - Horizontal scaling enabled via JWT tokens

-   **Backend:** A Python-based RESTful API. It will be built following **Clean Architecture** principles to ensure a clear separation of concerns between business rules (Domain), application logic (Application), and technical details (Infrastructure). This will make the system more maintainable, testable, and independent of frameworks and external agencies.
-   **Frontend:** A single-page application (SPA) built with React that provides the user interface.
-   **Containerization:** The entire application stack (backend, frontend, database) will be containerized using Docker. A `docker-compose.yml` file will be created at the project root to define, configure, and run all the necessary services (API, web client, database).

## 2. Technology Stack

### Backend Foundation
- **Python 3.11** - Balance of performance and development speed
- **FastAPI** - High-performance API framework with automatic docs
- **MongoDB 6.0** - Flexible document storage for healthcare data
- **Pydantic** - Data validation and settings management

### Frontend Ecosystem
- **React 18** - Component-based UI development
- **Vite 4** - Fast development toolchain
- **TanStack Table** - Powerful data table implementation
- **PDF-LIB** - Client-side PDF generation

### DevOps Pipeline
- **Docker Compose** - Local development environment
- **GitHub Actions** - CI/CD workflows
- **Prometheus** - Metrics collection
- **Grafana** - Operational dashboards

Based on the file structure, the key technologies are:

-   **Backend:**
    -   **Language:** Python
    -   **Framework:** Likely **FastAPI** or **Flask** (inferred from `src/main.py` and the `api/endpoints` structure).
    -   **Database:** **MongoDB** (inferred from `db/mongodb.py` and `scripts/mongo-init.js`).
    -   **Dependencies:** Managed by `requirements.txt`.

-   **Frontend:**
    -   **Library:** **React** (inferred from `.jsx` files and `package.json`).
    -   **Build Tool:** **Vite** (inferred from `vite.config.js`).
    -   **Styling:** **Tailwind CSS** (inferred from `tailwind.config.js`).
    -   **Dependencies:** Managed by `package.json`.

-   **DevOps & Tooling:**
    -   **Containerization:** Docker, Docker Compose.
    -   **Task Runner:** `Makefile` for automating common commands.
    -   **Scripts:** A collection of shell and Python scripts in `.claude/commands/` and `scripts/` for various tasks like database seeding, deployment, and code generation.

## 3. Core Features & Modules

### Appointment Lifecycle Management
1. **Scheduling** - Conflict checking, recurrence patterns
2. **Notifications** - SMS/Email reminders via Twilio
3. **Rescheduling** - Patient self-service portal
4. **Cancellation** - Audit trail tracking

### Data Processing Pipeline
```
[CSV Upload] → [Validation] → [Normalization] → [MongoDB]
       ↑           ↓               ↓
[Error Log] ← [Rejection]   [PDF Generation]
```

### Security Architecture
- **RBAC** (Role-Based Access Control)
- **JWT Authentication** with refresh tokens
- **Audit Logging** for HIPAA compliance
- **Data Encryption** at rest and in transit

The project is organized into several key functional areas:

| Feature                 | Backend Modules (`backend/src/`)                               | Frontend Components (`frontend/src/`)                                                              |
| ----------------------- | -------------------------------------------------------------- | -------------------------------------------------------------------------------------------------- |
| **Patient Management**  | `api/endpoints/patients.py`, `models/patient.py`               | `pages/Patients.jsx`, `components/patients/*` (PatientList, PatientProfile, PatientModal, etc.)    |
| **Appointment Scheduling** | `api/endpoints/schedule.py`, `services/appointment_service.py` | `pages/Schedule.jsx`, `components/schedule/CalendarView.jsx`                                       |
| **Data Import & Processing** | `api/endpoints/files.py`, `services/file_processor.py`         | `components/schedule/UploadStep.jsx`, `services/fileProcessor.js`                                  |

## 4. Directory Structure Highlights

-   `backend/`: Contains the Python API server.
    -   `src/api/endpoints/`: Defines the API routes.
    -   `src/models/`: Defines the MongoDB data models (e.g., `Appointment`, `Patient`).
    -   `src/services/`: Contains the core business logic.
-   `frontend/`: Contains the React web client.
    -   `src/pages/`: Top-level components for each main view.
    -   `src/components/`: Reusable UI components, organized by feature.
    -   `src/services/`: Functions for communicating with the backend API.
-   `docker/`: Holds the `docker-compose.yml` and `Dockerfile` for building and running the application services.
-   `.claude/`: Appears to be a dedicated directory for project documentation, commands, and settings, possibly for an AI assistant.
-   `agenda_laboratorio.csv`: A sample data file, likely used for testing the file import functionality.

## 5. Getting Started (Reimplementation Path)

1.  **Understand the Services:** Begin by examining `docker/docker-compose.yml` to see how the backend, frontend, and database services are defined and connected.
2.  **Set up the Backend:**
    -   Install dependencies from `requirements.txt`.
    -   Review `backend/.env.example` to understand the necessary environment variables.
    -   Explore the API endpoints in `backend/src/api/endpoints/`.
3.  **Set up the Frontend:**
    -   Run `npm install` in the `frontend/` directory.
    -   Review `vite.config.js` for any proxy settings or build configurations.
    -   Explore the main application component (`App.jsx`) and the page components in `frontend/src/pages/`.
4.  **Launch the Application:** Use `docker-compose up` to build and start all services.
5.  **Explore the UI:** Navigate the frontend to understand the user flows and how they correspond to the backend API calls.

## 6. User Interface (UI) and User Experience (UX)

The UI will be designed to be intuitive and efficient for clinic staff. Key features include:

-   **Sheet Upload and Parsing:** Users can upload appointment sheets in the format found in `docs/sample-sheets`. The system will parse these sheets and display the data in a table.
-   **Data Filtering:** The main data table can be filtered by "Nome da Unidade" and "Nome da Marca" to allow users to quickly find the information they need.
-   **PDF Generation:** Users can select one or more rows in the table and click a "Generate PDF" button. The system will then generate a PDF file based on the `Template Rota Domiciliar.pdf` file, populating it with the data from the selected rows.
