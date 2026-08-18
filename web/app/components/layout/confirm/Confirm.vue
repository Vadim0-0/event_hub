<script setup lang="ts">

  const confirmStore = useConfirmStore();

</script>

<template>
  <div 
    v-if="confirmStore.isOpen && confirmStore.options"
    class="
      fixed top-0 left-0 z-100 w-full h-full
      flex flex-col items-center justify-center
      p-10
      bg-overlay
    "
    @click.self="confirmStore.close()"
  >
    <div 
      class="flex flex-col
        w-full max-w-[450px] min-h-[200px] p-4
        bg-main rounded-sm
      "
    > 
      <div class="flex flex-col gap-2 mb-10">
        <h3 class="text-xl leading-6 font-semibold text-text-main">
          {{ confirmStore.options.title }}
        </h3>
        <p class="text-lg font-normal text-text-secondary">
          {{ confirmStore.options.description }}
        </p>
      </div>
      
      <UiCheckbox
        v-if="confirmStore.options.showCheckbox"
        v-model="confirmStore.checkboxValue"
        class="mt-auto"
        :label="confirmStore.options.checkboxLabel"
      />

      <div class="grid grid-cols-2 gap-2 mt-3">
        <UiButton style-type="cancel" @click="confirmStore.close()">
          {{ confirmStore.options.cancelLabel ?? 'Cancel' }}
        </UiButton>
        <UiButton
          :style-type="confirmStore.options.variant === 'delete' ? 'delete' : 'primary'"
          :disabled="confirmStore.isLoading"
          @click="confirmStore.confirm()"
        >
          {{ confirmStore.options.confirmLabel }}
        </UiButton>
      </div>
    </div>
  </div>
</template>

<style scoped lang="scss">

</style>