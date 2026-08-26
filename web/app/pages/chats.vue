<script setup lang="ts">
  import type { Conversation, Message } from '~/types/domain/messaging';
  import { onClickOutside } from '@vueuse/core';
  import type { UserListItem } from '~/types/domain/user';
  import chatsPageRaw from '~~/data/pages/chatsPage.json';
  import { mapChatsPage } from '~/mappers/pages/chatsPage';
  import type { ChatsPageRaw } from '~/types/i18n/pages/chatsPage';

  const { locale } = useI18n();
  
  const content = computed(() =>
    mapChatsPage((chatsPageRaw as ChatsPageRaw[])[0]!, locale.value),
  );

  useHead({
    title: computed(() => content.value.title),
  });

  // --- Meta ---
  definePageMeta({
    layout: 'main',
    requiresAuth: true,
  });


  // --- Composables ---
  const {
    getUnreadCount,
    markConversationRead,
    sendConversationMessage,
    createConversation,
    clearConversation,
    deleteConversation,
  } = useMessagingApi();
  const authStore = useAuthStore();
  const messagingStore = useMessagingStore();
  const confirmStore = useConfirmStore();
  const notifications = useNotificationsStore();


  // --- State ---
  const search = ref('');
  const draft = ref('');
  const isSending = ref(false);
  const selectedConversationId = ref<string | null>(null);
  const messagesContainer = ref<HTMLElement | null>(null);
  const messagesContent = ref<HTMLElement | null>(null);
  const isChatSettingsOpen = ref(false);
  const chatSettingsRef = ref<HTMLElement | null>(null);
  const isNewChatMode = ref(false);
  const sidebarListRef = ref<HTMLElement | null>(null);
  const isStartingChat = ref(false);
  const isCompact = useMediaQuery('(max-width: 1023px)');


  // --- Conversations list ---
  const {
    users,
    pending: usersPending,
    isLoadingMore: isLoadingMoreUsers,
    hasMore: hasMoreUsers,
    loadMore: loadMoreAvailableUsers,
    refresh: refreshAvailableUsers,
  } = useAvailableUsersList(isNewChatMode, search);

  const {
    conversations,
    pending: conversationsPending,
    refresh: refreshConversations,
  } = useConversationsList(search);

  const {
    messages,
    isLoading: isMessagesLoading,
    isLoadingOlder,
    hasMore: hasMoreMessages,
    shouldStickToBottom,
    loadMessages,
    scrollToBottom,
    onMessagesScroll,
    reset: resetMessages,
    clearMessages,
    appendMessage,
  } = useConversationMessages(selectedConversationId, messagesContainer, messagesContent);


  // --- UI flags ---
  const isChat = computed(() => selectedConversationId.value !== null);
  const selectedConversation = computed(() =>
    conversations.value.find(c => c.id === selectedConversationId.value) ?? null,
  );

  const showSidebar = computed(() => !isCompact.value || !isChat.value);
  const showChatPanel = computed(() => !isCompact.value || isChat.value);


  async function markAsRead(conversationId: string) {
    await markConversationRead(conversationId);
    const data = await getUnreadCount();
    messagingStore.setUnreadTotal(data.total);
  };

  const showScrollDownButton = computed(
    () => isChat.value && !shouldStickToBottom.value,
  );


  // --- Handlers ---
  async function selectConversation(conversation: Conversation) {
    messagingStore.setActiveConversation(conversation.id);
    selectedConversationId.value = conversation.id;
    await loadMessages();
    await nextTick();
    await scrollToBottom();
    await markAsRead(conversation.id);
    await refreshConversations();
  };

  function closeChat() {
    messagingStore.setActiveConversation(null);
    selectedConversationId.value = null;
    resetMessages();
    draft.value = '';
  };

  async function sendMessage() {
    const body = draft.value.trim();
    if (!body || !selectedConversationId.value || isSending.value) return;
    isSending.value = true;
    try {
      const sent = await sendConversationMessage(
        selectedConversationId.value,
        body,
      );
      appendMessage(sent);
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
  let unsubscribeCleared: (() => void) | undefined;
  let unsubscribeDeleted: (() => void) | undefined;

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
      if (appendMessage(message) && shouldStickToBottom.value) {
        scrollToBottom();
      }
      void markAsRead(conversation_id);
      return;
    }

    refreshConversations();
  };

  function handleConversationCleared(payload: {
    conversation_id: string
    for_everyone: boolean
  }) {
    if (selectedConversationId.value === payload.conversation_id) {
      clearMessages();
    }
    refreshConversations();
  };

  function handleConversationDeleted(payload: {
    conversation_id: string
    for_everyone: boolean
  }) {
    if (selectedConversationId.value === payload.conversation_id) {
      closeChat();
    }
    refreshConversations();
  };

  function mapUserToListItem(user: UserListItem): Conversation {
    return {
      id: `user-${user.id}`,
      participant: {
        id: user.id,
        username: user.username,
      },
      last_message: null,
      unread_count: 0,
      updated_at: user.created_at,
    };
  };


  // --- Change Chats ---
  function toggleNewChatMode() {
    isNewChatMode.value = !isNewChatMode.value;

    if (isNewChatMode.value) {
      void refreshAvailableUsers();
    }
  };

  async function startChatWithUser(recipientId: number) {
    if (isStartingChat.value) return;

    isStartingChat.value = true;
    try {
      const conversation = await createConversation(recipientId);

      isNewChatMode.value = false;
      await refreshConversations();
      await selectConversation(conversation);
    } catch (e) {
      const parsed = parseApiError(e);
      notifications.error(content.value.errorTitle, content.value.startChatError)
    } finally {
      isStartingChat.value = true;
    }
  };

  function openClearConfirm() {
    if (!selectedConversationId.value) return;
    isChatSettingsOpen.value = false;

    confirmStore.open({
      variant: 'default',
      title: content.value.confirmClearTitle,
      description: content.value.confirmClearDescription,
      confirmLabel: content.value.confirmClearButton,
      showCheckbox: true,
      checkboxLabel: content.value.confirmClearForEveryone,
      onConfirm: async ({ forEveryone }) => {
        await clearChatHistory(selectedConversationId.value!, forEveryone);
      },
    });
  };

  function openDeleteConfirm() {
    if (!selectedConversationId.value) return;
    isChatSettingsOpen.value = false;

    confirmStore.open({
      variant: 'delete',
      title: content.value.confirmDeleteTitle,
      description: content.value.confirmDeleteDescription,
      confirmLabel: content.value.confirmDeleteButton,
      showCheckbox: true,
      checkboxLabel: content.value.confirmDeleteForEveryone,
      onConfirm: async ({ forEveryone }) => {
        await deleteChat(selectedConversationId.value!, forEveryone);
      },
    });
  };

  async function refreshUnreadTotal() {
    const data = await getUnreadCount();
    messagingStore.setUnreadTotal(data.total);
  };

  async function clearChatHistory(conversationId: string, forEveryone = false) {
    try {
      await clearConversation(conversationId, forEveryone);

      clearMessages();
      await refreshConversations();
      await refreshUnreadTotal();
    } catch (e) {
      const parsed = parseApiError(e);
      notifications.error(content.value.errorTitle, parsed.formError || content.value.startChatError);
      throw e;
    }
  };

  async function deleteChat(conversationId: string, forEveryone = false) {
    try {
      await clearConversation(conversationId, forEveryone);

      closeChat();
      await refreshConversations();
      await refreshUnreadTotal();
    } catch (e) {
      const parsed = parseApiError(e);
      notifications.error(content.value.errorTitle, parsed.formError || content.value.deleteChatError);
      throw e;
    }
  };


  // --- Lifecycle ---
  onMounted(async () => {
    await authStore.fetchMe();
    await refreshConversations();
    unsubscribeNewMessage = messagingStore.onNewMessage(handleIncomingMessage);
    unsubscribeCleared = messagingStore.onConversationCleared(handleConversationCleared);
    unsubscribeDeleted = messagingStore.onConversationDeleted(handleConversationDeleted);
  });

  onUnmounted(() => {
    messagingStore.setActiveConversation(null);
    unsubscribeNewMessage?.();
    unsubscribeCleared?.();
    unsubscribeDeleted?.();
  });

  onClickOutside(chatSettingsRef, () => {
    isChatSettingsOpen.value = false;
  });

  function onSidebarListScroll() {
    if (!isNewChatMode.value || !hasMoreUsers.value || isLoadingMoreUsers.value) {
      return;
    }

    const container = sidebarListRef.value;
    if (!container) return;

    const distanceFromBottom =
      container.scrollHeight - container.scrollTop - container.clientHeight;

    if (distanceFromBottom < 80) {
      void loadMoreAvailableUsers();
    }
  }
  
