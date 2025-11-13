/**
 * TypeScript definitions for Chatwoot SDK
 */

interface ChatwootSDKConfig {
  websiteToken: string;
  baseUrl: string;
  position?: 'left' | 'right';
  locale?: string;
  type?: 'standard' | 'expanded_bubble';
  launcherTitle?: string;
  showPopoutButton?: boolean;
  darkMode?: 'light' | 'auto';
}

interface ChatwootUser {
  email?: string;
  name?: string;
  phone_number?: string;
  avatar_url?: string;
  identifier_hash?: string;
}

interface ChatwootAPI {
  toggle: (state: 'open' | 'close') => void;
  setUser: (identifier: string, user: ChatwootUser) => void;
  setCustomAttributes: (attributes: Record<string, unknown>) => void;
  deleteCustomAttribute: (attributeName: string) => void;
  setLabel: (label: string) => void;
  removeLabel: (label: string) => void;
  setLocale: (locale: string) => void;
  reset: () => void;
}

interface ChatwootSDK {
  run: (config: ChatwootSDKConfig) => void;
}

interface Window {
  chatwootSDK?: ChatwootSDK;
  $chatwoot?: ChatwootAPI;
  chatwootSettings?: Partial<ChatwootSDKConfig>;
}

// Augment ImportMeta for Vite env variables
interface ImportMetaEnv {
  readonly VITE_CHATWOOT_ENABLED?: string;
  readonly VITE_CHATWOOT_TOKEN?: string;
  readonly VITE_CHATWOOT_BASE_URL?: string;
}

interface ImportMeta {
  readonly env: ImportMetaEnv;
}
