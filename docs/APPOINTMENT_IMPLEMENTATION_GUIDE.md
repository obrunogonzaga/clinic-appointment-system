# 🚀 Guia de Implementação - Tela de Agendamentos

**Status:** 📝 Ready to Implement  
**Soluções:** Cards Responsivos + Calendário Interativo  
**Timeline:** 4 semanas (3 fases)

---

## 🎯 Quick Start

### Problemas → Soluções
```
❌ Scroll horizontal (11 colunas) → ✅ Cards responsivos
❌ Lista linear com paginação → ✅ Calendário interativo
```

### Breakpoints
```typescript
mobile: 320-767px   → Cards compactos
tablet: 768-1023px  → Cards normais  
desktop: 1024px+    → Tabela + Calendário
```

---

## 📋 FASE 1: Cards Responsivos (1-2 semanas)

### 1.1 Setup Base (2 dias)
```bash
# Breakpoints no tailwind.config.js
screens: {
  'mobile': '320px',
  'tablet': '768px', 
  'desktop': '1024px'
}
```

### 1.2 Hook Responsivo (1 dia)
```typescript
// hooks/useResponsiveLayout.ts
export const useResponsiveLayout = () => {
  const [breakpoint, setBreakpoint] = useState('desktop');
  
  useEffect(() => {
    const checkBreakpoint = () => {
      if (window.innerWidth < 768) setBreakpoint('mobile');
      else if (window.innerWidth < 1024) setBreakpoint('tablet');
      else setBreakpoint('desktop');
    };
    
    checkBreakpoint();
    window.addEventListener('resize', checkBreakpoint);
    return () => window.removeEventListener('resize', checkBreakpoint);
  }, []);
  
  return {
    isMobile: breakpoint === 'mobile',
    isTablet: breakpoint === 'tablet', 
    isDesktop: breakpoint === 'desktop',
    breakpoint
  };
};
```

### 1.3 AppointmentCard (3 dias)
```typescript
// components/AppointmentCard.tsx
interface AppointmentCardProps {
  appointment: Appointment;
  drivers: ActiveDriver[];
  onStatusChange: (id: string, status: string) => void;
  onDriverChange: (id: string, driverId: string) => void;
  onDelete: (id: string) => void;
  compact?: boolean;
}

export const AppointmentCard = ({ appointment, compact, ... }) => {
  const statusColor = getStatusColor(appointment.status);
  
  return (
    <div className={`
      bg-white border rounded-lg shadow-sm p-4
      ${compact ? 'p-3' : 'p-4'}
      hover:shadow-md transition-shadow
    `}>
      {/* Header */}
      <div className="flex justify-between items-start mb-3">
        <h3 className="font-medium text-gray-900">
          {appointment.nome_paciente}
        </h3>
        <StatusSelect 
          value={appointment.status}
          onChange={(status) => onStatusChange(appointment.id, status)}
          className={statusColor}
        />
      </div>
      
      {/* Body */}
      <div className="space-y-2 text-sm text-gray-600">
        <div className="flex items-center">
          <CalendarIcon className="w-4 h-4 mr-2" />
          {formatDate(appointment.data_agendamento)} às {appointment.hora_agendamento}
        </div>
        
        <div className="flex items-center">
          <BuildingOfficeIcon className="w-4 h-4 mr-2" />
          {appointment.nome_unidade}
        </div>
        
        <div className="flex items-center">
          <TruckIcon className="w-4 h-4 mr-2" />
          {appointment.nome_marca}
        </div>
        
        {!compact && (
          <>
            {appointment.telefone && (
              <div className="flex items-center">
                <PhoneIcon className="w-4 h-4 mr-2" />
                {appointment.telefone}
              </div>
            )}
          </>
        )}
      </div>
      
      {/* Footer */}
      <div className="flex justify-between items-center mt-4 pt-3 border-t">
        <DriverSelect
          value={appointment.driver_id}
          drivers={drivers}
          onChange={(driverId) => onDriverChange(appointment.id, driverId)}
        />
        
        <button
          onClick={() => onDelete(appointment.id)}
          className="p-1 text-red-600 hover:text-red-800"
        >
          <TrashIcon className="w-4 h-4" />
        </button>
      </div>
    </div>
  );
};
```