</script>

<template>
  <section class="
    relative flex flex-col flex-1 py-10
    bg-fourth
    max-md:py-5
    "
  >
    <div class="container mx-auto flex flex-col flex-1 px-8
      max-md:px-4
      max-sm:px-3
    ">
      <div class="mb-3 max-lg:mb-2">
        <h1
          class="
            text-4xl font-semibold text-text-main
            max-lg:text-3xl 
          "
        >
          {{ content.title }}
        </h1>
      </div>

      <div 
        class="
          relative
          flex flex-1 gap-2.5 overflow-hidden 
          max-lg:border max-lg:border-fifth max-lg:rounded-sm
          max-lg:gap-0
        "
      >

        <Transition :name="isCompact ? 'slide-sidebar' : undefined">
          <div 
            v-if="showSidebar"
            class="
              relative
              flex flex-col flex-1 max-w-90 p-2.5
              border border-fifth rounded-sm
              max-lg:max-w-full max-lg:w-full max-lg:border-none
            "
            >
  
            <div
              class="
                flex items-center gap-1
                px-2 py-0.5 mb-3
                bg-third rounded-sm
                max-sm:mb-2
              "
            >
              <Icon 
                name="material-symbols:search-rounded"
                class="size-6.5 text-fifth"
              />
              <UiInput 
                v-model="search"
                type="search"
                :placeholder="content.searchPlaceholder"
                input-class="
                !bg-transparent !py-2 !text-base max-sm:!py-1.5
                "
              />
            </div>
  
            <div 
              ref="sidebarListRef" 
              class="relative flex flex-col gap-1 flex-1 overflow-y-auto"
              data-lenis-prevent
              @scroll="onSidebarListScroll"
            >
              <div 
                v-if="isNewChatMode ? usersPending : conversationsPending"
                class="px-3 py-2 bg-primary-light rounded-sm">
                <p class="text-body-sm text-text-main">
                  {{ content.loading }}
                </p>
              </div>
              <div 
                v-else-if="isNewChatMode ? !users.length : !conversations.length"
                class="px-3 py-2 bg-primary-light rounded-sm">
                <p class="text-body-sm text-text-main">
                  {{ isNewChatMode ? content.emptyUsers : content.emptyConversations }}
                </p>
              </div>
  
              <!-- Users -->
              <TransitionGroup
                v-else-if="isNewChatMode"
                tag="ul"
                name="conversation-list"
                class="
                  absolute top-0 left-0 flex flex-col gap-2.5 w-full bg-fourth
                  max-sm:gap-2
                "
              >
                <ConversationItem
                  v-for="user in users"
                  :key="user.id"
                  :conversation="mapUserToListItem(user)"
                  :show-meta="false"
                  :preview-text="content.startChatPreview"
                  @select="startChatWithUser(user.id)"
                />
              </TransitionGroup>
  
              <!-- Conversations -->
              <TransitionGroup
                v-else
                tag="ul"
                name="conversation-list"
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
  
            <button
              class="
                group absolute bottom-2.5 left-2.5
                max-sm:left-[unset] max-sm:right-2
              "
              @click="toggleNewChatMode"
            >
              <Icon
                :name="isNewChatMode ? 'weui:arrow-outlined' : 'ri:chat-new-fill'"
                mode="svg"
                class="size-8 text-primary transition-color duration-300 ease-in-out group-hover:text-primary-hover"
                :class="isNewChatMode ? 'rotate-180' : ''"
              />
            </button>
  
          </div>
        </Transition>

        <Transition :name="isCompact ? 'slide-chat' : undefined">
          <div 
            v-show="showChatPanel"
            class="
              flex flex-col flex-1 overflow-hidden
              border border-fifth rounded-sm

              max-lg:absolute max-lg:top-0
              max-lg:border-none max-lg:w-full max-lg:h-full
            "
          >
            <Transition name="chat-content" mode="out-in">
              <div 
                v-if="isChat"
                :key="selectedConversationId ?? 'chat'"
                class="flex flex-col flex-1"
              >
                <div 
                  class="flex items-center gap-1.5
                    px-2 py-3
                    bg-main shadow-sm
                    max-sm:py-2
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
                        max-sm:w-10 max-sm:h-10
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
                      <h3 class="text-text-main text-xl font-semibold leading-6 whitespace-nowrap max-sm:text-body-xl">
                        {{ selectedConversation?.participant.username }}
                      </h3>
                      <p class="text-text-secondary text-sm whitespace-nowrap hidden">
                        {{ content.chatSubtitle }}
                      </p>
                    </div>
                  </div>
    
                  <div ref="chatSettingsRef" class="relative ml-auto">
                    <button class="py-1 rounded-sm hover:bg-primary-light" @click="isChatSettingsOpen = !isChatSettingsOpen">
                      <Icon name="mage:dots" mode="svg" class="size-5 text-text-main"/>
                    </button>
    
                    <Transition name="chat-settings-visible">
                      <div v-if="isChatSettingsOpen" class="absolute top-full right-0 z-10">
                        <LayoutChatSettings 
                          @clear-history="openClearConfirm"
                          @delete-chat="openDeleteConfirm"
                        />
                      </div>
                    </Transition>
                  </div>
    
                </div>
    
                <div 
                  ref="messagesContainer" 
                  class="relative flex flex-1 overflow-y-auto" 
                  data-lenis-prevent
                  @scroll="onMessagesScroll"
                >
                  <div ref="messagesContent" class="absolute top-0 left-0 w-full min-h-full flex flex-col justify-end">
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
                    max-sm:py-2 max-sm:gap-2
                  "
                >
                  <div class="w-full">
                    <UiInput
                      v-model="draft"
                      :placeholder="content.messagePlaceholder"
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

                <Transition name="scroll-down-btn">
                  
                  <button 
                    v-if="showScrollDownButton"
                    @click="scrollToBottom"
                    class="
                      absolute bottom-21 right-2
                      flex items-center justify-center shrink-0
                      w-10 h-10
                      shadow-[0px_0_23px_2px_rgba(0_0_0/0.2)] bg-primary rounded-sm hover:bg-primary-hover
                      max-sm:bottom-16
                    "
                  >
                    <Icon name="fluent:arrow-sort-down-16-regular" mode="svg" class="size-7 text-main"/>
                  </button>
                </Transition>

              </div>
    
              <div 
                v-else
                key="empty"
                class="flex flex-1 items-center justify-center p-3
                bg-primary-light"
              >
                <p class="text-center text-text-main text-xl font-semibold max-lg:text-lg">
                  {{ content.emptyState }}
                </p>
              </div>
            </Transition>
          </div>
        </Transition>
      </div>
    </div>
  </section>
