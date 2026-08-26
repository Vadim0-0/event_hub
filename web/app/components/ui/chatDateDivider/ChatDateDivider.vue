<script setup lang="ts">

  defineProps<{ label: string }>(); 

</script>

<template>
  <div 
    class="flex justify-center w-full mb-4 max-sm:mt-2 max-sm:mb-2"
  >
    <div 
      class="
        flex flex-col items-end gap-1 max-w-3/5
        p-2 px-4 rounded-sm bg-primary-light
        max-sm:p-1 max-sm:px-4
      "
    >
      <p 
        class="w-full text-text-main text-body-sm font-medium max-sm:text-sm"
      >
        {{ label }}
      </p>
    </div>
  </div>
</template>

<style scoped lang="scss">

</style>