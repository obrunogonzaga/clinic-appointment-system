import { useQuery } from '@tanstack/react-query';
import React from 'react';
import { useSearchParams } from 'react-router-dom';
import { appointmentAPI, driverAPI } from '../services/api';
import type { Appointment } from '../types/appointment';
import { NavigationBar } from '../components/NavigationBar';
import { buildGoogleMapsNavTo, buildWazeNavTo, formatAddressForNavigation } from '../utils/navigationHelpers';

export const DriverRoutePage: React.FC = () => {
  const [params] = useSearchParams();
  const driverId = params.get('driverId') ?? '';
  const date = params.get('date') ?? new Date().toISOString().slice(0, 10);

  const { data: driverData } = useQuery({
    queryKey: ['driver', driverId],
    queryFn: () => driverAPI.getDriver(driverId),
    enabled: !!driverId,
  });

  const { data: appts } = useQuery({
    queryKey: ['appointments-driver-day', driverId, date],
    queryFn: async () => {
      // 1) Busca do dia PARA o motorista
      const withDriver = await appointmentAPI.getAppointments({
        data: date,
        driver_id: driverId,
        page: 1,
        page_size: 100,
      });
      if (withDriver.appointments.length > 0) {
        return withDriver.appointments;
      }
      // 2) Fallback: se não houver vinculação, busca todos do dia
      const anyDriver = await appointmentAPI.getAppointments({
        data: date,
        page: 1,
        page_size: 100,
      });
      return anyDriver.appointments;
    },
    enabled: !!driverId && !!date,
  });

  const driverName = driverData?.data?.nome_completo || '—';
  const dateLabel = new Date(date).toLocaleDateString('pt-BR');

  if (!driverId) {
    return <div className="p-8">Parâmetro driverId ausente.</div>;
  }

  const renderCard = (ap: Appointment) => {
    const addressForNav = formatAddressForNavigation(ap);
    
    return (
      <div key={ap.id} className="card relative bg-white border-2 border-gray-800 rounded-2xl p-6 shadow-sm overflow-hidden">
        {/* Faixa lateral */}
        <div className="absolute left-0 top-0 h-full w-3 bg-gray-900 rounded-l-2xl" />

        {/* Cabeçalho */}
        <div className="grid grid-cols-12 items-center gap-4">
          <div className="col-span-12 md:col-span-6 flex items-center gap-4">
            <div className="text-6xl md:text-7xl font-black text-gray-900 tabular-nums">
              {(() => {
                const time = ap.hora_agendamento;
                if (!time) {
                  return '--:--';
                }
                const match = time.match(/^(\d{2}:\d{2})/);
                return match ? match[1] : '--:--';
              })()}
            </div>
            <div className="hidden md:block h-10 w-px bg-gray-800" />
            <div className="flex flex-wrap gap-8 text-lg font-bold text-gray-900">
              <span>Previsão:</span>
              <span>Chegada:</span>
              <span>Saída:</span>
            </div>
          </div>
          <div className="col-span-12 md:col-span-6 flex justify-between items-center">
            <div className="flex gap-6 text-xl font-semibold text-gray-900">
              <label className="inline-flex items-center gap-2">
                <span className={`inline-block w-6 h-6 border-2 rounded-sm ${isNac(ap) ? 'bg-gray-900 border-gray-900' : 'border-gray-800'}`} /> NAC
              </label>
              <label className="inline-flex items-center gap-2">
                <span className={`inline-block w-6 h-6 border-2 rounded-sm ${!isNac(ap) ? 'bg-gray-900 border-gray-900' : 'border-gray-800'}`} /> Unidade
              </label>
            </div>
            {/* Mini-links de navegação */}
            <div className="flex gap-2 no-print">
              <a
                href={buildGoogleMapsNavTo(addressForNav)}
                target="_blank"
                rel="noopener noreferrer"
                className="px-2 py-1 text-xs font-medium rounded text-white bg-blue-600 hover:bg-blue-700 transition-colors"
              >
                Maps
              </a>
              <a
                href={buildWazeNavTo(addressForNav)}
                target="_blank"
                rel="noopener noreferrer"
                className="px-2 py-1 text-xs font-medium rounded text-white bg-purple-600 hover:bg-purple-700 transition-colors"
              >
                Waze
              </a>
            </div>
          </div>
        </div>
      <div className="my-4 border-b-2 border-gray-800" />

      {/* Linha: Nome / CIP / Telefones */}
      <div className="grid grid-cols-12 gap-6 items-end">
        <div className="col-span-12 md:col-span-6">
          <div className="text-xl font-extrabold text-gray-900">Nome:</div>
          <div className="border-b-2 border-gray-800 text-lg py-2 min-h-[2.25rem]">{ap.nome_paciente || '-'}</div>
        </div>
        <div className="col-span-6 md:col-span-3">
          <div className="text-xl font-extrabold text-gray-900">CIP:</div>
          <div className="border-b-2 border-gray-800 text-lg py-2 min-h-[2.25rem]">&nbsp;</div>
        </div>
        <div className="col-span-6 md:col-span-3">
          <div className="text-xl font-extrabold text-gray-900">Telefones:</div>
          <div className="border-b-2 border-gray-800 text-lg py-2 min-h-[2.25rem]">{formatPhone(ap.telefone)}</div>
        </div>
      </div>

      {/* Linha: CEP / Rua / Nº / Complemento */}
      <div className="grid grid-cols-12 gap-6 items-end mt-6">
        <div className="col-span-12 md:col-span-3">
          <div className="text-xl font-extrabold text-gray-900">CEP:</div>
          <div className="border-b-2 border-gray-800 text-lg py-2 min-h-[2.25rem]">
            {ap.endereco_normalizado?.cep || ap.cep || '-'}
          </div>
        </div>
        <div className="col-span-12 md:col-span-5">
          <div className="text-xl font-extrabold text-gray-900">Rua:</div>
          <div className="border-b-2 border-gray-800 text-lg py-2 min-h-[2.25rem]">
            {ap.endereco_normalizado?.rua || ap.endereco_coleta || '-'}
          </div>
        </div>
        <div className="col-span-6 md:col-span-2">
          <div className="text-xl font-extrabold text-gray-900">Nº:</div>
          <div className="border-b-2 border-gray-800 text-lg py-2 min-h-[2.25rem]">
            {ap.endereco_normalizado?.numero || '-'}
          </div>
        </div>
        <div className="col-span-6 md:col-span-2">
          <div className="text-xl font-extrabold text-gray-900">Complemento:</div>
          <div className="border-b-2 border-gray-800 text-lg py-2 min-h-[2.25rem]">
            {ap.endereco_normalizado?.complemento || '-'}
          </div>
        </div>
      </div>

      {/* Linha: Convênio / Pendências */}
      <div className="grid grid-cols-12 gap-6 items-end mt-6">
        <div className="col-span-12 md:col-span-6">
          <div className="text-xl font-extrabold text-gray-900">Convênio:</div>
          <div className="border-b-2 border-gray-800 text-lg py-2 min-h-[2.25rem]">
            {(ap.numero_convenio || ap.nome_convenio) ? `${ap.numero_convenio ?? ''}${ap.numero_convenio && ap.nome_convenio ? ' - ' : ''}${ap.nome_convenio ?? ''}` : '-'}
          </div>
        </div>
        <div className="col-span-12 md:col-span-6 flex items-center gap-6">
          <div className="text-xl font-extrabold text-gray-900">Pendências:</div>
          <label className="inline-flex items-center gap-2 text-xl text-gray-900">
            <span className="inline-block w-6 h-6 border-2 border-gray-800 rounded-sm" /> Guia
          </label>
          <label className="inline-flex items-center gap-2 text-xl text-gray-900">
            <span className="inline-block w-6 h-6 border-2 border-gray-800 rounded-sm" /> Token
          </label>
          <label className="inline-flex items-center gap-2 text-xl text-gray-900">
            <span className="inline-block w-6 h-6 border-2 border-gray-800 rounded-sm" /> Outro
          </label>
        </div>
      </div>

      {/* Carro */}
      <div className="grid grid-cols-12 gap-6 mt-6">
        <div className="col-span-12 md:col-span-6">
          <div className="text-xl font-extrabold text-gray-900">Carro</div>
          <div className="border-2 border-gray-800 rounded-md min-h-[150px] p-3 text-gray-800 whitespace-pre-wrap">
            {ap.carro || '-'}
          </div>
        </div>
        <div className="col-span-12 md:col-span-6">
          <div className="text-xl font-extrabold text-gray-900">Obs. Coleta</div>
          <div className="border-2 border-gray-800 rounded-md min-h-[150px] p-3 text-gray-800 whitespace-pre-wrap">{ap.tipo_consulta || '-'}</div>
        </div>
      </div>

      {/* Observações */}
      <div className="grid grid-cols-12 gap-6 mt-6">
        <div className="col-span-12">
          <div className="text-xl font-extrabold text-gray-900">Observações</div>
          <div className="border-2 border-gray-800 rounded-md min-h-[100px] p-3 text-gray-800 whitespace-pre-wrap">
            {ap.observacoes || '-'}
          </div>
        </div>
      </div>
    </div>
    );
  };

  // ordena horário
  const ordered = (appts || []).slice().sort((a, b) => {
    const normalizeTime = (value?: string | null): string => {
      if (!value || !value.trim()) {
        return '99:99';
      }
      return value;
    };

    const [ah, am] = normalizeTime(a.hora_agendamento).split(':').map(Number);
    const [bh, bm] = normalizeTime(b.hora_agendamento).split(':').map(Number);
    return ah === bh ? am - bm : ah - bh;
  });

  return (
    <div className="min-h-screen bg-gray-50">
      <NavigationBar appointments={ordered} />
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <div className="flex items-start justify-between">
          <div>
            <h1 className="text-3xl font-bold text-gray-900">Rota Domiciliar</h1>
            <p className="text-gray-600 mt-2">
              Motorista: <span className="font-medium text-gray-900">{driverName}</span> · Data:
              <span className="font-medium text-gray-900"> {dateLabel}</span>
            </p>
          </div>
          <div className="no-print flex gap-2">
            <button
              onClick={() => window.print()}
              className="px-3 py-2 text-sm font-medium rounded-md text-white bg-green-600 hover:bg-green-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-green-500"
            >
              Imprimir
            </button>
            <button
              onClick={() => window.close()}
              className="px-3 py-2 text-sm font-medium rounded-md text-gray-700 bg-white border border-gray-300 hover:bg-gray-50"
            >
              Fechar
            </button>
          </div>
        </div>
      </div>

      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 pb-10">
        {ordered.length === 0 ? (
          <div className="text-center py-20 bg-white border border-gray-200 rounded-xl">
            <p className="text-gray-600">Sem agendamentos para a data.</p>
          </div>
        ) : (
          <div className="space-y-4">
            {ordered.map(renderCard)}
          </div>
        )}
      </div>

      <style>{`
        @media print {
          .no-print { display: none; }
          .card { page-break-inside: avoid; }
          body { background: white; }
        }
      `}</style>
    </div>
  );
};

function formatPhone(raw?: string): string {
  if (!raw) return '-';
  const digits = raw.replace(/\D/g, '');
  if (digits.length === 10) {
    return `(${digits.slice(0, 2)}) ${digits.slice(2, 6)}-${digits.slice(6)}`;
  }
  if (digits.length === 11) {
    return `(${digits.slice(0, 2)}) ${digits.slice(2, 3)}${digits.slice(3, 7)}-${digits.slice(7)}`;
  }
  return raw;
}

function isNac(ap: Appointment): boolean {
  // Heurística: considerar NAC quando não há unidade definida ou quando marca contém NAC
  const marca = (ap.nome_marca || '').toLowerCase();
  const unidade = (ap.nome_unidade || '').toLowerCase();
  if (!unidade && marca) return true;
  return marca.includes('nac');
}

