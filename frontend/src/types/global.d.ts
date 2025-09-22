/**
 * Global type definitions for runtime configuration
 */

declare global {
  interface Window {
    ENV?: {
      API_URL: string;
    };
  }
}

export {};