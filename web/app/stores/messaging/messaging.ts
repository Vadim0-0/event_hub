import type {
  Message,
  MessageNewPayload,
  ConversationActionPayload,
} from '~/types/domain/messaging';

export const useMessagingStore = defineStore('messaging', () => {
  const unreadTotal = ref(0);
  const activeConversationId = ref<string | null>(null);

  const newMessageListeners = new Set<(payload: MessageNewPayload) => void>();
  const clearedListeners = new Set<(payload: ConversationActionPayload) => void>();
  const deletedListeners = new Set<(payload: ConversationActionPayload) => void>();

  function onNewMessage(listener: (payload: MessageNewPayload) => void) {
    newMessageListeners.add(listener);
    return () => newMessageListeners.delete(listener);
  }

  function onConversationCleared(listener: (payload: ConversationActionPayload) => void) {
    clearedListeners.add(listener);
    return () => clearedListeners.delete(listener);
  }

  function onConversationDeleted(listener: (payload: ConversationActionPayload) => void) {
    deletedListeners.add(listener);
    return () => deletedListeners.delete(listener);
  }

  function handleNewMessage(payload: MessageNewPayload) {
    newMessageListeners.forEach((listener) => listener(payload));
  }

  function handleConversationCleared(payload: ConversationActionPayload) {
    clearedListeners.forEach((listener) => listener(payload));
  }

  function handleConversationDeleted(payload: ConversationActionPayload) {
    deletedListeners.forEach((listener) => listener(payload));
  }

  function setUnreadTotal(total: number) {
    unreadTotal.value = total;
  }

  function setActiveConversation(id: string | null) {
    activeConversationId.value = id;
  }

  return {
    unreadTotal,
    activeConversationId,
    onNewMessage,
    onConversationCleared,
    onConversationDeleted,
    handleNewMessage,
    handleConversationCleared,
    handleConversationDeleted,
    setUnreadTotal,
    setActiveConversation,
  };
});