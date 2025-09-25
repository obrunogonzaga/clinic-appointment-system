import { Role } from '../constants/roles';
import type { User } from '../types/auth';

const normalizeRawRole = (rawRole?: string | null): Role | null => {
  if (!rawRole) {
    return null;
  }

  const normalized = rawRole.trim().toLowerCase();

  if (normalized === 'admin' || normalized === 'administrator') {
    return Role.ADMIN;
  }

  if (
    normalized === 'colaborador' ||
    normalized === 'collaborator' ||
    normalized === 'user'
  ) {
    return Role.COLABORADOR;
  }

  return null;
};

export const resolveUserRole = (user?: User | null): Role | null => {
  if (!user) {
    return null;
  }

  const fromRoleField = normalizeRawRole(user.role);
  if (fromRoleField) {
    return fromRoleField;
  }

  if (typeof user.is_admin !== 'undefined') {
    return user.is_admin ? Role.ADMIN : Role.COLABORADOR;
  }

  return Role.COLABORADOR;
};

export const isAdmin = (user?: User | null): boolean => {
  return resolveUserRole(user) === Role.ADMIN;
};

