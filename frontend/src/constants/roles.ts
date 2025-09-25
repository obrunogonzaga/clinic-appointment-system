export enum Role {
  COLABORADOR = 'COLABORADOR',
  ADMIN = 'ADMIN',
}

export const ROLE_LABELS: Record<Role, string> = {
  [Role.COLABORADOR]: 'Colaborador',
  [Role.ADMIN]: 'Administrador',
};

export const ALL_ROLES: Role[] = [Role.COLABORADOR, Role.ADMIN];

