<script setup lang="ts">
  // --- Imports ---
  import type { CSSProperties } from 'vue';


  // --- Composables ---
  const aiChatStore = useAiChatStore();
  const { getHealth } = useAiApi();
  const dayjs = useDayjs();


  // --- Constants ---
  const PANEL_STORAGE_KEY = 'ai-chat-panel';
  const MIN_W = 280;
  const MIN_H = 240;
  type PanelAnimStyle = Record<string, string>;


  // --- Panel state ---
  const panelRef = ref<HTMLElement | null>(null);
  const savedPanel = loadPanelState();

  const pos = ref(savedPanel?.pos ?? { x: 8, y: 0 });
  const size = ref(savedPanel?.size ?? { width: 400, height: 400 });

  const isDragging = ref(false);
  const dragOffset = ref({ x: 0, y: 0 });

  const isResizing = ref(false);
  const resizeStart = ref({ x: 0, y: 0, width: 0, height: 0 });

  const isAnimating = ref(false);
  const runtimePanelStyle = ref<PanelAnimStyle | null>(null);

  // --- Chat state ---
  const draft = ref('');
  const isAiAvailable = ref(true);
  const aiModel = ref('');

  const messagesContainer = ref<HTMLElement | null>(null);
  const messagesContent = ref<HTMLElement | null>(null);

  const {
    messages,
    isLoading,
    isSending,
    isLoadingOlder,
    hasMore,
    isClearing,
    loadMessages,
    onMessagesScroll,
    sendMessage: sendAiMessage,
    clearChat,
    scrollToBottom,
  } = useAiChat(messagesContainer, messagesContent);


  // --- Panel computed ---
  const panelStyle = computed<CSSProperties>(() => ({
    left: `${pos.value.x}px`,
    top: `${pos.value.y}px`,
    width: `${size.value.width}px`,
    height: `${size.value.height}px`,
  }));

  const effectivePanelStyle = computed(() => runtimePanelStyle.value ?? panelStyle.value);


  // --- Panel persistence ---
  function loadPanelState() {
    try {
      const saved = localStorage.getItem(PANEL_STORAGE_KEY);
      if (!saved) return null;
      return JSON.parse(saved) as { pos: { x: number; y: number }; size: { width: number; height: number } };
    } catch {
      return null;
    }
  };

  function savePanelState() {
    localStorage.setItem(PANEL_STORAGE_KEY, JSON.stringify({
      pos: pos.value,
      size: size.value,
    }));
  };


  // --- Panel helpers ---
  function clamp(v: number, min: number, max: number) {
    return Math.min(Math.max(v, min), max);
  };

  function getPanelRectStyle(
    rect: { x: number; y: number; width: number; height: number },
    radius = '8px',
  ): PanelAnimStyle {
    return {
      left: `${rect.x}px`,
      top: `${rect.y}px`,
      width: `${rect.width}px`,
      height: `${rect.height}px`,
    };
  };

  function parsePx(value: string) {
    return Number.parseFloat(value);
  };

  function applyPanelStateFromStyle(style: PanelAnimStyle) {
    if (style.left) pos.value.x = parsePx(style.left);
    if (style.top) pos.value.y = parsePx(style.top);
    if (style.width) size.value.width = parsePx(style.width);
    if (style.height) size.value.height = parsePx(style.height);
  };


  // --- Panel animation ---
  async function finishPanelAnimation(to: PanelAnimStyle, syncState: boolean) {
    if (syncState) {
      applyPanelStateFromStyle(to);
    };

    runtimePanelStyle.value = null;
    await nextTick();
    panelRef.value?.getAnimations().forEach((animation) => animation.cancel());
    isAnimating.value = false;
  };

  async function animatePanel(
    from: PanelAnimStyle,
    to: PanelAnimStyle,
    duration = 350,
    syncState = true,
  ) {
    const el = panelRef.value;
    if (!el) return;

    isAnimating.value = true;
    runtimePanelStyle.value = from;
    await nextTick();

    try {
      const animation = el.animate([from, to], {
        duration,
        easing: 'cubic-bezier(0.4, 0, 0.2, 1)',
        fill: 'forwards',
      });
      await animation.finished;
      await finishPanelAnimation(to, syncState);
    } catch {
      await finishPanelAnimation(to, syncState);
    }
  };

  async function animateOpenFromButton() {
    const origin = aiChatStore.launchOrigin;
    if (!origin) return;

    const target = {
      x: pos.value.x,
      y: pos.value.y,
      width: size.value.width,
      height: size.value.height,
    };

    await animatePanel(
      {
        ...getPanelRectStyle(origin, '9999px'),
        opacity: '0.85',
      },
      {
        ...getPanelRectStyle(target),
        opacity: '1',
      },
    );

    aiChatStore.clearLaunchOrigin();
  };

  async function close() {
    savePanelState();

    const origin = aiChatStore.lastLaunchOrigin;
    if (origin) {
      await animatePanel(
        {
          ...getPanelRectStyle({
            x: pos.value.x,
            y: pos.value.y,
            width: size.value.width,
            height: size.value.height,
          }),
          opacity: '1',
        },
        {
          ...getPanelRectStyle(origin, '9999px'),
          opacity: '0.85',
        },
        280,
        false,
      );
    }

    aiChatStore.close();
  };


  // --- Panel drag ---
  function startDrag(e: MouseEvent) {
    if (e.button !== 0 || isAnimating.value) return;

    isDragging.value = true;
    dragOffset.value = {
      x: e.clientX - pos.value.x,
      y: e.clientY - pos.value.y,
    };

    document.addEventListener('mousemove', onDrag);
    document.addEventListener('mouseup', stopDrag);
    document.body.style.userSelect = 'none';
  };

  function onDrag(e: MouseEvent) {
    if (!isDragging.value) return;

    const maxX = window.innerWidth - size.value.width;
    const maxY = window.innerHeight - size.value.height;

    pos.value = {
      x: clamp(e.clientX - dragOffset.value.x, 0, maxX),
      y: clamp(e.clientY - dragOffset.value.y, 0, maxY),
    };
  };

  function stopDrag() {
    isDragging.value = false;
    document.removeEventListener('mousemove', onDrag);
    document.removeEventListener('mouseup', stopDrag);
    document.body.style.userSelect = '';
    savePanelState();
  };


  // --- Panel resize ---
  function startResize(e: MouseEvent) {
    if (e.button !== 0 || isAnimating.value) return;

    isResizing.value = true;
    resizeStart.value = {
      x: e.clientX,
      y: e.clientY,
      width: size.value.width,
      height: size.value.height,
    };
    document.addEventListener('mousemove', onResize);
    document.addEventListener('mouseup', stopResize);
    document.body.style.userSelect = 'none';
  };

  function onResize(e: MouseEvent) {
    if (!isResizing.value) return;

    const dx = e.clientX - resizeStart.value.x;
    const dy = e.clientY - resizeStart.value.y;
    const maxW = window.innerWidth - pos.value.x;
    const maxH = window.innerHeight - pos.value.y;

    size.value = {
      width: clamp(resizeStart.value.width + dx, MIN_W, maxW),
      height: clamp(resizeStart.value.height + dy, MIN_H, maxH),
    };
  };

  function stopResize() {
    isResizing.value = false;
    document.removeEventListener('mousemove', onResize);
    document.removeEventListener('mouseup', stopResize);
    document.body.style.userSelect = '';
    savePanelState();
  };


  // --- Chat ---
  function formatMessageTime(iso: string) {
    return dayjs(iso).format('HH:mm');
  };

  async function checkAiHealth() {
    try {
      const data = await getHealth();
      isAiAvailable.value = data.enabled && data.available;
      aiModel.value = data.model;
    } catch {
      isAiAvailable.value = false;
    }
  };

  async function sendMessage() {
    if (!draft.value.trim() || isSending.value || !isAiAvailable.value) return;

    const body = draft.value.trim();
    draft.value = '';

    try {
      await sendAiMessage(body);
    } catch {
      draft.value = body;
    }
  };

  async function onClearChat() {
    if (isClearing.value || isSending.value || !messages.value.length) return;
    await clearChat();
  };


  // --- Lifecycle ---
  onUnmounted(() => {
    stopDrag();
    stopResize();
    savePanelState();
  });

  onMounted(async () => {
    await animateOpenFromButton();
    await checkAiHealth();
    await loadMessages();
    await scrollToBottom();
  });
  
