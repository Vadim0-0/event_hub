<script setup lang="ts">


  const notifications = useNotificationsStore();

  const barClassByType = {
    success: 'after:bg-success',
    error: 'after:bg-error',
    info: 'after:bg-primary',
  } as const;


</script>

<template>
  <TransitionGroup
    tag="ul"
    name="notification"
    class="
      fixed top-0 right-0 z-60 flex flex-col gap-2.5 w-full max-w-125 p-2.5
      max-xl:max-w-100
      max-sm:max-w-full max-sm:gap-1
    "
  >
    <li 
      v-for="item in notifications.items"
      :key="item.id"
      class="
        relative flex overflow-hidden
        p-4 pb-6 w-full
        rounded-xl shadow-xl bg-third
        after:content-[''] after:absolute after:bottom-0 after:left-0 after:h-1 after:w-full

        max-xl:p-3 max-xl:pb-5
        max-sm:p-2 max-sm:pb-3
      "
      :class="barClassByType[item.type]"
    >
      <div class="flex flex-col gap-2.5 max-sm:gap-1">
        <div class="">
          <h4 class=" text-2xl text-text-main font-semibold max-sm:text-xl">
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
  </TransitionGroup>
</template>

<style scoped>

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