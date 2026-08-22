import type { AiChatResponse, AiMessage, AiMessageOut, AiPendingEventAction } from '~/types/domain/ai';

const PAGE_SIZE = 50;

function mapApiMessage(row: AiMessageOut): AiMessage {
  return {
    id: row.id,
    role: row.role as AiMessage['role'],
    body: row.content,
    created_at: row.created_at,
  };
}

export function useAiChat(
  messagesContainer: Ref<HTMLElement | null>,
  messagesContent: Ref<HTMLElement | null>,
) {
  const { listMessages, sendChatMessage, clearMessages: clearMessagesApi, createEventFromDraft } = useAiApi();
  const notifications = useNotificationsStore();

  const messages = ref<AiMessage[]>([]);
  const total = ref(0);
  const isLoading = ref(false);
  const isSending = ref(false);
  const isClearing = ref(false);

  const loadedSkip = ref(0);
  const isLoadingOlder = ref(false);
  const hasMore = ref(false);
  const shouldStickToBottom = ref(true);
  const suppressAutoScroll = ref(false);

  const pendingEventAction = ref<AiPendingEventAction | null>(null);
  const isCreatingEvent = ref(false);

  async function scrollToBottom() {
    shouldStickToBottom.value = true;
    await nextTick();
    requestAnimationFrame(() => {
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
    });
  }

  async function loadMessages() {
    isLoading.value = true;
    hasMore.value = false;

    try {
      const meta = await listMessages(0, 1);
      total.value = meta.total;

      if (!meta.total) {
        messages.value = [];
        loadedSkip.value = 0;
        return;
      }

      loadedSkip.value = Math.max(0, meta.total - PAGE_SIZE);
      const data = await listMessages(loadedSkip.value, PAGE_SIZE);
      messages.value = data.items.map(mapApiMessage);
      hasMore.value = loadedSkip.value > 0;
    } catch (e) {
      const parsed = parseApiError(e);
      notifications.error('AI error', parsed.formError || 'Failed to load messages');
      throw e;
    } finally {
      isLoading.value = false;
      await scrollToBottom();
    }
  }

  async function loadOlderMessages() {
    if (isLoadingOlder.value || isSending.value || !hasMore.value || !messages.value.length) {
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
      const nextSkip = Math.max(0, loadedSkip.value - PAGE_SIZE);
      const data = await listMessages(nextSkip, PAGE_SIZE);

      if (!data.items.length) {
        hasMore.value = false;
        finishPrepend();
        return;
      }

      const existingIds = new Set(messages.value.map((m) => m.id));
      const uniqueOlder = data.items
        .map(mapApiMessage)
        .filter((m) => !existingIds.has(m.id));

      if (!uniqueOlder.length) {
        hasMore.value = false;
        finishPrepend();
        return;
      }

      messages.value = [...uniqueOlder, ...messages.value];
      loadedSkip.value = nextSkip;
      hasMore.value = loadedSkip.value > 0;

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
    if (!container || isLoadingOlder.value || isSending.value || suppressAutoScroll.value) {
      return;
    }

    const distanceFromBottom =
      container.scrollHeight - container.scrollTop - container.clientHeight;

    shouldStickToBottom.value = distanceFromBottom < 80;

    if (container.scrollTop <= 80) {
      void loadOlderMessages();
    }
  }

  async function clearChat() {
    if (isClearing.value) return;

    isClearing.value = true;

    try {
      await clearMessagesApi();
      messages.value = [];
      total.value = 0;
      loadedSkip.value = 0;
      hasMore.value = false;
      shouldStickToBottom.value = true;
      pendingEventAction.value = null;
    } catch (e) {
      const parsed = parseApiError(e);
      notifications.error('AI error', parsed.formError || 'Failed to clear chat');
      throw e;
    } finally {
      isClearing.value = false;
    }
  }

  function appendFromChatResponse(
    userBody: string,
    response: {
      reply: string
      user_message_id: string
      assistant_message_id: string
    },
  ) {
    const now = new Date().toISOString();

    messages.value.push(
      {
        id: response.user_message_id,
        role: 'user',
        body: userBody,
        created_at: now,
      },
      {
        id: response.assistant_message_id,
        role: 'assistant',
        body: response.reply,
        created_at: now,
      },
    );

    total.value += 2;
  }

  async function sendMessage(body: string) {
    const text = body.trim();
    if (!text || isSending.value) return;

    isSending.value = true;
    shouldStickToBottom.value = true;

    const pendingId = `pending-${crypto.randomUUID()}`;
    messages.value.push({
      id: pendingId,
      role: 'user',
      body: text,
      created_at: new Date().toISOString(),
    });

    await scrollToBottom();

    let chatData: AiChatResponse | null = null;

    try {
      chatData = await sendChatMessage(text);
      messages.value = messages.value.filter((message) => message.id !== pendingId);
      appendFromChatResponse(text, chatData);
      await scrollToBottom();

      if (chatData.ready_to_create && chatData.draft) {
        pendingEventAction.value = {
          assistantMessageId: String(chatData.assistant_message_id),
          draft: chatData.draft,
        };
      } else {
        pendingEventAction.value = null;
      }
    } catch (e) {
      messages.value = messages.value.filter((message) => message.id !== pendingId);
      pendingEventAction.value = null;
      const parsed = parseApiError(e);
      notifications.error('AI error', parsed.formError || 'Failed to get AI response');
      throw e;
    } finally {
      isSending.value = false;
    }
  }

  async function confirmEventCreate() {
    if (!pendingEventAction.value || isCreatingEvent.value) return;

    isCreatingEvent.value = true;

    try {
      const result = await createEventFromDraft(pendingEventAction.value.draft);

      messages.value.push({
        id: `system-${crypto.randomUUID()}`,
        role: 'assistant',
        body: result.reply,
        created_at: new Date().toISOString(),
      });

      pendingEventAction.value = null;

      useEventsListRefreshStore().request();
      useEventsStore().fetchStats();
      notifications.success('Event created', result.event.title);
      await scrollToBottom();
    } catch (e) {
      const parsed = parseApiError(e);
      notifications.error('Error', parsed.formError || 'Failed to create event');
    } finally {
      isCreatingEvent.value = false;
    }
  };

  function cancelEventCreate() {
    pendingEventAction.value = null;
  };

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
    total,
    isLoading,
    isSending,
    isLoadingOlder,
    hasMore,
    isClearing,
    loadMessages,
    loadOlderMessages,
    onMessagesScroll,
    clearChat,
    sendMessage,
    scrollToBottom,
    PAGE_SIZE,
    pendingEventAction,
    isCreatingEvent,
    confirmEventCreate,
    cancelEventCreate,
  };
}