### 1.4 ViewMode Toggle (1 dia)
```typescript
// components/ViewModeToggle.tsx
type ViewMode = 'table' | 'cards' | 'calendar';

export const ViewModeToggle = ({ viewMode, onViewChange }) => {
  const { isMobile } = useResponsiveLayout();
  
  // Auto-hide table option on mobile
  const availableModes = isMobile 
    ? ['cards', 'calendar'] 
    : ['table', 'cards', 'calendar'];
    
  return (
    <div className="flex bg-gray-100 rounded-lg p-1">
      {availableModes.map(mode => (
        <button
          key={mode}
          onClick={() => onViewChange(mode)}
          className={`
            px-3 py-2 rounded-md text-sm font-medium transition-all
            ${viewMode === mode 
              ? 'bg-white text-gray-900 shadow-sm' 
              : 'text-gray-600 hover:text-gray-900'
            }
          `}
        >
          {mode === 'table' && <ListBulletIcon className="w-4 h-4" />}
          {mode === 'cards' && <Squares2X2Icon className="w-4 h-4" />}
          {mode === 'calendar' && <CalendarIcon className="w-4 h-4" />}
          <span className="ml-2 capitalize">{mode}</span>
        </button>
      ))}
    </div>
  );
};
```

### 1.5 Integração (1 dia)
```typescript
// Modificar AppointmentsPage.tsx
export const AppointmentsPage = () => {
  const [viewMode, setViewMode] = useState<ViewMode>('table');
  const { isMobile, isTablet } = useResponsiveLayout();
  
  // Auto-switch para cards em mobile
  useEffect(() => {
    if (isMobile && viewMode === 'table') {
      setViewMode('cards');
    }
  }, [isMobile, viewMode]);
  
  const renderContent = () => {
    switch (viewMode) {
      case 'cards':
        return (
          <div className={`
            grid gap-4
            ${isMobile ? 'grid-cols-1' : 'grid-cols-2 lg:grid-cols-3'}
          `}>
            {appointments.map(appointment => (
              <AppointmentCard
                key={appointment.id}
                appointment={appointment}
                compact={isMobile}
                drivers={drivers}
                onStatusChange={handleStatusChange}
                onDriverChange={handleDriverChange}
                onDelete={handleDelete}
              />
            ))}
          </div>
        );
      case 'table':
      default:
        return <AppointmentTable {...tableProps} />;
    }
  };
  
  return (
    <div className="space-y-6">
      {/* Header with View Toggle */}
      <div className="flex justify-between items-center">
        <h1>Gerenciamento de Agendamentos</h1>
        <ViewModeToggle viewMode={viewMode} onViewChange={setViewMode} />
      </div>
      
      <AppointmentFilters {...filterProps} />
      
      <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
        {renderContent()}
      </div>
    </div>
  );
};
```

**✅ Entrega Fase 1:** Zero scroll horizontal + Cards funcionais

---

## 📋 FASE 2: Calendário (2 semanas)

### 2.1 Date Navigation Hook (2 dias)
```typescript
// hooks/useDateNavigation.ts
export const useDateNavigation = () => {
  const [currentDate, setCurrentDate] = useState(new Date());
  const [calendarView, setCalendarView] = useState<'month' | 'week' | 'day'>('month');
  
  const navigateToToday = () => setCurrentDate(new Date());
  const navigatePrevious = () => {
    const newDate = new Date(currentDate);
    if (calendarView === 'month') {
      newDate.setMonth(newDate.getMonth() - 1);
    } else if (calendarView === 'week') {
      newDate.setDate(newDate.getDate() - 7);
    } else {
      newDate.setDate(newDate.getDate() - 1);
    }
    setCurrentDate(newDate);
  };
  
  const navigateNext = () => {
    // Similar logic for next
  };
  
  return {
    currentDate,
    calendarView,
    setCalendarView,
    navigateToToday,
    navigatePrevious,
    navigateNext,
    setCurrentDate
  };
};
```

### 2.2 Quick Date Filters (1 dia)
```typescript
// components/QuickDateFilters.tsx
export const QuickDateFilters = ({ onFilterChange }) => {
  const quickFilters = [
    { key: 'today', label: 'Hoje', value: new Date() },
    { key: 'tomorrow', label: 'Amanhã', value: addDays(new Date(), 1) },
    { key: 'this-week', label: 'Esta Semana', value: startOfWeek(new Date()) },
    { key: 'next-week', label: 'Próx. Semana', value: startOfWeek(addWeeks(new Date(), 1)) }
  ];
  
  return (
    <div className="flex flex-wrap gap-2">
      {quickFilters.map(filter => (
        <button
          key={filter.key}
          onClick={() => onFilterChange(filter.value)}
          className="px-3 py-1 text-sm bg-blue-50 text-blue-700 rounded-full hover:bg-blue-100"
        >
          {filter.label}
        </button>
      ))}
    </div>
  );
};
```

