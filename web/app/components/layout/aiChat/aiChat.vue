<script setup lang="ts">
  // --- Imports ---
  import type { CSSProperties } from 'vue';
  import aiChatRaw from '~~/data/components/aiChat.json';
  import { mapAiChat} from '~/mappers/components/aiChat';
  import type { AiChatRaw } from '~/types/i18n/components/aiChat';

  const { locale } = useI18n();
  const content = computed(() =>
    mapAiChat((aiChatRaw as AiChatRaw[])[0]!, locale.value),
  );

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

  const pos = ref(savedPanel?.pos ?? { x: 8, y: 8 });
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
    pendingEventAction,
    isCreatingEvent,
    confirmEventCreate,
    cancelEventCreate,
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

  function clampPanelToViewport() {
    if (!import.meta.client) return;

    const maxW = window.innerWidth;
    const maxH = window.innerHeight;

    size.value = {
      width: clamp(size.value.width, MIN_W, maxW),
      height: clamp(size.value.height, MIN_H, maxH),
    };

    pos.value = {
      x: clamp(pos.value.x, 0, Math.max(0, maxW - size.value.width)),
      y: clamp(pos.value.y, 0, Math.max(0, maxH - size.value.height)),
    };
  };

  function getPanelRect() {
    return {
      x: pos.value.x,
      y: pos.value.y,
      width: size.value.width,
      height: size.value.height,
    };
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
    clampPanelToViewport();
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
    clampPanelToViewport();

    const origin = aiChatStore.launchOrigin;
    if (!origin) return;

    const target = getPanelRect();

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
  function startDrag(e: PointerEvent) {
    if (e.button !== 0 || isAnimating.value) return;

    (e.currentTarget as HTMLElement).setPointerCapture(e.pointerId);

    isDragging.value = true;
    dragOffset.value = {
      x: e.clientX - pos.value.x,
      y: e.clientY - pos.value.y,
    };

    document.addEventListener('pointermove', onDrag);
    document.addEventListener('pointerup', stopDrag);
    document.addEventListener('pointercancel', stopDrag);
    document.body.style.userSelect = 'none';
  };

  function onDrag(e: PointerEvent) {
    if (!isDragging.value) return;

    e.preventDefault();

    const maxX = window.innerWidth - size.value.width;
    const maxY = window.innerHeight - size.value.height;

    pos.value = {
      x: clamp(e.clientX - dragOffset.value.x, 0, maxX),
      y: clamp(e.clientY - dragOffset.value.y, 0, maxY),
    };
  };

  function stopDrag(e?: PointerEvent) {
    isDragging.value = false;
    document.removeEventListener('pointermove', onDrag);
    document.removeEventListener('pointerup', stopDrag);
    document.removeEventListener('pointercancel', stopDrag);
    document.body.style.userSelect = '';

    if (e?.currentTarget instanceof HTMLElement) {
      try {
        e.currentTarget.releasePointerCapture(e.pointerId);
      } catch {}
    }

    clampPanelToViewport();
    savePanelState();
  };


  // --- Panel resize ---
  function startResize(e: PointerEvent) {
    if (e.button !== 0 || isAnimating.value) return;

    (e.currentTarget as HTMLElement).setPointerCapture(e.pointerId);

    isResizing.value = true;
    resizeStart.value = {
      x: e.clientX,
      y: e.clientY,
      width: size.value.width,
      height: size.value.height,
    };

    document.addEventListener('pointermove', onResize);
    document.addEventListener('pointerup', stopResize);
    document.addEventListener('pointercancel', stopResize);
    document.body.style.userSelect = 'none';
  };

  function onResize(e: PointerEvent) {
    if (!isResizing.value) return;
    e.preventDefault();

    const dx = e.clientX - resizeStart.value.x;
    const dy = e.clientY - resizeStart.value.y;
    const maxW = window.innerWidth - pos.value.x;
    const maxH = window.innerHeight - pos.value.y;

    size.value = {
      width: clamp(resizeStart.value.width + dx, MIN_W, maxW),
      height: clamp(resizeStart.value.height + dy, MIN_H, maxH),
    };
  };

  function stopResize(e?: PointerEvent) {
    isResizing.value = false;
    document.removeEventListener('pointermove', onResize);
    document.removeEventListener('pointerup', stopResize);
    document.removeEventListener('pointercancel', stopResize);
    document.body.style.userSelect = '';

    if (e?.currentTarget instanceof HTMLElement) {
      try {
        e.currentTarget.releasePointerCapture(e.pointerId);
      } catch {}
    };

    clampPanelToViewport();
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
    };
  };

  async function sendMessage() {
    if (!draft.value.trim() || isSending.value || !isAiAvailable.value) return;

    const body = draft.value.trim();
    draft.value = '';

    try {
      await sendAiMessage(body);
    } catch {
      draft.value = body;
    };
  };

  async function onClearChat() {
    if (isClearing.value || isSending.value || !messages.value.length) return;
    await clearChat();
  };


  // --- Lifecycle ---
  onBeforeMount(() => {
    clampPanelToViewport();
  });

  onMounted(async () => {
    clampPanelToViewport();
    await animateOpenFromButton();
    await checkAiHealth();
    await loadMessages();
    await scrollToBottom();

    if (import.meta.client) {
      window.addEventListener('resize', clampPanelToViewport);
    }
  });

  onUnmounted(() => {
    stopDrag();
    stopResize();

    if (import.meta.client) {
      window.removeEventListener('resize', clampPanelToViewport);
    }
  });
  
