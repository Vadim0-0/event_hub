<script setup lang="ts">

  const page = defineModel<number>('page', { required: true });
  const props = defineProps<{ totalPages: number }>();

  const items = computed(() => getPaginationItems(page.value, props.totalPages));

  function goTo(next: number) {
    if (next >= 1 && next <= props.totalPages) page.value = next
  };


</script>

<template>
  <div class="flex items-center justify-center gap-3">
    <button 
      class="pagination__btn rotate-180"
      :disabled="page <= 1"
      @click="goTo(page - 1)"
      >
      <Icon name="weui:arrow-outlined" class="size-7 text-text-main" />
    </button>
    <div class="flex items-center gap-2">
      <template v-for="(item, index) in items" :key="`${item}-${index}`">
        <span v-if="item === 'ellipsis'" class="px-1 text-text-main">...</span>

        <button
          v-else
          class="pagination__btn"
          :class="{ active: item === page }"
          @click="goTo(item)"
        >
          {{ item }}
        </button>
      </template>
    </div>
    <button 
      class="pagination__btn"
      :disabled="page >= totalPages"
      @click="goTo(page + 1)"
    >
      <Icon name="weui:arrow-outlined" class="size-7 text-text-main" />
    </button>
  </div>
</template>

<style scoped lang="scss">

  .pagination__btn {
    display: flex;
    align-items: center;
    justify-content: center;

    padding: 2px;
    width: 28px;
    height: 28px;

    border-radius: 5px;

    font-size: 16px;
    font-weight: 500;
    line-height: 100%;
    color: var(--color-text-main);

    &.active {
      background-color: var(--color-primary-light);
    }
  }

</style>