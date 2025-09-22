"""
User-related enums and permission mappings.
"""

from enum import Enum
from typing import List, Dict


class UserRole(str, Enum):
    """User roles in the system."""
    ADMIN = "admin"
    MOTORISTA = "motorista"
    COLETOR = "coletor"
    COLABORADOR = "colaborador"


class UserStatus(str, Enum):
    """User account status."""
    PENDENTE = "pendente"      # Aguardando aprovação do admin
    APROVADO = "aprovado"      # Aprovado e ativo
    REJEITADO = "rejeitado"    # Rejeitado pelo admin
    SUSPENSO = "suspenso"      # Suspenso temporariamente
    INATIVO = "inativo"        # Desativado/deletado


class Permission(str, Enum):
    """System permissions."""
    # User management
    USER_CREATE = "user:create"
    USER_READ = "user:read"
    USER_UPDATE = "user:update"
    USER_DELETE = "user:delete"
    USER_APPROVE = "user:approve"
    USER_LIST = "user:list"
    
    # Route management (rotas de coleta)
    ROUTE_CREATE = "route:create"
    ROUTE_READ = "route:read"
    ROUTE_UPDATE = "route:update"
    ROUTE_DELETE = "route:delete"
    ROUTE_ASSIGN = "route:assign"
    
    # Collection management (registros de coleta)
    COLLECTION_CREATE = "collection:create"
    COLLECTION_READ = "collection:read"
    COLLECTION_UPDATE = "collection:update"
    COLLECTION_DELETE = "collection:delete"
    COLLECTION_VALIDATE = "collection:validate"
    
    # Vehicle management
    VEHICLE_CREATE = "vehicle:create"
    VEHICLE_READ = "vehicle:read"
    VEHICLE_UPDATE = "vehicle:update"
    VEHICLE_DELETE = "vehicle:delete"
    VEHICLE_ASSIGN = "vehicle:assign"
    
    # Report management
    REPORT_CREATE = "report:create"
    REPORT_READ = "report:read"
    REPORT_EXPORT = "report:export"
    REPORT_ADMIN = "report:admin"
    
    # System management
    SYSTEM_CONFIG = "system:config"
    SYSTEM_LOGS = "system:logs"
    SYSTEM_AUDIT = "system:audit"
    SYSTEM_BACKUP = "system:backup"


# Role-based permissions mapping
ROLE_PERMISSIONS: Dict[UserRole, List[str]] = {
    UserRole.ADMIN: [
        # Admin tem todas as permissões
        p.value for p in Permission
    ],
    
    UserRole.MOTORISTA: [
        # Motorista pode ver e atualizar rotas atribuídas
        Permission.ROUTE_READ.value,
        Permission.ROUTE_UPDATE.value,
        # Pode registrar coletas
        Permission.COLLECTION_CREATE.value,
        Permission.COLLECTION_READ.value,
        Permission.COLLECTION_UPDATE.value,
        # Pode ver veículos
        Permission.VEHICLE_READ.value,
        # Pode gerar relatórios próprios
        Permission.REPORT_CREATE.value,
        Permission.REPORT_READ.value,
        Permission.REPORT_EXPORT.value,
    ],
    
    UserRole.COLETOR: [
        # Coletor pode ver rotas atribuídas
        Permission.ROUTE_READ.value,
        # Pode registrar e atualizar coletas
        Permission.COLLECTION_CREATE.value,
        Permission.COLLECTION_READ.value,
        Permission.COLLECTION_UPDATE.value,
        # Pode ver relatórios próprios
        Permission.REPORT_READ.value,
    ],
    
    UserRole.COLABORADOR: [
        # Colaborador tem acesso limitado
        Permission.ROUTE_READ.value,
        Permission.COLLECTION_READ.value,
        Permission.REPORT_READ.value,
    ],
}


def get_role_permissions(role: UserRole) -> List[str]:
    """
    Get permissions for a specific role.
    
    Args:
        role: User role
        
    Returns:
        List of permission strings
    """
    return ROLE_PERMISSIONS.get(role, [])


def has_permission(role: UserRole, permission: str) -> bool:
    """
    Check if a role has a specific permission.
    
    Args:
        role: User role
        permission: Permission to check
        
    Returns:
        True if role has permission, False otherwise
    """
    return permission in get_role_permissions(role)