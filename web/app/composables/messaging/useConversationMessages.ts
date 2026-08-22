import type { Message } from '~/types/domain/messaging';

const PAGE_SIZE = 50;

export function useConversationMessages(
  conversationId: Ref<string | null>,
  messagesContainer: Ref<HTMLElement | null>,
  messagesContent: Ref<HTMLElement | null>,
) {
  const api = useApi();

  const messages = ref<Message[]>([]);
  const isLoading = ref(false);
  const isLoadingOlder = ref(false);
  const hasMore = ref(true);
  const shouldStickToBottom = ref(true);
  const suppressAutoScroll = ref(false);

  async function fetchMessages(before?: string) {
    const id = conversationId.value;
    if (!id) return [];

    const params = new URLSearchParams({ limit: String(PAGE_SIZE) });
    if (before) params.set('before', before);

    return api<Message[]>(`/conversations/${id}/messages?${params}`);
  }

  async function scrollToBottom() {
    await nextTick();
    requestAnimationFrame(() => {
      const container = messagesContainer.value;
      const content = messagesContent.value;
      if (!container) return;
      const maxScroll = container.scrollHeight - container.clientHeight;
      container.scrollTop = maxScroll > 0 ? maxScroll : 0;
      if (content && maxScroll <= 0) {
        container.scrollTop = Math.max(0, content.offsetHeight - container.clientHeight);
      }
    });
  }

  async function loadMessages() {
    isLoading.value = true;
    hasMore.value = true;

    try {
      messages.value = await fetchMessages();
      hasMore.value = messages.value.length === PAGE_SIZE;
    } finally {
      isLoading.value = false;
      await scrollToBottom();
    }
  }

  async function loadOlderMessages() {
    if (
      !conversationId.value ||
      isLoadingOlder.value ||
      !hasMore.value ||
      !messages.value.length
    ) {
      return;
    }

    isLoadingOlder.value = true;
    shouldStickToBottom.value = false;
    suppressAutoScroll.value = true;

    const container = messagesContainer.value;
    const prevScrollHeight = container?.scrollHeight ?? 0;
    const prevScrollTop = container?.scrollTop ?? 0;

    const finishPrepend = () => {
      suppressAutoScroll.value = false;
      isLoadingOlder.value = false;
    };

    try {
      const oldestMessage = messages.value[0];
      if (!oldestMessage) {
        finishPrepend();
        return;
      }

      const older = await fetchMessages(oldestMessage.id);

      if (!older.length) {
        hasMore.value = false;
        finishPrepend();
        return;
      }

      const existingIds = new Set(messages.value.map((m) => m.id));
      const uniqueOlder = older.filter((m) => !existingIds.has(m.id));

      if (!uniqueOlder.length) {
        hasMore.value = false;
        finishPrepend();
        return;
      }

      messages.value = [...uniqueOlder, ...messages.value];
      hasMore.value = older.length === PAGE_SIZE;

      await nextTick();
      requestAnimationFrame(() => {
        if (container) {
          container.scrollTop = prevScrollTop + (container.scrollHeight - prevScrollHeight);
        }
        finishPrepend();
      });
    } catch {
      finishPrepend();
    }
  }

  function onMessagesScroll() {
    const container = messagesContainer.value;
    if (!container || isLoadingOlder.value || suppressAutoScroll.value) return;

    const distanceFromBottom =
      container.scrollHeight - container.scrollTop - container.clientHeight;

    shouldStickToBottom.value = distanceFromBottom < 80;

    if (container.scrollTop <= 80) {
      void loadOlderMessages();
    }
  }

  function reset() {
    messages.value = [];
    hasMore.value = true;
  }

  function clearMessages() {
    messages.value = [];
    hasMore.value = false;
  }

  function appendMessage(message: Message) {
    if (messages.value.some((m) => m.id === message.id)) return false;
    messages.value.push(message);
    return true;
  }

  watch(
    () => messages.value.at(-1)?.id,
    () => {
      if (suppressAutoScroll.value || isLoadingOlder.value || !shouldStickToBottom.value) {
        return;
      }
      scrollToBottom();
    },
  );

  return {
    messages,
    isLoading,
    isLoadingOlder,
    hasMore,
    shouldStickToBottom,
    loadMessages,
    loadOlderMessages,
    scrollToBottom,
    onMessagesScroll,
    reset,
    clearMessages,
    appendMessage,
    PAGE_SIZE,
  };
}
