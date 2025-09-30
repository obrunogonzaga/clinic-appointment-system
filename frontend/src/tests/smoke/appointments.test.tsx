import assert from 'node:assert/strict';
import { randomUUID } from 'node:crypto';
import { describe, test } from 'node:test';
import React from 'react';
import { renderToStaticMarkup } from 'react-dom/server';
import { AppointmentFormModal } from '../../components/AppointmentFormModal';
import { Modal } from '../../components/ui/Modal';
import { ViewModeToggle } from '../../components/ViewModeToggle';
import {
  appointmentQueryKeys,
  sanitizeUpdatePayload,
} from '../../hooks/useAppointmentDetails';
import {
  filterAppointmentsBySearch,
  filterAppointmentsByDateRange,
  getDateRangeForShortcut,
  toAppointmentViewModel,
} from '../../utils/appointmentViewModel';
import type { Appointment } from '../../types/appointment';

const buildAppointment = (overrides: Partial<Appointment> = {}): Appointment => ({
  id: overrides.id ?? randomUUID(),
  nome_marca: overrides.nome_marca ?? 'Marca X',
  nome_unidade: overrides.nome_unidade ?? 'Unidade Centro',
  nome_paciente: overrides.nome_paciente ?? 'Maria Silva',
  data_agendamento: overrides.data_agendamento ?? new Date().toISOString(),
  hora_agendamento: overrides.hora_agendamento ?? '08:00',
  status: overrides.status ?? 'Confirmado',
  telefone: overrides.telefone,
  carro: overrides.carro,
  observacoes: overrides.observacoes,
  driver_id: overrides.driver_id,
  collector_id: overrides.collector_id,
  documento_completo: overrides.documento_completo,
  documento_normalizado: overrides.documento_normalizado,
  cpf: overrides.cpf,
  rg: overrides.rg,
  numero_convenio: overrides.numero_convenio,
  nome_convenio: overrides.nome_convenio,
  cep: overrides.cep,
  endereco_coleta: overrides.endereco_coleta,
  endereco_completo: overrides.endereco_completo,
  endereco_normalizado: overrides.endereco_normalizado,
  tipo_consulta: overrides.tipo_consulta,
  created_at: overrides.created_at ?? new Date().toISOString(),
  updated_at: overrides.updated_at,
});

describe('Appointments smoke tests', () => {
  test('Modal renders dialog markup when opened', () => {
    const markup = renderToStaticMarkup(
      <Modal isOpen onClose={() => undefined} title="Importar Excel">
        <p>Conteúdo</p>
      </Modal>
    );

    assert.ok(markup.includes('role="dialog"'));
    assert.ok(markup.includes('Importar Excel'));
  });

  test('ViewModeToggle marks the table option as active when selected', () => {
    const markup = renderToStaticMarkup(
      <ViewModeToggle viewMode="table" onViewChange={() => undefined} />
    );

    assert.ok(markup.includes('Lista'));
    assert.ok(markup.includes('aria-pressed="true"'));
  });

  test('AppointmentFormModal renders required inputs when opened', () => {
    const markup = renderToStaticMarkup(
      <AppointmentFormModal
        isOpen
        onClose={() => undefined}
        onSubmit={async () => undefined}
        brands={['Marca X']}
        units={['Unidade Centro']}
        statuses={['Confirmado', 'Pendente']}
        drivers={[]}
        collectors={[]}
        tags={[]}
        maxTags={5}
      />
    );

    assert.ok(markup.includes('Adicionar Agendamento'));
    assert.ok(markup.includes('name="nome_paciente"'));
    assert.ok(markup.includes('name="cpf"'));
    assert.ok(markup.includes('Confirmado'));
  });

  test('filterAppointmentsBySearch finds matches by CPF digits and name', () => {
    const appointments = [
      toAppointmentViewModel(buildAppointment({
        id: '1',
        nome_paciente: 'João Pereira',
        cpf: '12345678901',
      })),
      toAppointmentViewModel(buildAppointment({
        id: '2',
        nome_paciente: 'Ana Clara',
        cpf: '98765432100',
      })),
    ];

    const byName = filterAppointmentsBySearch(appointments, 'ana');
    assert.equal(byName.length, 1);
    assert.equal(byName[0].id, '2');

    const byCpf = filterAppointmentsBySearch(appointments, '6789');
    assert.equal(byCpf.length, 1);
    assert.equal(byCpf[0].id, '1');
  });

  test('filterAppointmentsByDateRange keeps appointments within shortcut range', () => {
    const today = new Date();
    const nextWeek = new Date();
    nextWeek.setDate(today.getDate() + 8);

    const appointments = [
      toAppointmentViewModel(buildAppointment({ id: 'today', data_agendamento: today.toISOString() })),
      toAppointmentViewModel(buildAppointment({ id: 'next', data_agendamento: nextWeek.toISOString() })),
    ];

    const thisWeekRange = getDateRangeForShortcut('thisWeek');
    const filtered = filterAppointmentsByDateRange(appointments, thisWeekRange);

    assert.equal(filtered.length, 1);
    assert.equal(filtered[0].id, 'today');
  });

  test('sanitizeUpdatePayload removes undefined keys but keeps nullish values', () => {
    const payload = sanitizeUpdatePayload({
      status: 'Confirmado',
      telefone: undefined,
      observacoes: null,
    });

    assert.deepEqual(payload, {
      status: 'Confirmado',
      observacoes: null,
    });
  });

  test('appointmentQueryKeys.detail produces scoped cache keys', () => {
    const key = appointmentQueryKeys.detail('abc');
    assert.deepEqual(key, ['appointments', 'detail', 'abc']);
  });
});
