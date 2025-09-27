import type React from 'react';
import { ROLES, type Role } from '../constants/roles';
import { AppointmentsPage } from '../pages/AppointmentsPage';
import { CarsPage } from '../pages/CarsPage';
import { CollectorsPage } from '../pages/CollectorsPage';
import { ClientsPage } from '../pages/ClientsPage';
import AdminDashboardPage from '../pages/dashboard/AdminDashboardPage';
import OperationDashboardPage from '../pages/dashboard/OperationDashboardPage';
import { DriversPage } from '../pages/DriversPage';
import { LogisticsPackagesPage } from '../pages/LogisticsPackagesPage';
import { TagsPage } from '../pages/TagsPage';
import { UsersPage } from '../pages/UsersPage';

export interface AppRoute {
  id: string;
  path: string;
  Component: React.ComponentType;
  allowedRoles: Role[];
  breadcrumb: string[];
}

export const APP_ROUTES: AppRoute[] = [
  {
    id: 'dashboard-operation',
    path: '/dashboard/operacao',
    Component: OperationDashboardPage,
    allowedRoles: [ROLES.ADMIN, ROLES.COLABORADOR],
    breadcrumb: ['Operação', 'Dashboard'],
  },
  {
    id: 'dashboard-admin',
    path: '/dashboard/admin',
    Component: AdminDashboardPage,
    allowedRoles: [ROLES.ADMIN],
    breadcrumb: ['Administração', 'Dashboard'],
  },
  {
    id: 'appointments',
    path: '/agendamentos',
    Component: AppointmentsPage,
    allowedRoles: [ROLES.ADMIN, ROLES.COLABORADOR],
    breadcrumb: ['Operação', 'Agendamentos'],
  },
  {
    id: 'drivers',
    path: '/cadastros/motoristas',
    Component: DriversPage,
    allowedRoles: [ROLES.ADMIN, ROLES.COLABORADOR],
    breadcrumb: ['Cadastros', 'Motoristas'],
  },
  {
    id: 'collectors',
    path: '/cadastros/coletoras',
    Component: CollectorsPage,
    allowedRoles: [ROLES.ADMIN, ROLES.COLABORADOR],
    breadcrumb: ['Cadastros', 'Coletoras'],
  },
  {
    id: 'clients',
    path: '/cadastros/clientes',
    Component: ClientsPage,
    allowedRoles: [ROLES.ADMIN, ROLES.COLABORADOR],
    breadcrumb: ['Cadastros', 'Clientes'],
  },
  {
    id: 'cars',
    path: '/cadastros/carros',
    Component: CarsPage,
    allowedRoles: [ROLES.ADMIN, ROLES.COLABORADOR],
    breadcrumb: ['Cadastros', 'Carros'],
  },
  {
    id: 'packages',
    path: '/cadastros/pacotes',
    Component: LogisticsPackagesPage,
    allowedRoles: [ROLES.ADMIN, ROLES.COLABORADOR],
    breadcrumb: ['Cadastros', 'Pacotes'],
  },
  {
    id: 'users',
    path: '/admin/usuarios',
    Component: UsersPage,
    allowedRoles: [ROLES.ADMIN],
    breadcrumb: ['Administração', 'Usuários'],
  },
  {
    id: 'tags',
    path: '/admin/tags',
    Component: TagsPage,
    allowedRoles: [ROLES.ADMIN],
    breadcrumb: ['Administração', 'Tags'],
  },
];