</script>

<template>
  <div
    ref="panelRef"
    class="
      fixed z-200
      flex flex-col overflow-hidden
      bg-main rounded-md border border-solid border-fifth/50
      shadow-lg bg-secondary
    "
    :style="effectivePanelStyle"
  >
    <div
      class="relative z-2 flex items-center justify-between gap-1.5 px-5 py-2 shadow-sm rounded-md cursor-move"
      :class="{ 'pointer-events-none opacity-0': isAnimating }"
      @mousedown="startDrag"
    >
      <h2 class="text-xl font-semibold text-text-main">
        Chat Ai
      </h2>

      <button
        class="transition-all transition-300 ease-in-out hover:rotate-90"
        @mousedown.stop
        @click="close"
      >
        <Icon name="akar-icons:cross" mode="svg" class="size-5 text-text-main" />
      </button>
    </div>

    <div
      ref="messagesContainer"
      class="relative flex flex-col justify-end flex-1 overflow-y-auto"
      :class="{ 'opacity-0': isAnimating }"
      data-lenis-prevent
      @scroll="onMessagesScroll"
    >
      <div
        ref="messagesContent"
        class="absolute top-0 left-0 w-full min-h-full flex flex-col justify-end"
      >
        <div class="flex flex-col gap-4 px-5 py-2">
          <p v-if="isLoadingOlder" class="text-center text-sm text-text-secondary">
            Loading older messages...
          </p>
          <p
            v-else-if="hasMore === false && messages.length && !isSending"
            class="text-center text-sm text-text-secondary"
          >
            Beginning of conversation
          </p>

          <p v-if="isLoading" class="text-center text-sm text-text-secondary">
            Loading messages...
          </p>

          <template v-else>
            <p v-if="!isAiAvailable" class="text-center text-sm text-text-secondary">
              AI is unavailable
            </p>

            <p
              v-else-if="!messages.length && !isSending"
              class="text-center text-sm text-text-secondary"
            >
              Ask something about Event Hub
            </p>

            <AiChatMessage
              v-for="message in messages"
              :key="message.id"
              :body="message.body"
              :is-mine="message.role === 'user'"
              :time="formatMessageTime(message.created_at)"
            />

            <p v-if="isSending" class="text-center text-sm text-text-secondary">
              AI is typing...
            </p>
          </template>
        </div>
      </div>
    </div>

    <div
      class="flex items-center gap-3.5
        px-5 py-2
        bg-main shadow-[0_-2px_4px_0_rgb(0_0_0/0.05)]
        rounded-md
      "
      :class="{ 'opacity-0': isAnimating }"
    >
    <UiButton
      style-type="delete"
      class="shrink-0"
      :disabled="isClearing || isSending || !messages.length || isAnimating"
      @click="onClearChat"
    >
      <Icon name="ant-design:clear-outlined" mode="svg" class="size-6" />
    </UiButton>
      <div class="w-full">
        <UiInput
          v-model="draft"
          placeholder="Type a message..."
          input-class="!bg-third !py-2 !text-base"
          :disabled="!isAiAvailable || isSending || isAnimating"
          @keydown.enter.prevent="sendMessage"
        />
      </div>
      <button
        class="flex items-center justify-center shrink-0
          w-10 h-10
          bg-primary rounded-sm hover:bg-primary-hover
        "
        :disabled="!draft.trim() || isSending || !isAiAvailable || isAnimating"
        @click="sendMessage"
      >
        <Icon name="mynaui:send-solid" mode="svg" class="size-6 text-main" />
      </button>
    </div>

    <button
      type="button"
      class="absolute -bottom-1 right-0 w-2 h-3 bg-primary rounded-l-lg cursor-se-resize"
      :class="{ 'pointer-events-none opacity-0': isAnimating }"
      @mousedown.stop="startResize"
    />
  </div>
</template>

<style scoped lang="scss">

</style>
