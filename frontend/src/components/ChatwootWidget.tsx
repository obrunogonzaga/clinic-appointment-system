import { useEffect } from 'react';

interface ChatwootWindow extends Window {
  chatwootSDK?: {
    run: (config: ChatwootConfig) => void;
  };
  $chatwoot?: {
    toggle: (state: 'open' | 'close') => void;
    setUser: (id: string, user: ChatwootUser) => void;
    setLabel: (label: string) => void;
    setCustomAttributes: (attributes: Record<string, unknown>) => void;
    reset: () => void;
  };
}

interface ChatwootConfig {
  websiteToken: string;
  baseUrl: string;
  position?: 'left' | 'right';
  locale?: string;
  type?: 'standard' | 'expanded_bubble';
  launcherTitle?: string;
  showPopoutButton?: boolean;
}

interface ChatwootUser {
  email?: string;
  name?: string;
  phone_number?: string;
  avatar_url?: string;
}

interface ChatwootWidgetProps {
  websiteToken: string;
  baseUrl?: string;
  position?: 'left' | 'right';
  locale?: string;
  user?: {
    id: string;
  } & ChatwootUser;
  customAttributes?: Record<string, unknown>;
  enabled?: boolean;
}

export function ChatwootWidget({
  websiteToken,
  baseUrl = import.meta.env.VITE_CHATWOOT_BASE_URL || 'http://localhost:3001',
  position = 'right',
  locale = 'pt_BR',
  user,
  customAttributes,
  enabled = import.meta.env.VITE_CHATWOOT_ENABLED !== 'false'
}: ChatwootWidgetProps) {
  useEffect(() => {
    if (!enabled || !websiteToken) {
      return;
    }

    const script = document.createElement('script');
    script.src = `${baseUrl}/packs/js/sdk.js`;
    script.defer = true;
    script.async = true;

    script.onload = () => {
      const chatWindow = window as ChatwootWindow;

      chatWindow.chatwootSDK?.run({
        websiteToken,
        baseUrl,
        position,
        locale,
        type: 'standard',
        launcherTitle: 'Chat com Suporte',
        showPopoutButton: true
      });

      // Identificar usuário se fornecido
      if (user && chatWindow.$chatwoot) {
        const { id, ...userData } = user;
        chatWindow.$chatwoot.setUser(id, userData);
      }

      // Adicionar atributos customizados
      if (customAttributes && chatWindow.$chatwoot) {
        chatWindow.$chatwoot.setCustomAttributes(customAttributes);
      }
    };

    script.onerror = () => {
      console.error('Erro ao carregar widget Chatwoot');
    };

    document.body.appendChild(script);

    return () => {
      // Cleanup
      if (document.body.contains(script)) {
        document.body.removeChild(script);
      }

      const chatWindow = window as ChatwootWindow;
      chatWindow.$chatwoot?.reset();
    };
  }, [websiteToken, baseUrl, position, locale, user, customAttributes, enabled]);

  return null;
}

// Hook para controlar widget programaticamente
export function useChatwoot() {
  const open = () => {
    (window as ChatwootWindow).$chatwoot?.toggle('open');
  };

  const close = () => {
    (window as ChatwootWindow).$chatwoot?.toggle('close');
  };

  const setUser = (id: string, user: ChatwootUser) => {
    (window as ChatwootWindow).$chatwoot?.setUser(id, user);
  };

  const setCustomAttributes = (attributes: Record<string, unknown>) => {
    (window as ChatwootWindow).$chatwoot?.setCustomAttributes(attributes);
  };

  const setLabel = (label: string) => {
    (window as ChatwootWindow).$chatwoot?.setLabel(label);
  };

  return {
    open,
    close,
    setUser,
    setCustomAttributes,
    setLabel
  };
}
