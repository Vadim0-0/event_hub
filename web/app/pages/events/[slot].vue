<script setup lang="ts">
  // --- Meta ---
  definePageMeta({
    layout: 'main',
    requiresAuth: true,
  });

  // --- Route / page type ---
  const route = useRoute();
  const slot = computed(() => route.params.slot as string);
  const isAllEventsPage = computed(() => slot.value === 'allEventsPage');

  // --- Page Config ---
  const pageConfig = computed(() => {
    switch (slot.value) {
      case 'allEventsPage':
        return { title: 'All Events', showSearch: true, showSort: true }
      case 'myEventsPage':
        return { title: 'My Events', showSearch: false, showSort: true }
      default:
        return { title: 'Events', showSearch: false, showSort: false }
    }
  });

  // --- Filter & pagination
  const { 
    search, 
    sort, 
    debouncedSearch, 
    page, 
    toggleSort 
  } = useEventsFilters();

  // --- Data ---
  const { events, total, totalPages, pending, error } = useEventsList(
    page, 
    isAllEventsPage,
    debouncedSearch,
    sort,
  );

  // --- UI state ---
  const isErrorLoad = computed(() => !!error.value);

  const isEmpty = computed(() =>
    isAllEventsPage.value &&
    !pending.value &&
    !error.value &&
    (events.value?.length ?? 0) === 0,
  );

  const hasEvents = computed(() =>
    isAllEventsPage.value &&
    !pending.value &&
    !error.value &&
    (events.value?.length ?? 0) > 0,
  );

  const sortIcon = computed(() => {
    if (sort.value === 'asc') return 'fluent:arrow-sort-up-16-regular';
    if (sort.value === 'desc') return 'fluent:arrow-sort-down-16-regular';
    return 'fluent:arrow-sort-16-regular'
  });

</script>

<template>
  <section
    class="
      relative flex flex-col flex-1 py-10
      bg-fourth
    "
  >
    <div class="container mx-auto flex flex-col flex-1 px-8">
      <div class="mb-3">
        <h1
          class="
            text-4xl font-semibold text-text-main 
          "
        >
        {{ pageConfig.title }}
        </h1>
      </div>
      <div
        class="
          flex items-center gap-2
          px-2.5 py-1 mb-3
          bg-third rounded-sm
        "
      >
        <Icon 
          name="material-symbols:search-rounded"
          class="size-8 text-fifth"
        />
        <UiInput 
          v-model="search"
          type="search"
          placeholder="Search..."
          input-class="
           !bg-transparent !py-2
          "
        />
      </div>
      <div 
        class="
          flex items-center justify-between gap-2
          mb-3
        "
      >
        <div
          class="
            text-text-main text-body-xl
          "
        >
          <p v-if="isAllEventsPage">
            Events: <span>{{ total }}</span>
          </p>
        </div>

        <div>
          <UiButton @click="toggleSort">
            <Icon 
              :name="sortIcon"
              class="size-5 text-text-main"
            />
            Sorting
          </UiButton>
        </div>
      </div>
      <div class="relative flex-1">
        <div 
          v-if="isErrorLoad" 
          class="p-3 bg-error/10 rounded-sm">
          <p class="text-body-xl text-error">
            Loading error
          </p>
        </div>
        <div 
          v-if="isEmpty" 
          class="p-3 bg-primary-light rounded-sm">
          <p class="text-body-xl text-text-main">
            Empty
          </p>
        </div>
        <template v-else-if="isAllEventsPage && hasEvents">
          <ul
            class="
              absolute top-0 left-0 w-full
              grid grid-cols-6 gap-4
            "
          >
            <EventCard 
              v-for="event in events"
              :key="event.id"
              :event="event"
            />
          </ul>
        </template>
      </div>
      <div>
        <LayoutPagination 
          v-if="totalPages > 1"
          v-model:page="page"
          :total-pages="totalPages"
        />
      </div>
    </div>

  </section>
</template>

<style scoped lang="scss">

</style>