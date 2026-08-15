import type { Message } from '~/types/messaging';

export const useMessagingStore = defineStore('messaging', () => {
  const unreadTotal = ref(0);

  const newMessageListeners = new Set<(payload: any) => void>();
  const activeConversationId = ref<string | null>(null);

  function onNewMessage(listener: (payload: any) => void) {
    newMessageListeners.add(listener);
    return () => newMessageListeners.delete(listener);
  };

  function handleNewMessage(payload: {
    conversation_id: string
    message: Message
  }) {
    newMessageListeners.forEach((listener) => listener(payload))
  };

  function setUnreadTotal(total: number) {
    unreadTotal.value = total
  };

  function setActiveConversation(id: string | null) {
    activeConversationId.value = id
  };

  return { 
    unreadTotal,
    activeConversationId,
    onNewMessage,
    handleNewMessage,
    setUnreadTotal,
    setActiveConversation,
  };
});