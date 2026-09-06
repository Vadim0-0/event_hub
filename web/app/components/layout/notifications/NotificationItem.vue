<script setup lang="ts">
  import type { AppNotification } from '~/stores/ui/notifications';

  const props = defineProps<{
    item: AppNotification;
    barClass: string;
  }>();

  const notifications = useNotificationsStore();

  const SWIPE_THRESHOLD = 72;

  const itemRef = ref<HTMLElement | null>(null);
  const offset = ref({ x: 0, y: 0 });
  const isDragging = ref(false);
  const isAnimatingOut = ref(false);

  let pointerId: number | null = null;
  let startClientX = 0;
  let startClientY = 0;
  let startOffsetX = 0;
  let startOffsetY = 0;

  const itemStyle = computed(() => ({
    transform: `translate3d(${offset.value.x}px, ${offset.value.y}px, 0)`,
    transition: isDragging.value || isAnimatingOut.value ? undefined : 'transform 0.2s ease, opacity 0.2s ease',
    opacity: isAnimatingOut.value
      ? 0
      : 1 - Math.min(0.45, (Math.abs(offset.value.x) + Math.max(0, -offset.value.y)) / 260),
    touchAction: isDragging.value ? 'none' : 'pan-y',
  }));

  function onPointerDown(e: PointerEvent) {
    if (isAnimatingOut.value || e.button !== 0) return;

    isDragging.value = true;
    pointerId = e.pointerId;
    startClientX = e.clientX;
    startClientY = e.clientY;
    startOffsetX = offset.value.x;
    startOffsetY = offset.value.y;

    itemRef.value?.setPointerCapture(e.pointerId);
  };

  function onPointerMove(e: PointerEvent) {
    if (!isDragging.value || e.pointerId !== pointerId) return;

    offset.value = {
      x: startOffsetX + (e.clientX - startClientX),
      y: startOffsetY + (e.clientY - startClientY),
    };
  };

  function getDismissDirection(x: number, y: number) {
    const absX = Math.abs(x);
    const up = -y;

    if (up >= SWIPE_THRESHOLD && up >= absX) return 'up';
    if (x <= -SWIPE_THRESHOLD && absX >= up) return 'left';
    if (x >= SWIPE_THRESHOLD && absX >= up) return 'right';

    return null;
  };

  function animateOut(direction: 'left' | 'right' | 'up') {
    isAnimatingOut.value = true;
    isDragging.value = false;

    const travelX = direction === 'left'
      ? -window.innerWidth
      : direction === 'right'
        ? window.innerWidth
        : offset.value.x;

    const travelY = direction === 'up'
      ? -window.innerHeight
      : offset.value.y;

    offset.value = { x: travelX, y: travelY };

    window.setTimeout(() => {
      notifications.remove(props.item.id);
    }, 220);
  };

  function onPointerUp(e: PointerEvent) {
    if (!isDragging.value || e.pointerId !== pointerId) return;

    const activePointerId = pointerId;

    isDragging.value = false;
    pointerId = null;

    try {
      itemRef.value?.releasePointerCapture(activePointerId);
    } catch {}

    const direction = getDismissDirection(offset.value.x, offset.value.y);

    if (direction) {
      animateOut(direction);
      return;
    }

    offset.value = { x: 0, y: 0 };
  };

  function onPointerCancel(e: PointerEvent) {
    if (e.pointerId !== pointerId) return;

    isDragging.value = false;
    pointerId = null;
    offset.value = { x: 0, y: 0 };
  };
</script>

<template>
  <li
    ref="itemRef"
    class="
      relative flex overflow-hidden
      p-4 pb-6 w-full
      rounded-xl shadow-xl bg-third
      after:content-[''] after:absolute after:bottom-0 after:left-0 after:h-1 after:w-full
      select-none cursor-grab active:cursor-grabbing

      max-xl:p-3 max-xl:pb-5
      max-sm:p-2 max-sm:pb-3
    "
    :class="barClass"
    :style="itemStyle"
    @pointerdown="onPointerDown"
    @pointermove="onPointerMove"
    @pointerup="onPointerUp"
    @pointercancel="onPointerCancel"
  >
    <div class="flex flex-col gap-2.5 max-sm:gap-1 pointer-events-none">
      <div>
        <h4 class="text-2xl text-text-main font-semibold max-sm:text-xl">
          {{ item.title }}
        </h4>
      </div>
      <div>
        <p class="text-body-xl text-text-main max-sm:text-body-sm">
          {{ item.message }}
        </p>
      </div>
    </div>
  </li>
</template>
