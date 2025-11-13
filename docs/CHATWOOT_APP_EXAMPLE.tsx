/**
 * Exemplo de integração Chatwoot no App.tsx principal
 *
 * Este arquivo mostra como integrar o widget Chatwoot
 * na aplicação React com autenticação de usuário.
 */

import { ChatwootWidget, useChatwoot } from '@/components/ChatwootWidget';
import { useAuth } from '@/hooks/useAuth'; // seu hook de auth

// Exemplo 1: Integração básica sem autenticação
export function AppBasic() {
  return (
    <div className="app">
      {/* Widget Chatwoot - aparece no canto da tela */}
      <ChatwootWidget
        websiteToken={import.meta.env.VITE_CHATWOOT_TOKEN}
      />

      {/* Resto da aplicação */}
      <MainContent />
    </div>
  );
}

// Exemplo 2: Com identificação de usuário logado
export function AppWithAuth() {
  const { user, isAuthenticated } = useAuth();

  return (
    <div className="app">
      <ChatwootWidget
        websiteToken={import.meta.env.VITE_CHATWOOT_TOKEN}
        user={isAuthenticated && user ? {
          id: user.id,
          email: user.email,
          name: user.name,
          phone_number: user.phone,
        } : undefined}
        customAttributes={{
          role: user?.role,
          plan: 'basic',
          signup_date: user?.createdAt
        }}
      />

      <MainContent />
    </div>
  );
}

// Exemplo 3: Com botão customizado para abrir chat
function SupportButton() {
  const { open } = useChatwoot();

  return (
    <button
      onClick={open}
      className="fixed bottom-20 right-4 bg-blue-600 text-white px-4 py-2 rounded-full shadow-lg hover:bg-blue-700"
    >
      💬 Suporte
    </button>
  );
}

export function AppWithCustomButton() {
  const { user } = useAuth();

  return (
    <div className="app">
      {/* Widget oculto por padrão */}
      <ChatwootWidget
        websiteToken={import.meta.env.VITE_CHATWOOT_TOKEN}
        user={user ? {
          id: user.id,
          email: user.email,
          name: user.name
        } : undefined}
      />

      {/* Botão customizado */}
      <SupportButton />

      <MainContent />
    </div>
  );
}

// Exemplo 4: Condicional - só mostrar se habilitado
export function AppConditional() {
  const { user } = useAuth();
  const chatwootEnabled = import.meta.env.VITE_CHATWOOT_ENABLED === 'true';

  return (
    <div className="app">
      {chatwootEnabled && (
        <ChatwootWidget
          websiteToken={import.meta.env.VITE_CHATWOOT_TOKEN}
          user={user ? {
            id: user.id,
            email: user.email,
            name: user.name
          } : undefined}
        />
      )}

      <MainContent />
    </div>
  );
}

// Exemplo 5: Com diferentes locales
export function AppMultiLanguage() {
  const { user } = useAuth();
  const locale = user?.preferences?.language || 'pt_BR';

  return (
    <div className="app">
      <ChatwootWidget
        websiteToken={import.meta.env.VITE_CHATWOOT_TOKEN}
        locale={locale} // pt_BR, en, es, etc
        position="left" // ou 'right'
        user={user ? {
          id: user.id,
          email: user.email,
          name: user.name
        } : undefined}
      />

      <MainContent />
    </div>
  );
}

// Exemplo 6: Atualizar info do usuário dinamicamente
export function AppDynamic() {
  const { user } = useAuth();
  const { setUser, setCustomAttributes } = useChatwoot();

  // Atualizar quando mudar plano
  const handleUpgradePlan = (newPlan: string) => {
    setCustomAttributes({ plan: newPlan });
  };

  // Atualizar perfil
  const handleUpdateProfile = (updatedUser: any) => {
    setUser(updatedUser.id, {
      email: updatedUser.email,
      name: updatedUser.name,
      phone_number: updatedUser.phone
    });
  };

  return (
    <div className="app">
      <ChatwootWidget
        websiteToken={import.meta.env.VITE_CHATWOOT_TOKEN}
        user={user ? {
          id: user.id,
          email: user.email,
          name: user.name
        } : undefined}
      />

      <MainContent
        onUpgrade={handleUpgradePlan}
        onProfileUpdate={handleUpdateProfile}
      />
    </div>
  );
}

// Componente de exemplo
function MainContent({ onUpgrade, onProfileUpdate }: any) {
  return <div>Main app content here...</div>;
}

// --------------------------------------------------
// ARQUIVO .env NECESSÁRIO (frontend/.env)
// --------------------------------------------------
/*
VITE_CHATWOOT_ENABLED=true
VITE_CHATWOOT_TOKEN=your-website-token-from-chatwoot
VITE_CHATWOOT_BASE_URL=http://localhost:3001

# Em produção:
# VITE_CHATWOOT_BASE_URL=https://chat.seudominio.com
*/

// --------------------------------------------------
// COMO OBTER O TOKEN
// --------------------------------------------------
/*
1. Acessar http://localhost:3001
2. Criar conta admin (primeiro acesso)
3. Settings → Inboxes → Add Inbox
4. Selecionar "Website"
5. Copiar o websiteToken
6. Adicionar no .env como VITE_CHATWOOT_TOKEN
*/
