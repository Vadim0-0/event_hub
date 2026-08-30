<script setup lang="ts">

  import allEventsPageRaw from '~~/data/pages/events/allEventsPage.json'
  import myEventsPageRaw from '~~/data/pages/events/myEventsPage.json'
  import joinedEventsPageRaw from '~~/data/pages/events/joinedEventsPage.json'
  import historyEventsPageRaw from '~~/data/pages/events/historyEventsPage.json'
  import usersPageRaw from '~~/data/pages/events/usersPage.json'
  
  import { mapAllEventsPage } from '~/mappers/pages/events/allEventsPage';
  import { mapMyEventsPage } from '~/mappers/pages/events/myEventsPage';
  import { mapJoinedEventsPage } from '~/mappers/pages/events/joinedEventsPage';
  import { mapHistoryEventsPage } from '~/mappers/pages/events/historyEventsPage';
  import { mapUsersPage } from '~/mappers/pages/events/usersPage';

  import type { AllEventsPageRaw } from '~/types/i18n/pages/events/allEventsPage';
  import type { MyEventsPageRaw } from '~/types/i18n/pages/events/myEventsPage';
  import type { JoinedEventsPageRaw } from '~/types/i18n/pages/events/joinedEventsPage';
  import type { HistoryEventsPageRaw } from '~/types/i18n/pages/events/historyEventsPage';
  import type { UsersPageRaw } from '~/types/i18n/pages/events/usersPage';
  import type { MappedLoadMoreBtn } from '~/types/i18n/pages/events/loadMoreBtn';


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
    loadMoreBtn: MappedLoadMoreBtn
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
  });

  useHead({
    title: computed(() => pageContent.value?.title ?? pageConfig.value.title),
  });


  // --- Filters ---
  const {
    search,
    sort,
    debouncedSearch,
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
    pending,
    error,
    hasMore: eventsHasMore,
    isLoadingMore: eventsIsLoadingMore,
    loadMore: loadMoreEvents,
    PAGE_SIZE: eventsPageSize,
  } = useEventsList(isAllEventsPage, debouncedSearch, sort);

  const {
    events: myEvents,
    total: myTotal,
    pending: myPending,
    error: myError,
    hasMore: myEventsHasMore,
    isLoadingMore: myEventsIsLoadingMore,
    loadMore: loadMoreMyEvents,
    PAGE_SIZE: myEventsPageSize,
  } = useMyEventsList(isMyEventsPage, debouncedSearch, sort);

  const {
    events: joinedEvents,
    total: joinedTotal,
    pending: joinedPending,
    error: joinedError,
    hasMore: joinedEventsHasMore,
    isLoadingMore: joinedEventsIsLoadingMore,
    loadMore: loadMoreJoinedEvents,
    PAGE_SIZE: joinedEventsPageSize,
  } = useJoinedEventsList(isJoinedEventsPage, debouncedSearch, sort);

  const {
    events: historyEvents,
    total: historyTotal,
    pending: historyPending,
    error: historyError,
    hasMore: historyEventsHasMore,
    isLoadingMore: historyEventsIsLoadingMore,
    loadMore: loadMoreHistoryEvents,
    PAGE_SIZE: historyEventsPageSize,
  } = useHistoryEventsList(isHistoryEventsPage, debouncedSearch, sort);


  // --- Users data ---
  const {
    users,
    total: usersTotal,
    pending: usersPending,
    error: usersError,
    hasMore: usersHasMore,
    isLoadingMore: usersIsLoadingMore,
    loadMore: loadMoreUsers,
    PAGE_SIZE: usersPageSize,
  } = useUsersList(isUsersPage, debouncedSearch);


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

  const activeHasMore = computed(() => {
    if (isAllEventsPage.value) return eventsHasMore.value;
    if (isMyEventsPage.value) return myEventsHasMore.value;
    if (isJoinedEventsPage.value) return joinedEventsHasMore.value;
    if (isHistoryEventsPage.value) return historyEventsHasMore.value;
    return false;
  });

  const activeIsLoadingMore = computed(() => {
    if (isAllEventsPage.value) return eventsIsLoadingMore.value;
    if (isMyEventsPage.value) return myEventsIsLoadingMore.value;
    if (isJoinedEventsPage.value) return joinedEventsIsLoadingMore.value;
    if (isHistoryEventsPage.value) return historyEventsIsLoadingMore.value;
    return false;
  });

  const activePageSize = computed(() => {
    if (isAllEventsPage.value) return eventsPageSize;
    if (isMyEventsPage.value) return myEventsPageSize;
    if (isJoinedEventsPage.value) return joinedEventsPageSize;
    if (isHistoryEventsPage.value) return historyEventsPageSize;
    return eventsPageSize;
  });

  function loadMoreActive() {
    if (isAllEventsPage.value) void loadMoreEvents();
    else if (isMyEventsPage.value) void loadMoreMyEvents();
    else if (isJoinedEventsPage.value) void loadMoreJoinedEvents();
    else if (isHistoryEventsPage.value) void loadMoreHistoryEvents();
  }

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


  const showCreateEventButton = computed(() =>
    isAllEventsPage.value ||
    isMyEventsPage.value ||
    isJoinedEventsPage.value,
  );

