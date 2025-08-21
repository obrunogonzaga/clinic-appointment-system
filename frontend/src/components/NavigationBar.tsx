import React from 'react';
import type { Appointment } from '../types/appointment';
import {
  buildGoogleMapsDirUrl,
  buildGoogleMapsNavTo,
  buildWazeNavTo,
  getNextStop,
  getWaypointsForRoute,
  getFinalDestination,
  formatAddressForNavigation,
  ORIGIN_ADDRESS
} from '../utils/navigationHelpers';

interface NavigationBarProps {
  appointments: Appointment[];
}

export const NavigationBar: React.FC<NavigationBarProps> = ({ appointments }) => {
  const nextStop = getNextStop(appointments);
  const nextStopAddress = nextStop ? formatAddressForNavigation(nextStop) : '';

  const handleCompleteRoute = () => {
    if (appointments.length === 0) return;
    
    const waypoints = getWaypointsForRoute(appointments);
    const finalDestination = getFinalDestination(appointments);
    
    const url = buildGoogleMapsDirUrl(ORIGIN_ADDRESS, finalDestination, waypoints);
    window.open(url, '_blank', 'noopener,noreferrer');
  };

  const handleGoogleMapsNext = () => {
    if (!nextStopAddress) return;
    
    const url = buildGoogleMapsNavTo(nextStopAddress);
    window.open(url, '_blank', 'noopener,noreferrer');
  };

  const handleWazeNext = () => {
    if (!nextStopAddress) return;
    
    const url = buildWazeNavTo(nextStopAddress);
    window.open(url, '_blank', 'noopener,noreferrer');
  };

  if (appointments.length === 0) return null;

  return (
    <div className="sticky top-0 z-50 bg-white border-b-2 border-gray-800 shadow-sm no-print">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-4">
        <div className="flex flex-wrap gap-3 justify-center items-center">
          <button
            onClick={handleCompleteRoute}
            className="inline-flex items-center px-4 py-2 text-sm font-medium rounded-md text-white bg-blue-600 hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500 transition-colors"
          >
            <span className="mr-2">📍</span>
            Google Maps (Rota Completa)
          </button>
          
          <button
            onClick={handleGoogleMapsNext}
            disabled={!nextStop}
            className="inline-flex items-center px-4 py-2 text-sm font-medium rounded-md text-white bg-green-600 hover:bg-green-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-green-500 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
          >
            <span className="mr-2">🗺️</span>
            Google Maps (Próxima)
          </button>
          
          <button
            onClick={handleWazeNext}
            disabled={!nextStop}
            className="inline-flex items-center px-4 py-2 text-sm font-medium rounded-md text-white bg-purple-600 hover:bg-purple-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-purple-500 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
          >
            <span className="mr-2">🚗</span>
            Waze (Próxima)
          </button>
        </div>
        
        {nextStop && (
          <div className="mt-2 text-center text-sm text-gray-600">
            <strong>Próxima parada:</strong> {nextStop.hora_agendamento} - {nextStop.nome_paciente}
          </div>
        )}
      </div>
    </div>
  );
};