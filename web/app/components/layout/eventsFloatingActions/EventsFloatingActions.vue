<script setup lang="ts">
  defineProps<{
    showCreateButton?: boolean
  }>();

  const aiChatStore = useAiChatStore();
  const eventSetupStore = useEventSetupStore();
  const selectedEventStore = useSelectedEventStore();

  function openAiChat(event: MouseEvent) {
    const rect = (event.currentTarget as HTMLElement).getBoundingClientRect();
    aiChatStore.open(rect);
  };

  function openCreateEvent() {
    selectedEventStore.close();
    eventSetupStore.openCreate();
  };
</script>

<template>
  <div 
    class="
      flex gap-1
      max-sm:right-1
    "
  >
    <Transition name="ai-btn-hide">
      <UiButton
        v-if="!aiChatStore.isOpen"
        key="ai-chat-trigger"
        class="w-11 h-11 shadow-[0_1px_2px_rgb(60_64_67/0.3),0_2px_6px_2px_rgb(60_64_67/0.15)]"
        @click="openAiChat"
      >
        <Icon name="mingcute:ai-fill" mode="svg" class="size-full" />
      </UiButton>
    </Transition>

    <UiButton
      v-if="showCreateButton"
      class="w-11 h-11 shadow-[0_1px_2px_rgb(60_64_67/0.3),0_2px_6px_2px_rgb(60_64_67/0.15)]"
      @click="openCreateEvent"
    >
      <Icon name="line-md:plus" mode="svg" class="w-full h-full" />
    </UiButton>
  </div>
</template>

<style scoped lang="scss">
  .ai-btn-hide-enter-active,
  .ai-btn-hide-leave-active {
    transition: opacity 0.2s ease, transform 0.2s ease;
  }

  .ai-btn-hide-enter-from,
  .ai-btn-hide-leave-to {
    opacity: 0;
    transform: scale(0.6);
  }
</style>