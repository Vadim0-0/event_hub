import type { Conversation, Message } from '~/types/domain/messaging';

export function useMessagingApi() {
  const api = useApi();

  function getUnreadCount() {
    return api<{ total: number }>('/conversations/unread-count');
  };

  function markConversationRead(conversationId: string) {
    return api(`/conversations/${conversationId}/read`, { method: 'POST' });
  };

  function sendConversationMessage(conversationId: string, body: string) {
    return api<Message>(`/conversations/${conversationId}/messages`, {
      method: 'POST',
      body: { body },
    });
  };

  function createConversation(recipientId: number) {
    return api<Conversation>('/conversations/', {
      method: 'POST',
      body: { recipient_id: recipientId },
    });
  };

  function clearConversation(conversationId: string, forEveryone = false) {
    return api(`/conversations/${conversationId}/clear`, {
      method: 'POST',
      body: { for_everyone: forEveryone },
    });
  };

  function deleteConversation(conversationId: string, forEveryone = false) {
    return api(`/conversations/${conversationId}`, {
      method: 'DELETE',
      body: { for_everyone: forEveryone },
    });
  };

  return { 
    getUnreadCount,
    markConversationRead,
    sendConversationMessage,
    createConversation,
    clearConversation,
    deleteConversation,
  };
};