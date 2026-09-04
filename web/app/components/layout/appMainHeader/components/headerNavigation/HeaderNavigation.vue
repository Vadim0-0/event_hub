<script setup lang="ts">
  import { storeToRefs } from 'pinia';
  import type { HeaderNavigation } from '../../../../../types/i18n/components/mainHeader';

  defineProps<HeaderNavigation & { collapsed?: boolean }>()

  const emit = defineEmits<{
    navigate: [];
  }>();

  const localePath = useLocalePath();
  const messagingStore = useMessagingStore();
  const { unreadTotal } = storeToRefs(messagingStore);

  function unreadBadgeLabel(count: number) {
    if (count > 99) return '99';
    return String(count);
  };

  function onNavClick() {
    emit('navigate');
  }

</script>

<template>
  <nav
    class="flex flex-col gap-1"
  >
    <NuxtLink
      v-for="btn in navigation"
      :key="btn.id"
      :to="localePath(btn.to)"
      class="
        relative
        group
        flex items-center gap-2
        overflow-hidden
        py-2.5 px-2
        rounded-sm
        hover:bg-primary-light
      "
      active-class="active !bg-primary"
      :class="collapsed ? 'justify-center max-sm:py-2' : 'max-sm:py-2'"
      @click="onNavClick"
    >
      <span
        v-if="btn.id === 'chatsPage' && unreadTotal > 0"
        class="
          absolute top-0.5 right-0.5 z-1
          flex items-center justify-center p-1 min-w-5 h-5 bg-primary rounded-sm
          text-main text-xs font-medium
          transition-all duration-300 ease-in-out

          group-[.active]:bg-third group-[.active]:text-text-main
        "
      >
        {{ unreadBadgeLabel(unreadTotal) }}
      </span>
      <Icon
        :name="btn.icon"
        class="
          shrink-0
          size-6 text-text-main
          transition-all transition-300 ease-in-out
          group-[.active]:text-main
          max-sm:size-5
        "
      />
      <p
        v-show="!collapsed"
        class="
          whitespace-nowrap
          text-body-xl text-text-main
          transition-all transition-300 ease-in-out
          group-[.active]:text-main
          max-sm:text-body-sm
        "
      >
        {{ btn.text }}
      </p> 
    </NuxtLink>
  </nav>
</template>

<style scoped lang="scss">

  

</style>