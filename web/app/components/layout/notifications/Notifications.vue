<script setup lang="ts">

  const notifications = useNotificationsStore();

  const barClassByType = {
    success: 'after:bg-success',
    error: 'after:bg-error',
  } as const;


</script>

<template>
  <TransitionGroup
    tag="ul"
    name="notification"
    class="absolute top-2.5 right-2.5 z-20 flex flex-col gap-2.5"
  >
    <li 
      v-for="item in notifications.items"
      :key="item.id"
      class="
        relative flex overflow-hidden
        p-4 pb-6 max-w-[500px] 
        rounded-xl shadow-lg bg-third
        after:content-[''] after:absolute after:bottom-0 after:left-0 after:h-1 after:w-full
      "
      :class="barClassByType[item.type]"
    >
      <div class="flex flex-col gap-2.5">
        <div class="">
          <h4 class=" text-2xl text-text-main font-semibold">
            {{ item.title }}
          </h4>
        </div>
        <div>
          <p class="text-body-xl text-text-main">
            {{ item.message }}
          </p>
        </div>
      </div>
    </li>
  </TransitionGroup>
</template>

<style>

  .notification-enter-active,
  .notification-leave-active {
    transition: opacity 0.3s ease, transform 0.3s ease;
  }

  .notification-enter-from,
  .notification-leave-to {
    opacity: 0;
    transform: translateX(20px);
  }

</style>