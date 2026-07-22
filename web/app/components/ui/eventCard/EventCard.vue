<script setup lang="ts">

  import type { Event } from '~/types/event';

  const props = defineProps<{ event: Event }>();
  const dayjs = useDayjs();
  const selectedEventStore = useSelectedEventStore();

  function openEventInfo() {
    selectedEventStore.open(props.event)
  };

  const formattedCreatedAt = computed(() =>
    dayjs(props.event.created_at).format('DD MMMM YYYY')
  );

  const cardRef = ref<HTMLElement | null>(null);
  const defaultTransformStyle = 'perspective(800px) rotateX(0deg) rotateY(0deg) scale(1)';
  const transformStyle = ref(defaultTransformStyle);

  function onMouseMove(e: MouseEvent) {
    const el = cardRef.value;
    if (!el) return;

    const rect = el.getBoundingClientRect();
    const x = e.clientX - rect.left;
    const y = e.clientY - rect.top;

    const midX = x / rect.width - 0.5;
    const midY = y / rect.height - 0.5;

    const maxTilt = 10;

    const rotateY = midX * maxTilt;
    const rotateX = -midY * maxTilt;

    transformStyle.value = `perspective(800px) rotateX(${rotateX}deg) rotateY(${rotateY}deg) scale(1.04)`;
  };

  function onMouseLeave() {
    transformStyle.value = defaultTransformStyle;
  };


  const fillPercent = computed(() => {
    const max = props.event.max_participants
    if (!max) return 0
    return Math.min(100, (props.event.participants_count / max) * 100)
  });

  const participantsLabel = computed(() => {
    const current = props.event.participants_count
    const max = props.event.max_participants
    return max ? `${current}/${max}` : `${current}`
  });

  const ringStyle = computed(() => ({
    background: `conic-gradient(
      var(--color-main) ${fillPercent.value * 3.6}deg,
      var(--color-third) 0deg
    )`,
  }));

  const isOpen = computed(() => selectedEventStore.isSelected(props.event.id));

</script>

<template>
  <li
    ref="cardRef"
    class="
      relative
      flex flex-col
      p-2.5
      min-h-[200px]
 
      bg-primary shadow-md shadow-primary/20 rounded-sm
      transition-transform duration-300 ease-out
      will-change-transform
    "
    :class="{'!scale-[1.08]': isOpen}"
    :style="{ transform: transformStyle }"
    @mousemove="onMouseMove"
    @mouseleave="onMouseLeave"
  >
    <button
      type="button"
      @click="openEventInfo"
      class="absolute top-0 left-0 w-full h-full z-1"
    ></button>
    <div
      class="flex flex-col gap-2 mb-3"
    >
      <h3
        class="text-[22px] font-semibold  text-main line-clamp-1"
      >
        {{ event.title }}
      </h3>
      <p
        class="text-lg leading-5.5 text-main line-clamp-3"
      >
        {{ event.description }}
      </p>
    </div>
    <div class="flex flex-col items-start gap-1 mt-auto">
      <button 
        class="
          relative z-2
          text-base text-main">
          {{ event.creator.username }}
      </button>
      <p class="text-base text-main">
        {{ formattedCreatedAt }}
      </p>
    </div>
    <div
      class="
        absolute bottom-1.5 right-1.5
        w-8 h-8
        bg-main rounded-full 
      "
      :style="ringStyle"
      :title="`Participants: ${participantsLabel}`"
    >
      <div
        class="
          absolute
          top-2/4 left-2/4 -translate-2/4 
          w-[calc(100%-6px)] h-[calc(100%-6px)] 
          bg-primary rounded-full
        "
      >
      </div>
    </div>
  </li>
</template>

<style lang="scss">

  

</style>
