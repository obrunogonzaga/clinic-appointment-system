import {
  CalendarDaysIcon,
  HomeIcon,
  Squares2X2Icon,
  TagIcon,
  TruckIcon,
  UserIcon,
  UsersIcon,
} from '@heroicons/react/24/outline';
import type React from 'react';
import { ROLES, type Role } from '../constants/roles';

export type NavigationGroupId = 'operacao' | 'cadastros' | 'administracao';

export interface NavigationItem {
  id: string;
  label: string;
  description?: string;
  group: NavigationGroupId;
  icon: React.ComponentType<React.SVGProps<SVGSVGElement>>;
  to: string;
  matchPaths?: string[];
  allowedRoles: Role[];
}

export const NAVIGATION_GROUP_LABELS: Record<NavigationGroupId, string> = {
  operacao: 'Operação',
  cadastros: 'Cadastros',
  administracao: 'Administração',
};

export const NAVIGATION_ITEMS: NavigationItem[] = [
  {
    id: 'dashboard',
    label: 'Dashboard',
    description: 'Visão resumida das operações do dia',
    group: 'operacao',
    icon: HomeIcon,
    to: '/dashboard',
    matchPaths: ['/dashboard', '/dashboard/operacao', '/dashboard/admin'],
    allowedRoles: [ROLES.ADMIN, ROLES.COLABORADOR],
  },
  {
    id: 'agendamentos',
    label: 'Agendamentos',
    description: 'Gerencie e acompanhe consultas',
    group: 'operacao',
    icon: CalendarDaysIcon,
    to: '/agendamentos',
    allowedRoles: [ROLES.ADMIN, ROLES.COLABORADOR],
  },
  {
    id: 'motoristas',
    label: 'Motoristas',
    description: 'Cadastre e gerencie motoristas',
    group: 'cadastros',
    icon: TruckIcon,
    to: '/cadastros/motoristas',
    allowedRoles: [ROLES.ADMIN, ROLES.COLABORADOR],
  },
  {
    id: 'coletoras',
    label: 'Coletoras',
    description: 'Cadastre e gerencie coletoras',
    group: 'cadastros',
    icon: UsersIcon,
    to: '/cadastros/coletoras',
    allowedRoles: [ROLES.ADMIN, ROLES.COLABORADOR],
  },
  {
    id: 'clientes',
    label: 'Clientes',
    description: 'Gerencie pacientes e históricos',
    group: 'cadastros',
    icon: UsersIcon,
    to: '/cadastros/clientes',
    allowedRoles: [ROLES.ADMIN, ROLES.COLABORADOR],
  },
  {
    id: 'carros',
    label: 'Carros',
    description: 'Gerencie a frota disponível',
    group: 'cadastros',
    icon: TruckIcon,
    to: '/cadastros/carros',
    allowedRoles: [ROLES.ADMIN, ROLES.COLABORADOR],
  },
  {
    id: 'pacotes',
    label: 'Pacotes',
    description: 'Monte combinações completas de logística',
    group: 'cadastros',
    icon: Squares2X2Icon,
    to: '/cadastros/pacotes',
    allowedRoles: [ROLES.ADMIN, ROLES.COLABORADOR],
  },
  {
    id: 'usuarios',
    label: 'Usuários',
    description: 'Gestão de contas e permissões',
    group: 'administracao',
    icon: UserIcon,
    to: '/admin/usuarios',
    allowedRoles: [ROLES.ADMIN],
  },
  {
    id: 'tags',
    label: 'Tags',
    description: 'Categorize e organize atendimentos',
    group: 'administracao',
    icon: TagIcon,
    to: '/admin/tags',
    allowedRoles: [ROLES.ADMIN],
  },
];

export function getNavigationItemsByRole(role: Role | null): NavigationItem[] {
  if (!role) {
    return [];
  }

  return NAVIGATION_ITEMS.filter((item) => item.allowedRoles.includes(role));
}
