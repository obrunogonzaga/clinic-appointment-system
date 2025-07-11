"""
Main FastAPI application entry point
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import os
from typing import Dict, Any

# Create FastAPI app instance
app = FastAPI(
    title="Clinic Appointment System API",
    description="Sistema de agendamento de consultas para clínicas médicas",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/", tags=["Root"])
async def root() -> Dict[str, str]:
    """Root endpoint"""
    return {
        "message": "Welcome to Clinic Appointment System API",
        "version": "1.0.0",
        "docs": "/docs"
    }

@app.get("/health", tags=["Health"])
async def health_check() -> Dict[str, Any]:
    """Health check endpoint"""
    return {
        "status": "healthy",
        "service": "clinic-appointment-api",
        "version": "1.0.0",
        "environment": os.getenv("ENVIRONMENT", "development")
    }

@app.get("/api/v1/status", tags=["Status"])
async def api_status() -> Dict[str, str]:
    """API status endpoint"""
    return {
        "status": "operational",
        "message": "API is running properly"
    }

# This will be expanded with routers as we build the application
# Example:
# from src.presentation.routes import auth_router, appointment_router, patient_router
# app.include_router(auth_router, prefix="/api/v1/auth", tags=["Authentication"])
# app.include_router(appointment_router, prefix="/api/v1/appointments", tags=["Appointments"])
# app.include_router(patient_router, prefix="/api/v1/patients", tags=["Patients"])