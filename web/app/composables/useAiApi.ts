import type {
  AiChatResponse,
  AiHealthResponse,
  AiMessagesListOut,
} from '~/types/ai';

export function useAiApi() {
  const api = useApi();

  function getHealth() {
    return api<AiHealthResponse>('/ai/health');
  };

  function listMessages(skip = 0, limit = 50) {
    const params = new URLSearchParams({
      skip: String(skip),
      limit: String(limit),
    });
    return api<AiMessagesListOut>(`/ai/messages?${params}`);
  };

  function sendChatMessage(message: string) {
    return api<AiChatResponse>('/ai/chat', {
      method: 'POST',
      body: { message },
    });
  };

  function clearMessages() {
    return api<void>('/ai/messages', { method: 'DELETE' });
  };

  return {
    getHealth,
    listMessages,
    sendChatMessage,
    clearMessages,
  };
};