<script setup lang="ts">
  import type { HeaderNavigation } from '~/types/mainHeader';
  
  defineProps<HeaderNavigation & { collapsed?: boolean }>()

    const localePath = useLocalePath();


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
        group
        flex items-center gap-2
        overflow-hidden
        py-2.5 px-2
        rounded-sm
        hover:bg-primary-light
      "
      active-class="active !bg-primary"
      :class="collapsed ? 'justify-center' : ''"
    >
      <Icon
        :name="btn.icon"
        class="
          shrink-0
          size-6 text-text-main
          transition-all transition-300 ease-in-out
          group-[.active]:text-main
        "
      />
      <p
        v-show="!collapsed"
        class="
          whitespace-nowrap
          text-body-xl text-text-main
          transition-all transition-300 ease-in-out
          group-[.active]:text-main
        "
      >
        {{ btn.text }}
      </p> 
    </NuxtLink>
  </nav>
</template>

<style scoped lang="scss">

  

</style>