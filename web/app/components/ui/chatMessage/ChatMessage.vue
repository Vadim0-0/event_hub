<script setup lang="ts">

  defineProps<{
    body: string
    isMine: boolean
    time: string
  }>();

</script>

<template>
  <div 
    class="flex w-full"
    :class="isMine ? 'justify-end' : 'justify-start'"
  >
    <div 
      class="
        flex flex-col items-end gap-1 max-w-3/5 min-w-52
        p-2 rounded-sm

        max-sm:p-1 
      "
      :class="isMine ? 'bg-primary' : 'bg-third my-1.5'"
    >
      <p 
        class="w-full text-body-sm font-medium max-sm:text-sm"
        :class="isMine ? 'text-main' : 'text-text-main'"
      >
        {{ body }}
      </p>
      <p 
        class="text-sm whitespace-nowrap max-sm:text-xs"
        :class="isMine ? 'text-secondary ' : 'text-text-main'"
      >
        {{ time }}
      </p>
    </div>
  </div>
</template>

<style scoped lang="scss">

</style>