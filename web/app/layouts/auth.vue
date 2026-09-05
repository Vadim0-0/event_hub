<script setup lang="ts">

  const { locale, languageOptions, selectedLocale } = useLocaleSwitch();

</script>

<template>
  <main class="flex flex-col flex-1 h-dvh">
    <slot />
  </main>
  <div class="fixed left-2.5 bottom-2.5 w-52">
    <UiSelect
      v-model="selectedLocale"
      :options="languageOptions"
      list-layout="top"
    />
  </div>
</template>

<style scoped lang="scss">

</style>