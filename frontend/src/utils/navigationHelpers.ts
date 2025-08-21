import type { Appointment } from '../types/appointment';

/**
 * Formatar endereço do appointment para navegação
 */
export function formatAddressForNavigation(appointment: Appointment): string {
  const endereco = appointment.endereco_normalizado;
  
  if (endereco) {
    // Usar endereço normalizado se disponível
    const parts = [
      endereco.rua,
      endereco.numero,
      endereco.complemento,
      endereco.bairro,
      endereco.cidade,
      endereco.estado,
      endereco.cep
    ].filter(Boolean);
    
    return parts.join(', ');
  }
  
  // Fallback para campos originais
  const parts = [
    appointment.endereco_coleta,
    appointment.cep
  ].filter(Boolean);
  
  return parts.join(', ') || 'Endereço não disponível';
}

/**
 * Gerar URL do Google Maps para rota completa com origem, destino e waypoints
 */
export function buildGoogleMapsDirUrl(
  originAddress: string,
  destinationAddress: string,
  waypointAddresses: string[]
): string {
  const baseUrl = 'https://www.google.com/maps/dir/';
  
  // Monta a lista de pontos: origem + waypoints + destino
  const allPoints = [
    originAddress,
    ...waypointAddresses,
    destinationAddress
  ];
  
  // Codifica cada endereço
  const encodedPoints = allPoints.map(addr => encodeURIComponent(addr));
  
  return baseUrl + encodedPoints.join('/');
}

/**
 * Gerar URL do Google Maps para navegar diretamente para um endereço
 */
export function buildGoogleMapsNavTo(address: string): string {
  const encodedAddress = encodeURIComponent(address);
  return `https://www.google.com/maps/dir/?api=1&destination=${encodedAddress}`;
}

/**
 * Gerar URL do Waze para navegar diretamente para um endereço
 */
export function buildWazeNavTo(address: string): string {
  const encodedAddress = encodeURIComponent(address);
  return `https://www.waze.com/ul?navigate=yes&q=${encodedAddress}`;
}

/**
 * Obter a próxima parada na rota (primeira appointment ordenada por horário)
 */
export function getNextStop(appointments: Appointment[]): Appointment | null {
  if (appointments.length === 0) return null;
  
  // Ordena por horário e retorna a primeira
  const ordered = appointments.slice().sort((a, b) => {
    const [ah, am] = (a.hora_agendamento || '00:00').split(':').map(Number);
    const [bh, bm] = (b.hora_agendamento || '00:00').split(':').map(Number);
    return ah === bh ? am - bm : ah - bh;
  });
  
  return ordered[0];
}

/**
 * Gerar lista de waypoints para rota completa (todos os endereços exceto o último)
 */
export function getWaypointsForRoute(appointments: Appointment[]): string[] {
  if (appointments.length <= 1) return [];
  
  // Ordena por horário
  const ordered = appointments.slice().sort((a, b) => {
    const [ah, am] = (a.hora_agendamento || '00:00').split(':').map(Number);
    const [bh, bm] = (b.hora_agendamento || '00:00').split(':').map(Number);
    return ah === bh ? am - bm : ah - bh;
  });
  
  // Retorna todos exceto o último (que será o destino)
  return ordered.slice(0, -1).map(formatAddressForNavigation);
}

/**
 * Obter endereço de destino final (último appointment da rota)
 */
export function getFinalDestination(appointments: Appointment[]): string {
  if (appointments.length === 0) return '';
  
  // Ordena por horário e retorna o último
  const ordered = appointments.slice().sort((a, b) => {
    const [ah, am] = (a.hora_agendamento || '00:00').split(':').map(Number);
    const [bh, bm] = (b.hora_agendamento || '00:00').split(':').map(Number);
    return ah === bh ? am - bm : ah - bh;
  });
  
  return formatAddressForNavigation(ordered[ordered.length - 1]);
}

/**
 * Constante da origem fixa
 */
export const ORIGIN_ADDRESS = 'Av. das Américas, 10101 - Barra da Tijuca, Rio de Janeiro - RJ, 22790-000 (Aventura Center)';