import type { User } from '../types/auth';
import { ROLES, type Role } from '../constants/roles';

const ADMIN_LIKE_ROLES = new Set(['admin']);

export function resolveUserRole(user: User | null | undefined): Role | null {
  if (!user) {
    return null;
  }

  if (user.is_admin || ADMIN_LIKE_ROLES.has(String(user.role).toLowerCase())) {
    return ROLES.ADMIN;
  }

  return ROLES.COLABORADOR;
}

export function userHasRole(user: User | null | undefined, role: Role): boolean {
  return resolveUserRole(user) === role;
}

export function userHasAnyRole(
  user: User | null | undefined,
  allowedRoles: Role[],
): boolean {
  const resolvedRole = resolveUserRole(user);
  return resolvedRole !== null && allowedRoles.includes(resolvedRole);
}
