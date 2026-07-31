<script setup lang="ts">
  import allEventsRaw from '~~/data/pages/events/allEvents.json';
  import type { AllEventsPageRaw } from '~/types/allEventsPage';

  // --- Meta ---
  definePageMeta({
    layout: 'main',
    requiresAuth: true,
  });

  // --- Route / page type ---
  const route = useRoute();
  const slot = computed(() => route.params.slot as string);
  const isAllEventsPage = computed(() => slot.value === 'allEventsPage');
  const isMyEventsPage = computed(() => slot.value === 'myEventsPage');
  const isJoinedEventsPage = computed(() => slot.value === 'joinedEventsPage');

  // --- Page Config ---
  const pageConfig = computed(() => {
    switch (slot.value) {
      case 'allEventsPage':
        return { title: 'All Events', showSearch: true, showSort: true };
      case 'myEventsPage':
        return { title: 'My Events', showSearch: true, showSort: true };
      case 'joinedEventsPage':
        return { title: 'Joined Events', showSearch: true, showSort: true };
      default:
        return { title: 'Events', showSearch: false, showSort: false };
    };
  });

  // --- Page Content ---
  const { locale } = useI18n();
  const allEventsPageData = (allEventsRaw as AllEventsPageRaw[])[0]!;

  const pageContent = computed(() => {
    if (slot.value === 'allEventsPage') {
      return mapAllEventsPage(allEventsPageData, locale.value)
    }
    return null
  });

  useHead({
    title: computed(() => pageContent.value?.title ?? pageConfig.value.title),
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

  const {
    events: myEvents,
    total: myTotal,
    totalPages: myTotalPages,
    pending: myPending,
    error: myError,
  } = useMyEventsList(page, isMyEventsPage, debouncedSearch, sort);

  const {
    events: joinedEvents,
    total: joinedTotal,
    totalPages: joinedTotalPages,
    pending: joinedPending,
    error: joinedError,
  } = useJoinedEventsList(page, isJoinedEventsPage, debouncedSearch, sort);


  const activeEvents = computed(() => {
    if (isAllEventsPage.value) return events.value;
    if (isMyEventsPage.value) return myEvents.value;
    return joinedEvents.value;
  });

  const activeTotal = computed(() => {
    if (isAllEventsPage.value) return total.value;
    if (isMyEventsPage.value) return myTotal.value;
    return joinedTotal.value;
  });

  const activeTotalPages = computed(() =>
    isAllEventsPage.value ? totalPages.value : myTotalPages.value,
  );

  const activePending = computed(() =>
    isAllEventsPage.value ? pending.value : myPending.value,
  );

  const activeError = computed(() =>
    isAllEventsPage.value ? error.value : myError.value,
  );

  const isEventsListPage = computed(() =>
    isAllEventsPage.value || isMyEventsPage.value || isJoinedEventsPage.value,
  );

  const isErrorLoad = computed(() => !!activeError.value);

  const isEmpty = computed(() =>
    isEventsListPage.value &&
    !activePending.value &&
    !activeError.value &&
    (activeEvents.value?.length ?? 0) === 0,
  );

  const hasEvents = computed(() =>
    isEventsListPage.value &&
    !activePending.value &&
    !activeError.value &&
    (activeEvents.value?.length ?? 0) > 0,
  );

  const sortIcon = computed(() => {
    if (sort.value === 'asc') return 'fluent:arrow-sort-up-16-regular';
    if (sort.value === 'desc') return 'fluent:arrow-sort-down-16-regular';
    return 'fluent:arrow-sort-16-regular'
  });

  // EventSetup
  const eventSetupStore = useEventSetupStore();
  const selectedEventStore = useSelectedEventStore();

  function openCreateEvent() {
    selectedEventStore.close();
    eventSetupStore.openCreate();
  };

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
          {{ pageContent?.title ?? pageConfig.title }}
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
          <p v-if="isEventsListPage">
            {{ pageContent?.infoText ?? 'Events:' }} <span>{{ activeTotal }}</span>
          </p>
        </div>

        <div>
          <UiButton @click="toggleSort" style-type="cancel">
            <Icon 
              :name="sortIcon"
              class="size-5 text-text-main"
              mode="svg"
            />
            {{ pageContent?.sortingButtonText  ?? 'Sorting'}}
          </UiButton>
        </div>
      </div>
      <div class="relative flex-1">
        <div 
          v-if="isErrorLoad" 
          class="p-3 bg-error/10 rounded-sm">
          <p class="text-body-xl text-error">
            {{ pageContent?.loadingErrorText ?? 'Loading error' }}
          </p>
        </div>
        <div 
          v-if="isEmpty" 
          class="p-3 bg-primary-light rounded-sm">
          <p class="text-body-xl text-text-main">
            {{ pageContent?.emptyText ?? 'Empty' }}
          </p>
        </div>
        <template v-else-if="hasEvents">
          <TransitionGroup
            tag="ul"
            name="event-card"
            appear
            class="
              absolute top-0 left-0 w-full
              grid grid-cols-6 gap-4
              z-2
            "
          >
            <EventCard 
              v-for="(event, index) in activeEvents"
              :key="event.id"
              :event="event"
              :index="index"
            />
          </TransitionGroup>
        </template>

        <UiButton
          v-if="isAllEventsPage || isMyEventsPage || isJoinedEventsPage"
          @click="openCreateEvent"
          class="
            absolute z-3 bottom-0.5 right-0.5
            w-11 h-11
          "
        >
          <Icon name="line-md:plus" mode="svg" class="w-full h-full"/>
        </UiButton>
      </div>
      <div>
        <LayoutPagination 
          v-if="activeTotalPages > 1"
          v-model:page="page"
          :total-pages="activeTotalPages"
        />
      </div>
    </div>

  </section>
</template>

<style scoped lang="scss">
  // Visible
  .event-card-enter-active {
    transition:
      opacity 0.4s ease,
      transform 0.4s ease;
    transition-delay: var(--delay, 0ms);
  }
  .event-card-enter-from {
    opacity: 0;
    transform: translateY(20px) scale(0.9);
  }

  // Sorting Change
  .event-card-move {
    transition: transform 0.4s ease;
  }

  // Delete Card
  .event-card-leave-active {
    transition: opacity 0.25s ease, transform 0.25s ease;
    position: absolute; 
  }
  .event-card-leave-to {
    opacity: 0;
    transform: scale(0.95);
  }

</style>