### 2.3 Calendar Component (5 dias)
```typescript
// components/AppointmentCalendar.tsx
export const AppointmentCalendar = ({ appointments, filters }) => {
  const { currentDate, calendarView, navigatePrevious, navigateNext } = useDateNavigation();
  
  const groupedAppointments = useMemo(() => {
    return appointments.reduce((acc, appointment) => {
      const date = format(new Date(appointment.data_agendamento), 'yyyy-MM-dd');
      acc[date] = acc[date] || [];
      acc[date].push(appointment);
      return acc;
    }, {} as Record<string, Appointment[]>);
  }, [appointments]);
  
  const renderMonthView = () => {
    const startDate = startOfMonth(currentDate);
    const endDate = endOfMonth(currentDate);
    const days = eachDayOfInterval({ start: startDate, end: endDate });
    
    return (
      <div className="grid grid-cols-7 gap-1">
        {/* Header */}
        {['Dom', 'Seg', 'Ter', 'Qua', 'Qui', 'Sex', 'Sáb'].map(day => (
          <div key={day} className="p-2 text-center text-sm font-medium text-gray-500">
            {day}
          </div>
        ))}
        
        {/* Days */}
        {days.map(day => {
          const dateKey = format(day, 'yyyy-MM-dd');
          const dayAppointments = groupedAppointments[dateKey] || [];
          
          return (
            <CalendarDay
              key={dateKey}
              date={day}
              appointments={dayAppointments}
              onClick={() => onDayClick(day)}
              isToday={isSameDay(day, new Date())}
              isSelected={isSameDay(day, currentDate)}
            />
          );
        })}
      </div>
    );
  };
  
  return (
    <div className="bg-white rounded-lg border">
      {/* Calendar Header */}
      <div className="flex justify-between items-center p-4 border-b">
        <h2 className="text-lg font-semibold">
          {format(currentDate, 'MMMM yyyy', { locale: ptBR })}
        </h2>
        
        <div className="flex items-center space-x-2">
          <button onClick={navigatePrevious}>
            <ChevronLeftIcon className="w-5 h-5" />
          </button>
          <button onClick={navigateNext}>
            <ChevronRightIcon className="w-5 h-5" />
          </button>
        </div>
      </div>
      
      {/* Calendar Body */}
      <div className="p-4">
        {calendarView === 'month' && renderMonthView()}
        {calendarView === 'week' && renderWeekView()}
        {calendarView === 'day' && renderDayView()}
      </div>
    </div>
  );
};
```

### 2.4 Calendar Day Component (2 dias)
```typescript
// components/CalendarDay.tsx
export const CalendarDay = ({ date, appointments, onClick, isToday, isSelected }) => {
  const appointmentsByStatus = appointments.reduce((acc, apt) => {
    acc[apt.status] = (acc[apt.status] || 0) + 1;
    return acc;
  }, {} as Record<string, number>);
  
  return (
    <div
      onClick={() => onClick(date)}
      className={`
        p-2 min-h-[80px] border border-gray-200 cursor-pointer
        hover:bg-blue-50 transition-colors
        ${isToday ? 'bg-blue-100 border-blue-300' : ''}
        ${isSelected ? 'bg-blue-200' : ''}
      `}
    >
      {/* Date number */}
      <div className={`text-sm font-medium mb-1 ${isToday ? 'text-blue-700' : 'text-gray-900'}`}>
        {format(date, 'd')}
      </div>
      
      {/* Appointment indicators */}
      {appointments.length > 0 && (
        <div className="space-y-1">
          {Object.entries(appointmentsByStatus).map(([status, count]) => (
            <div
              key={status}
              className={`
                text-xs px-1 py-0.5 rounded text-center
                ${getStatusColor(status)}
              `}
            >
              {count}
            </div>
          ))}
        </div>
      )}
    </div>
  );
};
```

**✅ Entrega Fase 2:** Calendário funcional + Navegação por datas

---

## 📋 FASE 3: Polimento (1 semana)