</script>

<template>
  <div
    ref="panelRef"
    class="
      fixed z-200
      flex flex-col overflow-hidden
      rounded-md border border-solid border-fifth/50
      shadow-lg bg-secondary

      max-sm:min-h-full max-sm:min-w-full
      max-sm:border-none
    "
    :style="effectivePanelStyle"
  >
    <div
      class="
        relative z-2 flex items-center justify-between gap-1.5 px-5 py-2 shadow-sm rounded-md cursor-move touch-none
        max-sm:px-4 max-sm:py-2
      "
      :class="{ 'pointer-events-none opacity-0': isAnimating }"
      @pointerdown="startDrag"
    >
      <h2 class="text-xl font-semibold text-text-main">
        {{ content.title }}
      </h2>

      <button
        class="transition-all transition-300 ease-in-out hover:rotate-90"
        @pointerdown.stop
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
        <div 
          class="
            flex flex-col gap-4 px-5 py-2
            max-sm:px-4 max-sm:gap-2
          ">
          <p v-if="isLoadingOlder" class="text-center text-sm text-text-secondary max-sm:mb-3">
            {{ content.loadingOlderMessages }}
          </p>
          <p
            v-else-if="hasMore === false && messages.length && !isSending"
            class="text-center text-sm text-text-secondary max-sm:mb-3"
          >
            {{ content.beginningOfConversation }}
          </p>

          <p v-if="isLoading" class="text-center text-sm text-text-secondary max-sm:mb-3">
            {{ content.loadingMessages }}
          </p>

          <template v-else>
            <p v-if="!isAiAvailable" class="text-center text-sm text-text-secondary max-sm:mb-3">
              {{ content.aiUnavailable }}
            </p>

            <p
              v-else-if="!messages.length && !isSending"
              class="text-center text-sm text-text-secondary max-sm:mb-3"
            >
              {{ content.askSomething }}
            </p>

            <template v-for="message in messages" :key="message.id">
              <AiChatMessage
                :body="message.body"
                :is-mine="message.role === 'user'"
                :time="formatMessageTime(message.created_at)"
              />

              <div
                v-if="pendingEventAction && String(pendingEventAction.assistantMessageId) === String(message.id)"
                class="flex justify-start px-2 -mt-2 mb-2 max-sm:mt-0 max-sm:mb-0"
              >
                <div 
                  class="
                    flex gap-2 max-w-3/5 min-w-52 max-sm:min-w-full max-sm:max-w-full
                    max-sm:grid max-sm:grid-cols-2
                    "
                >
                  <UiButton
                    style-type="cancel"
                    :disabled="isCreatingEvent"
                    @click="cancelEventCreate"
                  >
                    {{ content.cancelButton }}
                  </UiButton>
                  <UiButton
                    style-type="primary"
                    :disabled="isCreatingEvent"
                    @click="confirmEventCreate"
                  >
                    {{ content.confirmButton }}
                  </UiButton>
                </div>
              </div>
            </template>

            <p v-if="isSending" class="text-center text-sm text-text-secondary">
              {{ content.typing }}
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
        max-sm:px-3 max-sm:py-2 max-sm:gap-2.5
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
      class="absolute -bottom-1 -right-0.5 w-3 h-4 bg-primary rounded-l-lg cursor-se-resize touch-none max-md:hidden"
      :class="{ 'pointer-events-none opacity-0': isAnimating }"
      @pointerdown.stop="startResize"
    />
  </div>
</template>

<style scoped lang="scss">

</style>
