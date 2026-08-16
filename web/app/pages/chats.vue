<script setup lang="ts">
  import type { Conversation, Message } from '~/types/messaging';

  useHead({
    title: 'Chats',
  });

  // --- Meta ---
  definePageMeta({
    layout: 'main',
    requiresAuth: true,
  });


  // --- Composables ---
  const api = useApi();
  const authStore = useAuthStore();
  const messagingStore = useMessagingStore();


  // --- State ---
  const search = ref('');
  const draft = ref('');
  const isSending = ref(false);
  const isMessagesLoading = ref(false);
  const selectedConversationId = ref<string | null>(null);
  const messages = ref<Message[]>([]);
  const isLoadingOlder = ref(false);
  const hasMoreMessages = ref(true);
  const MESSAGES_PAGE_SIZE = 50;
  const messagesContainer = ref<HTMLElement | null>(null);
  const messagesContent = ref<HTMLElement | null>(null);


  // --- Conversations list ---
  const {
    conversations,
    pending: conversationsPending,
    refresh: refreshConversations,
  } = useConversationsList(search);


  // --- UI flags ---
  const isChat = computed(() => selectedConversationId.value !== null);
  const selectedConversation = computed(() =>
    conversations.value.find(c => c.id === selectedConversationId.value) ?? null,
  );


  // --- Messages ---
  async function loadMessages(conversationId: string) {
    isMessagesLoading.value = true;
    hasMoreMessages.value = true;

    try {
      messages.value = await api<Message[]>(
        `/conversations/${conversationId}/messages?limit=${MESSAGES_PAGE_SIZE}`,
      );

      hasMoreMessages.value = messages.value.length === MESSAGES_PAGE_SIZE;
    } finally {
      isMessagesLoading.value = false;
      await nextTick();
      scrollToBottom();
    }
  };

  async function loadOlderMessages() {
    if (
      !selectedConversationId.value ||
      isLoadingOlder.value ||
      !hasMoreMessages.value ||
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

      const older = await api<Message[]>(
        `/conversations/${selectedConversationId.value}/messages`
        + `?before=${oldestMessage.id}&limit=${MESSAGES_PAGE_SIZE}`,
      );

      if (!older.length) {
        hasMoreMessages.value = false;
        finishPrepend();
        return;
      }

      const existingIds = new Set(messages.value.map((m) => m.id));
      const uniqueOlder = older.filter((m) => !existingIds.has(m.id));

      if (!uniqueOlder.length) {
        hasMoreMessages.value = false;
        finishPrepend();
        return;
      }

      messages.value = [...uniqueOlder, ...messages.value];
      hasMoreMessages.value = older.length === MESSAGES_PAGE_SIZE;

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
  };

  async function markAsRead(conversationId: string) {
    await api(`/conversations/${conversationId}/read`, { method: 'POST' });
    const data = await api<{ total: number }>('/conversations/unread-count');
    messagingStore.setUnreadTotal(data.total);
  };

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
  };
  
  const shouldStickToBottom = ref(true);
  const suppressAutoScroll = ref(false);

  function onMessagesScroll() {
    const container = messagesContainer.value;
    if (!container || isLoadingOlder.value || suppressAutoScroll.value) return;

    const distanceFromBottom =
      container.scrollHeight - container.scrollTop - container.clientHeight;

    shouldStickToBottom.value = distanceFromBottom < 80;

    if (container.scrollTop <= 80) {
      void loadOlderMessages();
    }
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

  
  // --- Handlers ---
  async function selectConversation(conversation: Conversation) {
    messagingStore.setActiveConversation(conversation.id);
    selectedConversationId.value = conversation.id;
    await loadMessages(conversation.id);
    await markAsRead(conversation.id);
    await refreshConversations();
  };

  function closeChat() {
    messagingStore.setActiveConversation(null);
    selectedConversationId.value = null;
    messages.value = [];
    draft.value = '';
    hasMoreMessages.value = true;
  };

  async function sendMessage() {
    const body = draft.value.trim();
    if (!body || !selectedConversationId.value || isSending.value) return;
    isSending.value = true;
    try {
      const sent = await api<Message>(
        `/conversations/${selectedConversationId.value}/messages`,
        { method: 'POST', body: { body } },
      );
      if (!messages.value.some((m) => m.id === sent.id)) {
        messages.value.push(sent);
      }
      draft.value = '';
      await refreshConversations();
      await nextTick();
      scrollToBottom();
    } finally {
      isSending.value = false;
    }
  };


  // --- Realtime ---
  let unsubscribeNewMessage: (() => void) | undefined;

  function handleIncomingMessage(payload: {
    conversation_id: string
    message: Message
  }) {
    const { conversation_id, message } = payload;

    if (message.sender_id === authStore.user?.id) {
      refreshConversations();
      return;
    }

    if (selectedConversationId.value === conversation_id) {
      const exists = messages.value.some((m) => m.id === message.id);
      if (!exists) {
        messages.value.push(message);
        if (shouldStickToBottom.value) {
          scrollToBottom();
        }
      }
      void markAsRead(conversation_id);
      return;
    }

    refreshConversations();
  };


  // --- Lifecycle ---
  onMounted(async () => {
    await authStore.fetchMe();
    await refreshConversations();
    unsubscribeNewMessage = messagingStore.onNewMessage(handleIncomingMessage);
  });

  onUnmounted(() => {
    messagingStore.setActiveConversation(null);
    unsubscribeNewMessage?.();
  });
  
</script>

<template>
  <section class="
    relative flex flex-col flex-1 py-10
    bg-fourth"
  >
    <div class="container mx-auto flex flex-col flex-1 px-8">
      <div class="mb-3">
        <h1
          class="
            text-4xl font-semibold text-text-main 
          "
        >
          Chats
        </h1>
      </div>

      <div class="flex flex-1 gap-2.5">

        <div 
          class="
            flex flex-col flex-1 max-w-90 p-2.5
            border border-fifth rounded-sm
          "
        
          >

          <div
            class="
              flex items-center gap-1
              px-2 py-0.5 mb-3
              bg-third rounded-sm
            "
          >
            <Icon 
              name="material-symbols:search-rounded"
              class="size-6.5 text-fifth"
            />
            <UiInput 
              v-model="search"
              type="search"
              placeholder="Search..."
              input-class="
              !bg-transparent !py-2 !text-base
              "
            />
          </div>

          <div class="relative flex flex-col gap-1 flex-1 overflow-y-auto">
            <div 
              v-if="conversationsPending"
              class="px-3 py-2 bg-primary-light rounded-sm">
              <p class="text-body-sm text-text-main">
                Loading...
              </p>
            </div>
            <div 
              v-else-if="!conversations.length"
              class="px-3 py-2 bg-primary-light rounded-sm">
              <p class="text-body-sm text-text-main">
                No conversations yet
              </p>
            </div>
            <TransitionGroup
              tag="ul"
              name="conversation-item"
              class="absolute top-0 left-0 flex flex-col gap-2.5 w-full bg-fourth"
            >
              <ConversationItem
                v-for="conversation in conversations"
                :key="conversation.id"
                :conversation="conversation"
                :is-active="conversation.id === selectedConversationId"
                @select="selectConversation(conversation)"
              />
            </TransitionGroup>
          </div>

        </div>

        <div 
          class="
            flex flex-col flex-1 overflow-hidden
            border border-fifth rounded-sm"
        >

          <div 
            v-if="isChat"
            class="flex flex-col flex-1"
          >
            <div 
              class="flex items-center gap-1.5
                px-2 py-3
                bg-main shadow-sm
              "
            > 
              <button @click="closeChat" class="flex items-center justify-center ">
                <Icon
                  name="weui:arrow-outlined"
                  class="size-6 text-text-main rotate-180"
                />
              </button>

              <div class="flex items-center gap-2.5">
                <div 
                  class="
                    flex items-center justify-center overflow-hidden rounded-sm shrink-0
                    w-11 h-11
                  "
                >
                  <svg 
                    class="w-full h-full fill-text-main"
                    xmlns="http://www.w3.org/2000/svg" width="1em" height="1em" viewBox="0 0 32 32">
                    <path d="M0 0h32v32H0z" fill="none" />
                    <g fill="">
                      <path d="m15.287 17.527l-.99 3.17a1.005 1.005 0 0 0 .97 1.303h1.466c.688 0 1.173-.662.97-1.304l-.99-3.17c-.213-.701-1.203-.701-1.426 0m-1.87 5.757c.747.39 1.637.612 2.583.612c.956 0 1.836-.222 2.583-.612c.256-.13.53.148.369.39A3.53 3.53 0 0 1 16 25.25a3.53 3.53 0 0 1-2.952-1.577c-.16-.232.114-.52.369-.39M11.542 15.4c-1.214 0-2.24.84-2.527 1.967a.512.512 0 0 0 .503.633h.8a1.664 1.664 0 1 1 3.209 0h.148a.428.428 0 0 0 .424-.504a2.61 2.61 0 0 0-2.557-2.096m8.916 0c1.214 0 2.24.84 2.527 1.967a.512.512 0 0 1-.503.633h-.8a1.664 1.664 0 0 0-1.61-2.108a1.65 1.65 0 0 0-1.658 1.665q0 .236.06.443h-.149a.428.428 0 0 1-.424-.504a2.6 2.6 0 0 1 2.557-2.096" />
                      <path d="M11.927 16.611a.947.947 0 0 1 .84 1.389h-1.679a1 1 0 0 1-.108-.443c0-.172.046-.334.127-.473a.295.295 0 0 0 .544-.164a.3.3 0 0 0-.105-.229a.95.95 0 0 1 .381-.08m7.347.421a.94.94 0 0 0-.16.525c0 .157.04.305.11.443h1.678a.947.947 0 0 0-1.182-1.325a.3.3 0 0 1-.17.545a.3.3 0 0 1-.276-.188m2.404-4.649c.575.181.955.483 1.282.767a.517.517 0 0 1-.68.78c-.293-.256-.543-.444-.913-.56c-.378-.12-.927-.176-1.824-.067a.517.517 0 1 1-.126-1.026c.983-.12 1.694-.072 2.26.106m-12.313.747l-.001.002a.517.517 0 0 0 .633.818l.005-.004l.03-.022q.045-.032.14-.09a4.14 4.14 0 0 1 2.585-.53a.517.517 0 1 0 .127-1.027a5.17 5.17 0 0 0-3.242.67a4 4 0 0 0-.253.166l-.016.012l-.006.004z" />
                      <path d="M27.415 8.07a4.33 4.33 0 0 0-2.363-1.96c-1.049-.36-1.949-1.05-2.522-2A4.34 4.34 0 0 0 18.822 2c-.604 0-1.177.13-1.701.35c-.712.31-1.513.31-2.225 0a4.5 4.5 0 0 0-1.71-.35c-1.553 0-2.908.82-3.68 2.05a5 5 0 0 1-2.58 2.07c-.164.058-.326.106-.487.155C5.62 6.52 4.836 6.758 4 8.07c-1 1.57-1.12 3.4-.23 4.71c.327.48.505 1.05.505 1.63l.001.67A4 4 0 0 0 3 18.01c0 1.161.494 2.206 1.284 2.937q-.013.519-.034 1.039c0 1.134.925 2.185 1.991 2.933a8.3 8.3 0 0 0 8.008 6.091h3.517a8.3 8.3 0 0 0 8.011-6.104c1.059-.748 1.973-1.792 1.973-2.92l-.002-1.07A4 4 0 0 0 29 18.01a4 4 0 0 0-1.287-2.939v-.661c0-.58.178-1.15.504-1.63c.94-1.35.068-3.18-.802-4.71M7.5 13.3c0-2.926 2.399-5.3 5.29-5.3h2.373a.24.24 0 0 1 .219.151l.007.018l.008.018a5.52 5.52 0 0 0 5.037 3.283h2.587a1.7 1.7 0 0 1 1.593 1.651l-.166 2.768l.887.149a2 2 0 0 1-.216 3.969l-.885.051l-.22 3.504a6.3 6.3 0 0 1-6.248 5.448H14.25A6.3 6.3 0 0 1 8 23.56l-.23-3.504l-.884-.05a2 2 0 0 1-.26-3.961l.254-.048l.62-.091z" />
                    </g>
                  </svg>
                </div>

                <div class="flex flex-col gap-0.5 overflow-hidden">
                  <h3 class="text-text-main text-base font-semibold leading-4 whitespace-nowrap">
                    {{ selectedConversation?.participant.username }}
                  </h3>
                  <p class="text-text-secondary text-sm whitespace-nowrap">
                    Chat
                  </p>
                </div>
              </div>

              <button class="ml-auto">
                <Icon name="mage:dots" mode="svg" class="size-5 text-text-main"/>
              </button>
            </div>

            <div 
              ref="messagesContainer" 
              class="relative flex flex-col justify-end flex-1 overflow-y-auto" 
              data-lenis-prevent
              @scroll="onMessagesScroll"
            >
              <div ref="messagesContent" class="absolute top-0 left-0 w-full">
                <ConversationChat
                  v-if="authStore.user"
                  :messages="messages"
                  :current-user-id="authStore.user.id"
                  :loading="isMessagesLoading"
                  :loading-older="isLoadingOlder"
                  :has-more="hasMoreMessages"
                />
              </div>
            </div>

            <div
              class="flex items-center gap-3.5
                px-2 py-4
                bg-main shadow-[0_-2px_4px_0_rgb(0_0_0/0.05)]
              "
            >
              <div class="w-full">
                <UiInput
                  v-model="draft"
                  placeholder="Type a message..."
                  input-class="!bg-third !py-2 !text-base"
                  @keydown.enter.prevent="sendMessage"
                />
              </div>
              <button 
                @click="sendMessage"
                class="flex items-center justify-center shrink-0
                  w-10 h-10
                  bg-primary rounded-sm hover:bg-primary-hover
                "
                :disabled="!draft.trim() || isSending || !selectedConversationId"
              >
                <Icon name="mynaui:send-solid" mode="svg" class="size-6 text-main"/>
              </button>
            </div>
          </div>

          <div 
            v-else
            class="flex flex-1 items-center justify-center
            bg-primary-light"
          >
            <p class="text-center text-text-main text-xl font-semibold">
              Select a chat to start chatting
            </p>
          </div>
        </div>

      </div>
    </div>
  </section>
</template>

<style scoped lang="scss">

</style>