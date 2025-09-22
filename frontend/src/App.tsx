import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { useState } from 'react';
import { HashRouter, Route, Routes } from 'react-router-dom';
import { Navigation } from './components/Navigation';
import { AppointmentsPage } from './pages/AppointmentsPage';
import { CarsPage } from './pages/CarsPage';
import { CollectorsPage } from './pages/CollectorsPage';
import { Dashboard } from './pages/Dashboard';
import { DriverRoutePage } from './pages/DriverRoutePage';
import { DriversPage } from './pages/DriversPage';

// Create a client
const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      retry: 1,
      staleTime: 5 * 60 * 1000, // 5 minutes
    },
  },
});

function Shell() {
  const [activeTab, setActiveTab] = useState('dashboard');
  const renderContent = () => {
    switch (activeTab) {
      case 'dashboard':
        return <Dashboard onTabChange={setActiveTab} />;
      case 'appointments':
        return <AppointmentsPage />;
      case 'drivers':
        return <DriversPage />;
      case 'collectors':
        return <CollectorsPage />;
      case 'cars':
        return <CarsPage />;
      default:
        return <Dashboard onTabChange={setActiveTab} />;
    }
  };
  return (
    <div className="min-h-screen bg-gray-50 flex">
      <Navigation activeTab={activeTab} onTabChange={setActiveTab} />
      <main className="flex-1 p-8">{renderContent()}</main>
    </div>
  );
}

function App() {
  return (
    <QueryClientProvider client={queryClient}>
      <HashRouter>
        <Routes>
          <Route path="/routes/driver" element={<DriverRoutePage />} />
          <Route path="*" element={<Shell />} />
        </Routes>
      </HashRouter>
    </QueryClientProvider>
  );
}

export default App;