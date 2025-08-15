import { useState, useEffect } from 'react';

export type Breakpoint = 'mobile' | 'tablet' | 'desktop' | 'wide';

interface ResponsiveLayout {
  isMobile: boolean;
  isTablet: boolean;
  isDesktop: boolean;
  isWide: boolean;
  breakpoint: Breakpoint;
}

export const useResponsiveLayout = (): ResponsiveLayout => {
  const [breakpoint, setBreakpoint] = useState<Breakpoint>('desktop');

  useEffect(() => {
    const checkBreakpoint = () => {
      const width = window.innerWidth;
      
      if (width < 768) {
        setBreakpoint('mobile');
      } else if (width < 1024) {
        setBreakpoint('tablet');
      } else if (width < 1440) {
        setBreakpoint('desktop');
      } else {
        setBreakpoint('wide');
      }
    };

    // Check on mount
    checkBreakpoint();

    // Listen for resize events
    window.addEventListener('resize', checkBreakpoint);
    
    return () => {
      window.removeEventListener('resize', checkBreakpoint);
    };
  }, []);

  return {
    isMobile: breakpoint === 'mobile',
    isTablet: breakpoint === 'tablet',
    isDesktop: breakpoint === 'desktop',
    isWide: breakpoint === 'wide',
    breakpoint,
  };
};
