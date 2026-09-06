<script setup lang="ts">
  import NotificationItem from './NotificationItem.vue';

  const notifications = useNotificationsStore();

  const barClassByType = {
    success: 'after:bg-success',
    error: 'after:bg-error',
    info: 'after:bg-primary',
  } as const;

</script>

<template>
  <TransitionGroup
    v-if="notifications.items.length"
    tag="ul"
    name="notification"
    class="
      fixed top-0 right-0 z-60 flex flex-col gap-2.5 w-full max-w-125 p-2.5
      max-xl:max-w-100
      max-sm:max-w-full max-sm:gap-1
    "
  >
    <NotificationItem
      v-for="item in notifications.items"
      :key="item.id"
      :item="item"
      :bar-class="barClassByType[item.type]"
    />
  </TransitionGroup>
</template>

<style scoped>

  .notification-enter-active,
  .notification-leave-active {
    transition: opacity 0.25s ease, transform 0.25s ease;
  }

  .notification-enter-from,
  .notification-leave-to {
    opacity: 0;
    transform: translateX(20px);
  }

  .notification-leave-active {
    position: absolute;
    width: calc(100% - 1.25rem);
    max-width: inherit;
  }

</style>