</script>

<template>
  <section
    class="
      relative flex flex-col flex-1 py-10 pb-2
      bg-fourth
      max-md:py-5 max-md:pb-2
    "
  >
    <div 
      class="
        relative
        container mx-auto flex flex-col flex-1 px-8
        max-md:px-4
        max-sm:px-3
      "
    >
      <div class="mb-3 max-lg:mb-2">
        <h1
          class="
            text-4xl font-semibold text-text-main 
            max-lg:text-3xl
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
          max-sm:mb-2 max-sm:px-2 max-sm:py-1
        "
      >
        <Icon 
          name="material-symbols:search-rounded"
          class="shrink-0 size-8 text-fifth max-sm:size-7"
        />
        <UiInput 
          v-model="search"
          type="search"
          placeholder="Search..."
          input-class="
           !bg-transparent !py-2
           max-sm:!py-1.5
          "
        />
      </div>
      <div 
        class="
          flex items-center justify-between gap-2
          max-sm:mb-3
        "
        :class="hasUsers ? 'mb-3' : ''"
      >
        <div
          class="
            text-text-main text-body-xl
            max-sm:text-body-sm
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
          <UiButton @click="toggleSort" style-type="cancel" class="leading-none">
            <Icon 
              :name="sortIcon"
              class="size-5 text-text-main"
              mode="svg"
            />
            {{ pageContent?.sortingButtonText }}
          </UiButton>
        </div>
      </div>
      <div 
        class="
          relative flex-1 overflow-y-auto overflow-x-hidden
          max-sm:
        " 
        
        data-lenis-prevent>
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
              grid grid-cols-6 gap-4 p-4 pb-20
              z-2
              max-2xl:grid-cols-5
              max-xl:grid-cols-4
              max-lg:grid-cols-3 max-lg:gap-3
              max-md:grid-cols-2 max-md:gap-2
              max-sm:relative max-sm:grid-cols-1 max-sm:p-0 max-sm:pb-12
            "
          >
            <EventCard 
              v-for="(event, index) in activeEvents"
              :key="event.id"
              :event="event"
              :index="index % activePageSize"
            />

            <UiButton
              v-if="activeHasMore || activeIsLoadingMore"
              key="events-load-more"
              class="
                !p-2.5
                col-span-6
                max-2xl:col-span-5
                max-xl:col-span-4
                max-lg:col-span-3
                max-md:col-span-2
                max-sm:col-span-1 max-sm:p-1.5
              "
              :disabled="activeIsLoadingMore"
              @click="loadMoreActive"
            >
              {{ activeIsLoadingMore ? pageContent?.loadMoreBtn.loading : pageContent?.loadMoreBtn.loadMore }}
              <Icon
                name="fluent:arrow-sync-24-filled"
                mode="svg"
                class="size-6"
                :class="{ 'animate-spin': activeIsLoadingMore }"
              />
            </UiButton>
          </TransitionGroup>
        </template>

        <template v-else-if="hasUsers">
          <TransitionGroup
            tag="ul"
            name="user-card"
            appear
            class="
              absolute top-0 left-0 w-full pb-20
              flex flex-col gap-2.5
              z-2
              max-sm:relative max-sm:gap-2 max-sm:pb-12
            "
          >
            <UserCard
              v-for="(user, index) in users"
              :key="user.id"
              :user="user"
              :index="index % usersPageSize"
              :load-more-btn="pageContent!.loadMoreBtn"
            />

            <UiButton
              v-if="usersHasMore || usersIsLoadingMore"
              key="users-load-more"
              class="
                !p-2.5
                col-span-6
                max-2xl:col-span-5
                max-xl:col-span-4
                max-lg:col-span-3
                max-md:col-span-2
                max-sm:col-span-1 max-sm:p-1.5
              "
              :disabled="usersIsLoadingMore"
              @click="loadMoreUsers"
            >
              {{ usersIsLoadingMore ? pageContent?.loadMoreBtn.loading : pageContent?.loadMoreBtn.loadMore }}
              <Icon
                name="fluent:arrow-sync-24-filled"
                mode="svg"
                class="size-6"
                :class="{ 'animate-spin': usersIsLoadingMore }"
              />
            </UiButton>
          </TransitionGroup>
        </template>
      </div>
      <div 
        class="
          absolute bottom-4 right-0 z-10 mx-12
          max-sm:fixed max-sm:bottom-1 max-sm:mx-3
        ">
        <LayoutEventsFloatingActions :show-create-button="showCreateEventButton" />
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

  .user-card-enter-active {
    transition:
      opacity 0.4s ease,
      transform 0.4s ease;
    transition-delay: var(--delay, 0ms);
  }
  .user-card-enter-from {
    opacity: 0;
    transform: translateY(20px) scale(0.9);
  }

  .user-card-move {
    transition: transform 0.4s ease;
  }

  .user-card-leave-active {
    transition: opacity 0.25s ease, transform 0.25s ease;
    position: absolute;
    width: 100%;
  }
  .user-card-leave-to {
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