import { useEffect } from 'react';
import type { ChatwootSDKConfig, ChatwootUser } from '../types/chatwoot';

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
      window.chatwootSDK?.run({
        websiteToken,
        baseUrl,
        position,
        locale,
        type: 'standard',
        launcherTitle: 'Chat com Suporte',
        showPopoutButton: true
      } as ChatwootSDKConfig);

      // Identificar usuário se fornecido
      if (user && window.$chatwoot) {
        const { id, ...userData } = user;
        window.$chatwoot.setUser(id, userData);
      }

      // Adicionar atributos customizados
      if (customAttributes && window.$chatwoot) {
        window.$chatwoot.setCustomAttributes(customAttributes);
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

      window.$chatwoot?.reset();
    };
  }, [websiteToken, baseUrl, position, locale, user, customAttributes, enabled]);

  return null;
}

// Hook para controlar widget programaticamente
export function useChatwoot() {
  const open = () => {
    window.$chatwoot?.toggle('open');
  };

  const close = () => {
    window.$chatwoot?.toggle('close');
  };

  const setUser = (id: string, user: ChatwootUser) => {
    window.$chatwoot?.setUser(id, user);
  };

  const setCustomAttributes = (attributes: Record<string, unknown>) => {
    window.$chatwoot?.setCustomAttributes(attributes);
  };

  const setLabel = (label: string) => {
    window.$chatwoot?.setLabel(label);
  };

  return {
    open,
    close,
    setUser,
    setCustomAttributes,
    setLabel
  };
}
