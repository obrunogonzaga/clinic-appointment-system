# Project Context: Clinic Appointment Scheduling System

This document provides comprehensive context for the AI assistant to effectively help with the development of the Clinic Appointment Scheduling System. It serves as the central reference for understanding the project's current state, technical decisions, and development workflow.

## Project Overview

The Clinic Appointment Scheduling System is a modern web application designed to streamline appointment management for healthcare facilities. The system focuses on core functionality while maintaining scalability and user experience excellence.

### Business Context
- **Target Users**: Healthcare administrators, receptionists, doctors, and nurses
- **Primary Use Case**: Efficient appointment scheduling and patient management
- **Key Business Value**: Reduced administrative overhead and improved patient experience
- **Compliance Requirements**: Healthcare data privacy and security standards

## Current State

The project is in the **initial planning and architecture phase**. Core documentation has been established, and technical decisions have been finalized.

### Project Phase: Planning & Setup
- ✅ Project requirements defined (PRD.md)
- ✅ Architecture documented (ARCHITECTURE.md)
- ✅ Code patterns established (CODE_PATTERNS.md)
- ✅ Project overview completed (PROJECT_OVERVIEW.md)
- 🔄 **Current Focus**: Implementation planning and environment setup
- ⏳ **Next Phase**: Backend development and database setup

### Technical Decisions Made
1. **Backend**: Python with FastAPI and Clean Architecture
2. **Frontend**: React with TypeScript and modern tooling
3. **Database**: MongoDB for flexibility and scalability
4. **Containerization**: Docker with docker-compose for development
5. **Authentication**: JWT-based with role-based access control
6. **Testing**: Comprehensive unit and integration testing strategy

## Key Files & Documentation

### Core Documentation
- **`PROJECT_OVERVIEW.md`**: High-level project overview with architecture and features
- **`.claude/PRD.md`**: Detailed product requirements and specifications
- **`.claude/ARCHITECTURE.md`**: Technical architecture and system design
- **`.claude/CODE_PATTERNS.md`**: Development patterns and coding standards
- **`.claude/CONTEXT.md`**: This file - project context and guidelines

### Sample Data & Templates
- **`docs/sample-sheets/`**: Excel file examples for import functionality
  - `Relatorio de agendamento - 2025-06-20T122858.131.xls`
  - `Relatorio de agendamento - 2025-06-20T122913.065.xls`
  - `Relatorio de agendamento - 2025-06-20T123139.568.xls`
- **`docs/template/Template Rota Domiciliar.pdf`**: PDF template for report generation

### Future Implementation Structure
```
clini-appointment/
├── backend/                 # Python FastAPI application
│   ├── src/
│   │   ├── domain/         # Business logic and entities
│   │   ├── application/    # Use cases and services
│   │   ├── infrastructure/ # External integrations
│   │   └── presentation/   # API endpoints
│   ├── tests/
│   ├── requirements.txt
│   └── Dockerfile
├── frontend/               # React TypeScript application
│   ├── src/
│   │   ├── components/     # Reusable UI components
│   │   ├── pages/         # Application pages
│   │   ├── hooks/         # Custom React hooks
│   │   ├── services/      # API integration
│   │   └── types/         # TypeScript definitions
│   ├── package.json
│   └── Dockerfile
├── docker-compose.yml      # Development environment
├── .env.example           # Environment variables template
└── README.md              # Setup and development guide
```

## Development Goals & Roadmap

### Phase 1: Foundation (Current)
1. ✅ Complete project documentation and planning
2. 🔄 Set up development environment and tooling
3. ⏳ Initialize backend project structure
4. ⏳ Initialize frontend project structure
5. ⏳ Configure Docker development environment

### Phase 2: Core Backend (Next)
1. Implement domain entities and business logic
2. Set up MongoDB integration and repositories
3. Create authentication and authorization system
4. Develop appointment management APIs
5. Implement patient management APIs
6. Add comprehensive testing suite

### Phase 3: Frontend Development
1. Set up React application with routing
2. Implement authentication flow
3. Create appointment management interface
4. Develop patient management interface
5. Add data visualization components
6. Implement responsive design

### Phase 4: Integration & Features
1. Excel import/export functionality
2. PDF report generation
3. Email and SMS notifications
4. Advanced scheduling features
5. Performance optimization
6. Security hardening

