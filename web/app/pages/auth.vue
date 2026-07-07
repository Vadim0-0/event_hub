<script setup lang="ts">
  definePageMeta({
    layout: 'auth',
  })

  const mode = ref<'login' | 'register'>('login')

</script>

<template>
  <div class="flex flex-1">
    <div class="container mx-auto px-4 flex flex-1 items-center justify-center">
      <div class="w-full max-w-4xl p-5 rounded-2xl bg-primary-light ">
        <AuthLogin v-if="mode === 'login'" @switch-to-register="mode = 'register'"/>
        <AuthRegister v-else @switch-to-login="mode = 'login'"/>
      </div>
    </div>
  </div>
</template>

<style scoped lang="scss">

</style>