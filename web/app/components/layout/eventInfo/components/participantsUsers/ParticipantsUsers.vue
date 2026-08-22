<script setup lang="ts">
  import type { Participant } from '~/types/domain/event';


  // --- Props & Emits ---
  const props = defineProps<{
    eventId: string
    totalCount?: number
    isCreator?: boolean
    readOnly?: boolean
  }>();

  const emit = defineEmits<{
    close: []
    'participant-removed': []
  }>();

  const api = useApi();


  // --- State ---
  const page = ref(1);
  const enabled = ref(true);
  const loadedParticipants = ref<Participant[]>([]);

  const copiedUserId = ref<number | null>(null);
  let resetTimer: ReturnType<typeof setTimeout> | null = null;

  const removingUserId = ref<number | null>(null);


  // --- Data ---
  const {
    participants,
    pending,
    error,
    refresh,
    PAGE_SIZE,
  } = useEventParticipantsList( computed(() => props.eventId),
    enabled,
    page,
  );

  // --- UI flags ---
  const isInitialLoading = computed(() => pending.value && page.value === 1);
  const isLoadingMore = computed(() => pending.value && page.value > 1);

  const isEmpty = computed(() =>
    !pending.value &&
    !error.value &&
    loadedParticipants.value.length === 0,
  );

  const hasMore = computed(() =>
    loadedParticipants.value.length < (props.totalCount ?? 0),
  );

  const hoveredUserId = ref<number | null>(null)

  const {
    onBeforeEnter,
    onEnter,
    onAfterEnter,
    onBeforeLeave,
    onLeave,
  } = useHeightTransition({
    duration: 300,
    marginTop: 10,
    animateOpacity: true,
  });

  const openedUserId = ref<number | null>(null);
  function toggleActions(id: number) {
    openedUserId.value = openedUserId.value === id ? null : id
  };

  const selectedEventStore = useSelectedEventStore();

  const canRemoveParticipants = computed(() => props.isCreator && !props.readOnly);


  // --- Sync API data → accumulated list ---
  watch(participants, (newData) => {
    if (!newData) return;

    if (page.value === 1) {
      loadedParticipants.value = newData;
    } else {
      loadedParticipants.value = [...loadedParticipants.value, ...newData];
    };
  });

  watch(() => props.eventId, () => {
    page.value = 1;
    loadedParticipants.value = [];
  });

  onUnmounted(() => {
    if (resetTimer) clearTimeout(resetTimer);
  });


  // --- Handlers ---
  function loadMore() {
    if (pending.value || !hasMore.value) return;
    page.value++;
  };

  async function copyParticipantEmail(participant: Participant) {
    const email = participant.user.email;
    if (!email) return;

    await navigator.clipboard.writeText(email);
    copiedUserId.value = participant.user.id;
    
    if (resetTimer) clearTimeout(resetTimer);
    resetTimer = setTimeout(() => {
      copiedUserId.value = null;
    }, 1000);
  };

  async function removeParticipant(participant: Participant) {
    if (!canRemoveParticipants.value) return;
    if (removingUserId.value) return;

    removingUserId.value = participant.user.id;
    try {
      await api(`/events/${props.eventId}/participants/${participant.user.id}`, {
        method: 'DELETE',
      });

      loadedParticipants.value = loadedParticipants.value.filter(
        (p) => p.user.id !== participant.user.id,
      );

      emit('participant-removed');
    } catch {
      // toast / alert
    } finally {
      removingUserId.value = null;
    }
  };

  function goToUserPage(participant: Participant) {
    selectedEventStore.close();

    navigateTo({
      path: '/events/usersPage',
      query: { search: participant.user.email },
    });
  };


</script>