### Phase 5: Deployment & Monitoring
1. Production deployment configuration
2. CI/CD pipeline setup
3. Monitoring and logging implementation
4. Performance monitoring
5. Security auditing
6. Documentation finalization

## Development Environment

### Required Tools
- **Python 3.11+**: Backend development
- **Node.js 18+**: Frontend development
- **Docker & Docker Compose**: Containerization
- **MongoDB**: Database (via Docker)
- **Git**: Version control
- **VS Code/PyCharm**: Recommended IDEs

### Development Workflow
1. **Feature Development**: Create feature branches from `develop`
2. **Code Quality**: Follow patterns defined in CODE_PATTERNS.md
3. **Testing**: Write tests for all new functionality
4. **Documentation**: Update relevant documentation
5. **Review**: Code review before merging
6. **Integration**: Merge to `develop` for testing
7. **Release**: Merge to `main` for production

## Technical Constraints & Considerations

### Performance Requirements
- **Response Time**: < 200ms for API endpoints
- **Concurrent Users**: Support 100+ simultaneous users
- **Data Volume**: Handle 10,000+ appointments efficiently
- **Availability**: 99.9% uptime target

### Security Requirements
- **Authentication**: Multi-factor authentication support
- **Authorization**: Role-based access control (RBAC)
- **Data Encryption**: At rest and in transit
- **Audit Logging**: Comprehensive activity tracking
- **Input Validation**: Strict validation and sanitization

### Scalability Considerations
- **Horizontal Scaling**: Stateless application design
- **Database Optimization**: Proper indexing and query optimization
- **Caching Strategy**: Redis for session and data caching
- **Load Balancing**: Support for multiple application instances

## Team Guidelines

### Communication
- **Documentation First**: Update documentation with changes
- **Clear Commit Messages**: Follow conventional commit format
- **Issue Tracking**: Use GitHub issues for feature requests and bugs
- **Code Reviews**: Mandatory for all changes

### Quality Standards
- **Code Coverage**: Minimum 80% test coverage
- **Type Safety**: Full TypeScript usage in frontend
- **Code Style**: Automated formatting with Black (Python) and Prettier (TypeScript)
- **Security**: Regular dependency updates and security scanning

### AI Assistant Guidelines

When helping with this project, the AI assistant should:

1. **Follow Architecture**: Adhere to Clean Architecture principles
2. **Use Patterns**: Apply patterns defined in CODE_PATTERNS.md
3. **Maintain Quality**: Ensure code quality and testing standards
4. **Consider Security**: Always implement security best practices
5. **Update Documentation**: Keep documentation current with changes
6. **Think Scalability**: Consider future growth and performance
7. **Validate Requirements**: Cross-reference with PRD.md for accuracy
8. **Maintain Consistency**: Follow established naming and structure conventions

### Common Development Tasks

#### Setting Up Development Environment
```bash
# Clone repository
git clone <repository-url>
cd clinic-appointment

# Start development environment
docker-compose up -d

# Install backend dependencies
cd backend
pip install -r requirements.txt
pip install -r requirements-dev.txt

# Install frontend dependencies
cd ../frontend
npm install

# Run tests
npm test              # Frontend tests
cd ../backend && pytest  # Backend tests
```

#### Creating New Features
1. Create feature branch: `git checkout -b feature/appointment-conflicts`
2. Implement following Clean Architecture layers
3. Add comprehensive tests
4. Update relevant documentation
5. Submit pull request with detailed description

#### Database Operations
- Use migration scripts for schema changes
- Follow indexing strategies defined in ARCHITECTURE.md
- Test with sample data from `docs/sample-sheets/`

## Project Success Metrics

### Technical Metrics
- **Code Quality**: Maintainability index > 80
- **Performance**: All API endpoints < 200ms response time
- **Reliability**: < 0.1% error rate
- **Security**: Zero critical vulnerabilities

### Business Metrics
- **User Adoption**: 90% of target users actively using system
- **Efficiency**: 50% reduction in appointment scheduling time
- **Accuracy**: 99% data accuracy in appointments and patient records
- **Satisfaction**: User satisfaction score > 4.5/5

This context document should be referenced throughout development to ensure alignment with project goals and maintain consistency across all development activities.
