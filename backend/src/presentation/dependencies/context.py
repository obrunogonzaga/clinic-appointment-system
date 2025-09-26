"""FastAPI dependency helpers for request context extraction."""

from __future__ import annotations

from fastapi import HTTPException, Request, status

from src.application.common import RequestContext, UserRole


async def get_request_context(request: Request) -> RequestContext:
    """Build a RequestContext object from headers and connection info."""

    user_id = request.headers.get("X-User-Id") or "system"
    tenant_id = request.headers.get("X-Tenant-Id") or "default"
    role_header = request.headers.get("X-User-Role") or UserRole.COLLABORATOR.value

    try:
        role = UserRole(role_header.lower())
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Perfil de usuário inválido",
        ) from exc

    source_ip = request.headers.get("X-Forwarded-For")
    if not source_ip and request.client:
        source_ip = request.client.host

    return RequestContext(
        user_id=user_id,
        tenant_id=tenant_id,
        role=role,
        source_ip=source_ip,
    )
