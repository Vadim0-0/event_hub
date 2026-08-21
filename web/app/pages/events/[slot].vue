<script setup lang="ts">

  import allEventsPageRaw from '~~/data/pages/events/allEventsPage.json'
  import myEventsPageRaw from '~~/data/pages/events/myEventsPage.json'
  import joinedEventsPageRaw from '~~/data/pages/events/joinedEventsPage.json'
  import historyEventsPageRaw from '~~/data/pages/events/historyEventsPage.json'
  import usersPageRaw from '~~/data/pages/events/usersPage.json'
  
  import { mapAllEventsPage } from '~/mappers/allEventsPage';
  import { mapMyEventsPage } from '~/mappers/myEventsPage';
  import { mapJoinedEventsPage } from '~/mappers/joinedEventsPage';
  import { mapHistoryEventsPage } from '~/mappers/historyEventsPage';
  import { mapUsersPage } from '~/mappers/usersPage';

  import type { AllEventsPageRaw } from '~/types/allEventsPage';
  import type { MyEventsPageRaw } from '~/types/myEventsPage';
  import type { JoinedEventsPageRaw } from '~/types/joinedEventsPage';
  import type { HistoryEventsPageRaw } from '~/types/historyEventsPage';
  import type { UsersPageRaw } from '~/types/usersPage';


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
  const isUsersPage = computed(() => slot.value === 'usersPage');
  const isHistoryEventsPage = computed(() => slot.value === 'historyEventsPage');

  const isEventsListPage = computed(() =>
    isAllEventsPage.value ||
    isMyEventsPage.value ||
    isJoinedEventsPage.value ||
    isHistoryEventsPage.value,
  );


  // --- Page config ---
  const pageConfig = computed(() => {
    switch (slot.value) {
      case 'allEventsPage':
        return { title: 'All Events', showSearch: true, showSort: true };
      case 'myEventsPage':
        return { title: 'My Events', showSearch: true, showSort: true };
      case 'joinedEventsPage':
        return { title: 'Joined Events', showSearch: true, showSort: true };
      case 'historyEventsPage':
        return { title: 'History', showSearch: true, showSort: true };
      case 'usersPage':
        return { title: 'Users', showSearch: true, showSort: false };
      default:
        return { title: 'Events', showSearch: false, showSort: false };
    }
  });

  type EventsSlotPageContent = {
    title: string
    infoText: string
    emptyText: string
    loadingErrorText: string
    sortingButtonText?: string
  };


  // --- Page content (i18n) ---
  const { locale } = useI18n();
  const allEventsPageData = (allEventsPageRaw as AllEventsPageRaw[])[0]!;

  const pageContent = computed((): EventsSlotPageContent | null => {
    switch (slot.value) {
      case 'allEventsPage':
        return mapAllEventsPage(
          (allEventsPageRaw as AllEventsPageRaw[])[0]!,
          locale.value,
        )
      case 'myEventsPage':
        return mapMyEventsPage(
          (myEventsPageRaw as MyEventsPageRaw[])[0]!,
          locale.value,
        )
      case 'joinedEventsPage':
        return mapJoinedEventsPage(
          (joinedEventsPageRaw as JoinedEventsPageRaw[])[0]!,
          locale.value,
        )
      case 'historyEventsPage':
        return mapHistoryEventsPage(
          (historyEventsPageRaw as HistoryEventsPageRaw[])[0]!,
          locale.value,
        )
      case 'usersPage':
        return mapUsersPage(
          (usersPageRaw as UsersPageRaw[])[0]!,
          locale.value,
        )
      default:
        return null
    }
  })

  useHead({
    title: computed(() => pageContent.value?.title ?? pageConfig.value.title),
  });


  // --- Filters & pagination ---
  const {
    search,
    sort,
    debouncedSearch,
    page,
    toggleSort,
  } = useEventsFilters();

  const sortIcon = computed(() => {
    if (sort.value === 'asc') return 'fluent:arrow-sort-up-16-regular';
    if (sort.value === 'desc') return 'fluent:arrow-sort-down-16-regular';
    return 'fluent:arrow-sort-16-regular';
  });


  // --- Events data ---
  const {
    events,
    total,
    totalPages,
    pending,
    error,
  } = useEventsList(page, isAllEventsPage, debouncedSearch, sort);

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

  const {
    events: historyEvents,
    total: historyTotal,
    totalPages: historyTotalPages,
    pending: historyPending,
    error: historyError,
  } = useHistoryEventsList(page, isHistoryEventsPage, debouncedSearch, sort);


  // --- Users data ---
  const {
    users,
    total: usersTotal,
    totalPages: usersTotalPages,
    pending: usersPending,
    error: usersError,
  } = useUsersList(page, isUsersPage, debouncedSearch);


  // --- Active events (all / my / joined) ---
  const activeEvents = computed(() => {
    if (isAllEventsPage.value) return events.value;
    if (isMyEventsPage.value) return myEvents.value;
    if (isJoinedEventsPage.value) return joinedEvents.value;
    if (isHistoryEventsPage.value) return historyEvents.value;
    return [];
  });

  const activeTotal = computed(() => {
    if (isAllEventsPage.value) return total.value;
    if (isMyEventsPage.value) return myTotal.value;
    if (isJoinedEventsPage.value) return joinedTotal.value;
    if (isHistoryEventsPage.value) return historyTotal.value;
    return 0;
  });

  const activeTotalPages = computed(() => {
    if (isAllEventsPage.value) return totalPages.value;
    if (isMyEventsPage.value) return myTotalPages.value;
    if (isJoinedEventsPage.value) return joinedTotalPages.value;
    if (isHistoryEventsPage.value) return historyTotalPages.value;
    return 1;
  });

  const activePending = computed(() => {
    if (isAllEventsPage.value) return pending.value;
    if (isMyEventsPage.value) return myPending.value;
    if (isJoinedEventsPage.value) return joinedPending.value;
    if (isHistoryEventsPage.value) return historyPending.value;
    return false;
  });

  const activeError = computed(() => {
    if (isAllEventsPage.value) return error.value;
    if (isMyEventsPage.value) return myError.value;
    if (isJoinedEventsPage.value) return joinedError.value;
    if (isHistoryEventsPage.value) return historyError.value;
    return null;
  });


  // --- Events UI flags ---
  const isErrorLoad = computed(() =>
    isEventsListPage.value && !!activeError.value,
  );

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


  // --- Users UI flags ---
  const usersIsError = computed(() =>
    isUsersPage.value && !!usersError.value,
  );

  const usersIsEmpty = computed(() =>
    isUsersPage.value &&
    !usersPending.value &&
    !usersError.value &&
    (users.value?.length ?? 0) === 0,
  );

  const hasUsers = computed(() =>
    isUsersPage.value &&
    !usersPending.value &&
    !usersError.value &&
    (users.value?.length ?? 0) > 0,
  );


  // --- EventSetup ---
  const eventSetupStore = useEventSetupStore();
  const selectedEventStore = useSelectedEventStore();

  function openCreateEvent() {
    selectedEventStore.close();
    eventSetupStore.openCreate();
  };


  // --- AI Chat ---
  const aiChatStore = useAiChatStore();

  function aiChatOpen(event: MouseEvent) {
    const rect = (event.currentTarget as HTMLElement).getBoundingClientRect()
    aiChatStore.open(rect)
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
          {{ pageContent?.title }}
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
            {{ pageContent?.infoText }} <span>{{ activeTotal }}</span>
          </p>
          <p v-else-if="isUsersPage">
            {{ pageContent?.infoText }} <span>{{ usersTotal }}</span>
          </p>
        </div>

        <div v-if="pageContent?.sortingButtonText">
          <UiButton @click="toggleSort" style-type="cancel">
            <Icon 
              :name="sortIcon"
              class="size-5 text-text-main"
              mode="svg"
            />
            {{ pageContent?.sortingButtonText }}
          </UiButton>
        </div>
      </div>
      <div class="relative flex-1">
        <div 
          v-if="isErrorLoad"
          class="p-3 bg-error/10 rounded-sm">
          <p class="text-body-xl text-error">
            {{ pageContent?.loadingErrorText }}
          </p>
        </div>
        <div 
          v-else-if="isEmpty"
          class="p-3 bg-primary-light rounded-sm">
          <p class="text-body-xl text-text-main">
            {{ pageContent?.emptyText }}
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

        <template v-else-if="hasUsers">
          <TransitionGroup
            tag="ul"
            name="user-card"
            appear
            class="
              absolute top-0 left-0 w-full
              flex flex-col gap-2.5
              z-2
            "
          >
            <UserCard
              v-for="(user, index) in users"
              :key="user.id"
              :user="user"
              :index="index"
            />
          </TransitionGroup>
        </template>

        <div class="
          absolute z-3 bottom-0.5 right-0.5
          flex gap-1
        ">
          <Transition name="ai-btn-hide">
            <UiButton
              v-if="!aiChatStore.isOpen"
              key="ai-chat-trigger"
              class="w-11 h-11"
              @click="aiChatOpen"
            >
              <Icon name="mingcute:ai-fill" mode="svg" class="size-full" />
            </UiButton>
          </Transition>
          <UiButton
            v-if="isAllEventsPage || isMyEventsPage || isJoinedEventsPage"
            @click="openCreateEvent"
            class="
              w-11 h-11
            "
          >
            <Icon name="line-md:plus" mode="svg" class="w-full h-full"/>
          </UiButton>
        </div>

      </div>
      <div>
        <LayoutPagination
          v-if="isUsersPage && usersTotalPages > 1"
          v-model:page="page"
          :total-pages="usersTotalPages"
        />
        <LayoutPagination
          v-else-if="isEventsListPage && activeTotalPages > 1"
          v-model:page="page"
          :total-pages="activeTotalPages"
        />
      </div>
    </div>

  </section>
</template>

<style scoped lang="scss">
  /* Enter */
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

  /* Move (sort/reorder) */
  .event-card-move {
    transition: transform 0.4s ease;
  }

  /* Leave */
  .event-card-leave-active {
    transition: opacity 0.25s ease, transform 0.25s ease;
    position: absolute;
  }
  .event-card-leave-to {
    opacity: 0;
    transform: scale(0.95);
  }

  /* AiChat Button */
  .ai-btn-hide-enter-active,
  .ai-btn-hide-leave-active {
    transition: opacity 0.2s ease, transform 0.2s ease;
  }

  .ai-btn-hide-enter-from,
  .ai-btn-hide-leave-to {
    opacity: 0;
    transform: scale(0.6);
  }
</style>