### 3.1 Performance (2 dias)
```typescript
// Virtualization para listas grandes
import { FixedSizeList as List } from 'react-window';

// Memoization
const MemoizedAppointmentCard = React.memo(AppointmentCard);
const MemoizedCalendarDay = React.memo(CalendarDay);

// Lazy loading
const AppointmentCalendar = lazy(() => import('./AppointmentCalendar'));
```

### 3.2 Loading States (1 dia)
```typescript
// components/LoadingStates.tsx
export const CardSkeleton = () => (
  <div className="bg-white border rounded-lg p-4 animate-pulse">
    <div className="h-4 bg-gray-200 rounded mb-3"></div>
    <div className="space-y-2">
      <div className="h-3 bg-gray-200 rounded w-3/4"></div>
      <div className="h-3 bg-gray-200 rounded w-1/2"></div>
    </div>
  </div>
);

export const CalendarSkeleton = () => (
  <div className="bg-white rounded-lg border p-4 animate-pulse">
    <div className="h-6 bg-gray-200 rounded mb-4"></div>
    <div className="grid grid-cols-7 gap-1">
      {Array.from({ length: 35 }).map((_, i) => (
        <div key={i} className="h-20 bg-gray-200 rounded"></div>
      ))}
    </div>
  </div>
);
```

### 3.3 Error States (1 dia)
```typescript
// components/ErrorBoundary.tsx
export const AppointmentErrorBoundary = ({ children }) => {
  return (
    <ErrorBoundary
      fallback={
        <div className="text-center py-12">
          <ExclamationTriangleIcon className="w-12 h-12 text-red-500 mx-auto mb-4" />
          <h3 className="text-lg font-medium text-gray-900 mb-2">
            Erro ao carregar agendamentos
          </h3>
          <p className="text-gray-600 mb-4">
            Tente recarregar a página ou entre em contato com o suporte.
          </p>
          <button 
            onClick={() => window.location.reload()}
            className="bg-blue-600 text-white px-4 py-2 rounded-md hover:bg-blue-700"
          >
            Recarregar
          </button>
        </div>
      }
    >
      {children}
    </ErrorBoundary>
  );
};
```

### 3.4 Animations (1 dia)
```typescript
// Adicionar transições suaves
const slideIn = {
  initial: { opacity: 0, x: -20 },
  animate: { opacity: 1, x: 0 },
  exit: { opacity: 0, x: 20 }
};

const fadeIn = {
  initial: { opacity: 0 },
  animate: { opacity: 1 },
  transition: { duration: 0.2 }
};
```

**✅ Entrega Fase 3:** UX polida + Performance otimizada

---

## 📦 Utilities & Helpers

### Status Colors
```typescript
// utils/statusColors.ts
export const getStatusColor = (status: string) => {
  const colors = {
    'Confirmado': 'bg-green-50 text-green-700 border-green-200',
    'Cancelado': 'bg-red-50 text-red-700 border-red-200', 
    'Reagendado': 'bg-yellow-50 text-yellow-700 border-yellow-200',
    'Concluído': 'bg-blue-50 text-blue-700 border-blue-200',
    'Não Compareceu': 'bg-gray-50 text-gray-700 border-gray-200'
  };
  return colors[status] || colors['Não Compareceu'];
};
```

### Date Formatting
```typescript
// utils/dateUtils.ts
export const formatDate = (dateString: string) => {
  const date = new Date(dateString);
  return format(date, 'dd/MM/yyyy');
};

export const formatDateTime = (dateString: string, timeString: string) => {
  return `${formatDate(dateString)} às ${timeString}`;
};
```

---

## ✅ Checklist Final

### Fase 1 - Cards
- [ ] Hook `useResponsiveLayout` criado
- [ ] `AppointmentCard` implementado
- [ ] `ViewModeToggle` funcionando
- [ ] Auto-switch mobile → cards
- [ ] Zero scroll horizontal

### Fase 2 - Calendário  
- [ ] Hook `useDateNavigation` criado
- [ ] `QuickDateFilters` implementado
- [ ] `AppointmentCalendar` com month/week/day views
- [ ] `CalendarDay` com indicadores de status
- [ ] Navegação entre datas funcionando

### Fase 3 - Polimento
- [ ] Loading states implementados
- [ ] Error boundaries adicionados
- [ ] Performance otimizada
- [ ] Animações suaves

---

**🎯 Resultado:** Interface moderna, responsiva e user-friendly para gestão de agendamentos.
