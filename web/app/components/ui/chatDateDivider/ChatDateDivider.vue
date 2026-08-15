<script setup lang="ts">

  defineProps<{ label: string }>(); 

</script>

<template>
  <div 
    class="flex justify-center w-full mb-4"
  >
    <div 
      class="
        flex flex-col items-end gap-1 max-w-3/5
        p-2 px-4 rounded-sm bg-third
      "
    >
      <p 
        class="w-full text-text-main text-body-sm font-medium"
      >
        {{ label }}
      </p>
    </div>
  </div>
</template>

<style scoped lang="scss">

</style>