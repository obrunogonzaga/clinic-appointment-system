export const ROLES = {
  ADMIN: 'ADMIN',
  COLABORADOR: 'COLABORADOR',
} as const;

export type Role = (typeof ROLES)[keyof typeof ROLES];

export const ROLE_LABELS: Record<Role, string> = {
  [ROLES.ADMIN]: 'Administrador',
  [ROLES.COLABORADOR]: 'Colaborador',
};