<template>
  <div class="
    relative
    flex flex-col h-full
    px-5 py-5
    bg-main rounded-l-lg
  ">
    <button
      type="button"
      @click="emit('close')"
      class="
        absolute top-2/4 transform -translate-y-2/4 left-0
        flex items-center justify-center py-2 rounded-r-sm
        bg-third
      "
    >
      <Icon
        name="weui:arrow-outlined"
        class="size-6 text-text-main"
      />
    </button>

    <div class="flex flex-col gap-5 mb-5">
      <h3 class="text-3xl font-semibold text-text-main">
        Participants Users
      </h3>
    </div>

    <div class="max-w-full overflow-y-auto">

      <div 
        v-if="isInitialLoading"
        class="p-3 bg-primary-light rounded-sm">
        <p class="text-body-xl text-text-main">
          Loading...
        </p>
      </div>

      <div 
        v-else-if="error"
        class="p-3 bg-error/10 rounded-sm">
        <p class="text-body-xl text-error">
          Error
        </p>
      </div>

      <div 
        v-else-if="isEmpty"
        class="p-3 bg-primary-light rounded-sm">
        <p class="text-body-xl text-text-main">
          Empty
        </p>
      </div>

      <ul v-else class="flex flex-col gap-1.5">
        <li 
          v-for="participant in loadedParticipants"
          :key="participant.user.id"
          class="
            overflow-hidden p-2
            bg-primary rounded-md cursor-pointer
            transition-all transition-300 ease-in-out
            hover:shadow-[0px_-3px_21px_-2px_rgba(46,46,46,0.15)]
          "
          @mouseenter="hoveredUserId = participant.user.id"
          @mouseleave="hoveredUserId = null"
        >
          <div 
            @click="goToUserPage(participant)"
            class="flex items-center gap-2"
          >
            <div 
              class="
                flex items-center justify-center overflow-hidden rounded-[50%] flex-shrink-0 w-10 h-10
                bg-main border-r-2 border-solid border-third
              "
            >
              <svg 
                class="w-[90%] h-[90%] fill-text-main"
                xmlns="http://www.w3.org/2000/svg" width="1em" height="1em" viewBox="0 0 32 32">
                <path d="M0 0h32v32H0z" fill="none" />
                <g fill="">
                  <path d="m15.287 17.527l-.99 3.17a1.005 1.005 0 0 0 .97 1.303h1.466c.688 0 1.173-.662.97-1.304l-.99-3.17c-.213-.701-1.203-.701-1.426 0m-1.87 5.757c.747.39 1.637.612 2.583.612c.956 0 1.836-.222 2.583-.612c.256-.13.53.148.369.39A3.53 3.53 0 0 1 16 25.25a3.53 3.53 0 0 1-2.952-1.577c-.16-.232.114-.52.369-.39M11.542 15.4c-1.214 0-2.24.84-2.527 1.967a.512.512 0 0 0 .503.633h.8a1.664 1.664 0 1 1 3.209 0h.148a.428.428 0 0 0 .424-.504a2.61 2.61 0 0 0-2.557-2.096m8.916 0c1.214 0 2.24.84 2.527 1.967a.512.512 0 0 1-.503.633h-.8a1.664 1.664 0 0 0-1.61-2.108a1.65 1.65 0 0 0-1.658 1.665q0 .236.06.443h-.149a.428.428 0 0 1-.424-.504a2.6 2.6 0 0 1 2.557-2.096" />
                  <path d="M11.927 16.611a.947.947 0 0 1 .84 1.389h-1.679a1 1 0 0 1-.108-.443c0-.172.046-.334.127-.473a.295.295 0 0 0 .544-.164a.3.3 0 0 0-.105-.229a.95.95 0 0 1 .381-.08m7.347.421a.94.94 0 0 0-.16.525c0 .157.04.305.11.443h1.678a.947.947 0 0 0-1.182-1.325a.3.3 0 0 1-.17.545a.3.3 0 0 1-.276-.188m2.404-4.649c.575.181.955.483 1.282.767a.517.517 0 0 1-.68.78c-.293-.256-.543-.444-.913-.56c-.378-.12-.927-.176-1.824-.067a.517.517 0 1 1-.126-1.026c.983-.12 1.694-.072 2.26.106m-12.313.747l-.001.002a.517.517 0 0 0 .633.818l.005-.004l.03-.022q.045-.032.14-.09a4.14 4.14 0 0 1 2.585-.53a.517.517 0 1 0 .127-1.027a5.17 5.17 0 0 0-3.242.67a4 4 0 0 0-.253.166l-.016.012l-.006.004z" />
                  <path d="M27.415 8.07a4.33 4.33 0 0 0-2.363-1.96c-1.049-.36-1.949-1.05-2.522-2A4.34 4.34 0 0 0 18.822 2c-.604 0-1.177.13-1.701.35c-.712.31-1.513.31-2.225 0a4.5 4.5 0 0 0-1.71-.35c-1.553 0-2.908.82-3.68 2.05a5 5 0 0 1-2.58 2.07c-.164.058-.326.106-.487.155C5.62 6.52 4.836 6.758 4 8.07c-1 1.57-1.12 3.4-.23 4.71c.327.48.505 1.05.505 1.63l.001.67A4 4 0 0 0 3 18.01c0 1.161.494 2.206 1.284 2.937q-.013.519-.034 1.039c0 1.134.925 2.185 1.991 2.933a8.3 8.3 0 0 0 8.008 6.091h3.517a8.3 8.3 0 0 0 8.011-6.104c1.059-.748 1.973-1.792 1.973-2.92l-.002-1.07A4 4 0 0 0 29 18.01a4 4 0 0 0-1.287-2.939v-.661c0-.58.178-1.15.504-1.63c.94-1.35.068-3.18-.802-4.71M7.5 13.3c0-2.926 2.399-5.3 5.29-5.3h2.373a.24.24 0 0 1 .219.151l.007.018l.008.018a5.52 5.52 0 0 0 5.037 3.283h2.587a1.7 1.7 0 0 1 1.593 1.651l-.166 2.768l.887.149a2 2 0 0 1-.216 3.969l-.885.051l-.22 3.504a6.3 6.3 0 0 1-6.248 5.448H14.25A6.3 6.3 0 0 1 8 23.56l-.23-3.504l-.884-.05a2 2 0 0 1-.26-3.961l.254-.048l.62-.091z" />
                </g>
              </svg>
            </div>

            <div class="flex flex-col whitespace-nowrap overflow-hidden">
              <h4 class="text-main text-lg font-semibold leading-4">
                {{ participant.user.username }}
              </h4>
              <p class="text-main text-ml">
                {{ participant.user.email }}
              </p>
            </div>

            <button
              class="ml-auto w-10"
            >
              <Icon 
                name="material-symbols-light:face-right-rounded"
                mode="svg"
                class="w-full h-full text-main" />
            </button>
          </div>
          <Transition
            :css="false"
            @before-enter="onBeforeEnter"
            @enter="onEnter"
            @after-enter="onAfterEnter"
            @before-leave="onBeforeLeave"
            @leave="onLeave"
          >
            <div 
              v-if="hoveredUserId === participant.user.id"
              class="grid grid-cols-2 gap-2
              mt-2.5
              "
            >
              <UiButton @click="copyParticipantEmail(participant)" style-type="cancel">
                {{ copiedUserId === participant.user.id ? 'Copied' : 'Copy' }}
              </UiButton>
              <UiButton 
                v-if="isCreator"
                style-type="delete"
                :disabled="!canRemoveParticipants"
                @click="removeParticipant(participant)"
              >
                {{ removingUserId === participant.user.id ? 'Removing...' : 'Delete' }}
              </UiButton>
            </div>
          </Transition>
        </li>

        <li v-if="hasMore">
          <UiButton 
            class="w-full"
            :disabled="isLoadingMore"
            @click="loadMore"
          >
            <p>{{ isLoadingMore ? 'Loading...' : 'Load More' }}</p>
            <Icon name="fluent:arrow-sync-24-filled" mode="svg" class="size-6" :class="{ 'animate-spin': isLoadingMore }"/>
          </UiButton>
        </li>
      </ul>
    </div>

  </div>
</template>

<style scoped lang="scss">

</style>