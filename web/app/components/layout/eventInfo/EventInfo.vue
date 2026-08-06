<script setup lang="ts">

  import type { Event, EventDetail } from '~/types/event';
  import { ParticipantsUsers } from './components';


  // --- Props & Emits ---
  const props = defineProps<{
    event: Event
  }>();

  const emit = defineEmits<{
    close: []
    updated: [event: EventDetail]
    edit: [event: Event]
  }>();


  // --- Composables ---
  const dayjs = useDayjs();
  const api = useApi();


  // --- State ---
  const isActionPending = ref(false);
  const participantsUsersVisible = ref(false);
  const eventDetails = ref<EventDetail | null>(null);


  // --- Event data ---
  const currentEvent = computed(() => eventDetails.value ?? props.event);

  async function loadEventDetails(id: string) {
    eventDetails.value = await api<EventDetail>(`/events/${id}`);
  };

  watch(
    () => props.event,
    (event) => loadEventDetails(event.id),
    { immediate: true },
  );

  watch(() => props.event.id, () => {
    participantsUsersVisible.value = false;
  });


  // --- Formatted fields ---
  const formattedStart = computed(() =>
    dayjs(currentEvent.value.starts_at).format('DD MMMM YYYY, HH:mm'),
  );

  const formattedCreatedAt = computed(() =>
    dayjs(currentEvent.value.created_at).format('DD MMMM YYYY'),
  );

  const maxParticipantsLabel = computed(() =>
    currentEvent.value.max_participants ?? '∞',
  );


  // --- User role & event status ---
  const isCreator = computed(() => eventDetails.value?.is_creator === true);
  const isParticipant = computed(() => eventDetails.value?.is_participant === true);

  const isFull = computed(() => {
    const max = currentEvent.value.max_participants;
    if (max == null) return false;
    return currentEvent.value.participants_count >= max;
  });

  const isStarted = computed(() =>
    dayjs(currentEvent.value.starts_at).isBefore(dayjs()),
  );


  // --- UI flags ---
  const showChangeEventButton = computed(() => isCreator.value && !isStarted.value);

  const isParticipationDisabled = computed(() =>
    isActionPending.value ||
    isCreator.value ||
    isStarted.value ||
    (!isParticipant.value && isFull.value),
  );

  const isEventReadOnly = computed(() => isStarted.value);

  // --- Participants panel ---
  function openParticipantsUsers() {
    participantsUsersVisible.value = true;
  };

  function closeParticipantsUsers() {
    participantsUsersVisible.value = false;
  };


  // --- Handlers ---
  async function handleToggleParticipation() {
    if (isParticipationDisabled.value) return;

    isActionPending.value = true;
    try {
      if (isParticipant.value) {
        await api(`/events/${props.event.id}/leave`, { method: 'DELETE' });
      } else {
        await api(`/events/${props.event.id}/join`, { method: 'POST' });
      }
      await loadEventDetails(props.event.id);
      if (eventDetails.value) {
        emit('updated', eventDetails.value);
      }
    } catch {
      // optional: toast / notification
    } finally {
      isActionPending.value = false;
    };
  };

  async function onParticipantRemoved() {
    await loadEventDetails(props.event.id);
    if (eventDetails.value) {
      emit('updated', eventDetails.value);
    };
  };

  function handleChangeEvent() {
    emit('edit', currentEvent.value);
  };

</script>

<template>
  <div 
    class="
      fixed top-0 right-0 z-50
      flex flex-col items-end
      w-full h-full max-w-[400px]
      
    "
  >
    <div 
      class="
        relative
        flex flex-col flex-1 gap-3
        px-5 py-5
        h-full w-full
        transition-all transition-300 ease-in-out
      bg-main border-l-2 border-solid border-third shadow-sm rounded-l-lg
      "
    >
      <button 
        type="button"
        @click="emit('close')"
        class="group ml-auto mr-2"
      >
        <Icon name="akar-icons:cross" 
          class="
            size-6 text-text-main
            transition-transform transition-300 ease-in-out
            group-hover:rotate-90
          " 
        />
      </button>
      <div
        class="flex flex-col flex-1 overflow-y-auto mb-4"
      >
        <div
          class="flex flex-col flex-1 gap-5 mb-4"
        >
          <h3
            class="text-3xl font-semibold text-text-main"
          >
            {{ currentEvent.title }}
          </h3>
          <p class="text-xl font-normal text-text-secondary min-h-[200px]">
            {{ currentEvent.description }}
          </p>
        </div>
        <div 
          class="
            flex flex-col gap-2 text-body-xl font-normal text-text-main
            [&_span]:pl-2
          "
        >
          <p>
            Creator: <span>{{ currentEvent.creator.username }}</span>
          </p>
          <p>
            Start: <span>{{ formattedStart }}</span>
          </p>
          <p>
            Create: <span>{{ formattedCreatedAt }}</span>
          </p>
          <p>
            Max participants: <span>{{ maxParticipantsLabel }}</span>
          </p>
          <p v-if="!isCreator">
            Already participants: <span>{{ currentEvent.participants_count }}</span>
          </p>

          <UiButton v-else class=" !justify-between" @click="openParticipantsUsers">
            <p>
              Already participants: <span>{{ currentEvent.participants_count }}</span>
            </p>
            <Icon
              name="weui:arrow-outlined"
              class="size-6 text-main"
            />
          </UiButton>

          <p v-if="isStarted" class="text-text-secondary">
            This event has already ended
          </p>
        </div>
      </div>


      <div
        class="grid grid-cols-2 gap-2"
      >
        <UiButton 
          style-type="cancel"
          @click="emit('close')">
          Cancel
        </UiButton>
        
        <UiButton
          :style-type="isParticipant ? 'delete' : 'primary'"
          :disabled="isParticipationDisabled"
          @click="handleToggleParticipation"
        >
          <template v-if="isParticipant">
            Leave
          </template>
          <template v-else>
            Sign up
          </template>
        </UiButton>

        <UiButton
          class="col-span-2"
          style-type="cancel"
          v-if="showChangeEventButton"
          @click="handleChangeEvent"
        >
          Change Event
        </UiButton>
      </div>

      <Transition name="slide">
        <div
          v-if="participantsUsersVisible"
          class="absolute top-0 right-0 w-full h-full z-2"
        >
        <ParticipantsUsers
          :event-id="currentEvent.id"
          :total-count="currentEvent.participants_count"
          :is-creator="isCreator"
          :read-only="isEventReadOnly"
          @close="closeParticipantsUsers"
          @participant-removed="onParticipantRemoved"
        />
        </div>
      </Transition>
    </div>
  </div>
</template>

<style scoped lang="scss">

  .slide-enter-active,
  .slide-leave-active {
    transition: opacity 0.3s ease-in-out, transform 0.3s ease-in-out;
  }
  .slide-enter-from,
  .slide-leave-to {
    opacity: 1;
    transform: translateX(100%);
  }

</style>