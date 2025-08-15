/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      screens: {
        'mobile': '320px',
        'tablet': '768px', 
        'desktop': '1024px',
        'wide': '1440px',
      },
      colors: {
        status: {
          confirmed: {
            50: '#D1FAE5',
            700: '#047857',
            DEFAULT: '#10B981'
          },
          cancelled: {
            50: '#FEE2E2', 
            700: '#B91C1C',
            DEFAULT: '#EF4444'
          },
          rescheduled: {
            50: '#FEF3C7',
            700: '#B45309', 
            DEFAULT: '#F59E0B'
          },
          completed: {
            50: '#DBEAFE',
            700: '#1D4ED8',
            DEFAULT: '#3B82F6'
          },
          'no-show': {
            50: '#F3F4F6',
            700: '#374151',
            DEFAULT: '#6B7280'
          }
        }
      }
    },
  },
  plugins: [
    require('@tailwindcss/forms'),
  ],
}