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
      "
      :class="isMine ? 'bg-primary' : 'bg-third'"
    >
      <p 
        class="w-full text-body-sm font-medium"
        :class="isMine ? 'text-main' : 'text-text-main'"
      >
        {{ body }}
      </p>
      <p 
        class="text-sm whitespace-nowrap"
        :class="isMine ? 'text-secondary ' : 'text-text-main'"
      >
        {{ time }}
      </p>
    </div>
  </div>
</template>

<style scoped lang="scss">

</style>