</template>

<style scoped lang="scss">
  .scroll-down-btn-enter-active,
  .scroll-down-btn-leave-active {
    transition: transform 0.3s ease-in-out, opacity 0.3s ease-in-out;
  }
  .scroll-down-btn-enter-from,
  .scroll-down-btn-leave-to {
    transform: translateY(10px);
    opacity: 0;
  }

  .chat-settings-visible-enter-active,
  .chat-settings-visible-leave-active {
    transition: transform 0.3s ease-in-out, opacity 0.3s ease-in-out;
  }
  .chat-settings-visible-enter-from,
  .chat-settings-visible-leave-to {
    transform: translateY(-10px);
    opacity: 0;
  }

  .slide-chat-enter-active,
  .slide-chat-leave-active {
    transition: transform 0.3s ease-in-out, opacity 0.3s ease-in-out;
  }
  .slide-chat-enter-from,
  .slide-chat-leave-to {
    transform: translateX(100%);
    opacity: 0;
  }

  .slide-sidebar-enter-active,
  .slide-sidebar-leave-active {
    transition: transform 0.3s ease-in-out, opacity 0.3s ease-in-out;
  }
  .slide-sidebar-enter-from,
  .slide-sidebar-leave-to {
    transform: translateX(-100%);
    opacity: 0;
  }

  @media (min-width: 1024px) {
    .chat-content-enter-active,
    .chat-content-leave-active {
      transition: transform 0.3s ease-in-out, opacity 0.3s ease-in-out;
    }
    .chat-content-enter-from {
      opacity: 0;
      transform: translateY(12px);
    }
    .chat-content-leave-to {
      opacity: 0;
      transform: translateY(-12px);
    }
  }

</style>