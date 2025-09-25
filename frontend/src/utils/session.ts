import type { Role } from '../constants/roles';
import { ROLES } from '../constants/roles';
import type { User } from '../types/auth';

const ADMIN_ALIASES = new Set(['admin', 'ADMIN', 'Administrador']);

export const getUserRole = (user?: User | null): Role => {
  if (!user) {
    return ROLES.COLABORADOR;
  }

  if (user.role && ADMIN_ALIASES.has(user.role)) {
    return ROLES.ADMIN;
  }

  if (user.is_admin) {
    return ROLES.ADMIN;
  }

  return ROLES.COLABORADOR;
};

export const userHasRole = (user: User | null, allowedRoles: Role[]): boolean => {
  const role = getUserRole(user);
  return allowedRoles.includes(role);
};

export const formatRoleLabel = (role: Role): string =>
  role === ROLES.ADMIN ? 'Administrador' : 'Colaborador';
