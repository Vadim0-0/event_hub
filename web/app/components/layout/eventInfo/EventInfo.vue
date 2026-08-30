<script setup lang="ts">

  import type { Event, EventDetail } from '~/types/domain/event';
  import { ParticipantsUsers } from './components';
  import eventInfoRaw from '~~/data/components/eventInfo.json';
  import { mapEventInfo } from '~/mappers/components/eventInfo';
  import type { EventInfoRaw } from '~/types/i18n/components/eventInfo';


  // --- Props & Emits ---
  const props = defineProps<{
    event: Event
  }>();

  const emit = defineEmits<{
    close: []
    updated: [event: EventDetail]
    edit: [event: Event]
  }>();

  const { locale } = useI18n();
  const content = computed(() =>
    mapEventInfo((eventInfoRaw as EventInfoRaw[])[0]!, locale.value),
  );

  const notifications = useNotificationsStore();


  // --- Composables ---
  const dayjs = useDayjs();
  const { getEventById, joinEvent, leaveEvent } = useEventsApi();


  // --- State ---
  const isActionPending = ref(false);
  const participantsUsersVisible = ref(false);
  const eventDetails = ref<EventDetail | null>(null);


  // --- Event data ---
  const currentEvent = computed(() => eventDetails.value ?? props.event);

  async function loadEventDetails(id: string) {
    eventDetails.value = await getEventById(id);
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

  const hasLocation = computed(() =>
    Boolean(currentEvent.value.location?.trim()),
  );

  const locationLabel = computed(() =>
    currentEvent.value.location?.trim() || '—',
  );

  const latitudeLabel = computed(() =>
    currentEvent.value.latitude != null
      ? currentEvent.value.latitude.toFixed(6)
      : '—',
  );

  const longitudeLabel = computed(() =>
    currentEvent.value.longitude != null
      ? currentEvent.value.longitude.toFixed(6)
      : '—',
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

  const mapsUrl = computed(() => {
    const { latitude, longitude } = currentEvent.value;
    if (latitude == null || longitude == null) return null;
    return `https://www.openstreetmap.org/?mlat=${latitude}&mlon=${longitude}#map=17/${latitude}/${longitude}`;
  });

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

    const wasParticipant = isParticipant.value;
    const eventTitle = currentEvent.value.title;

    isActionPending.value = true;

    try {
      if (isParticipant.value) {
        await leaveEvent(props.event.id);

        notifications.success(
          content.value.notifications.leaveSuccess.title,
          content.value.notifications.leaveSuccess.message.replace(
            '{title}',
            eventTitle,
          ),
        );
      } else {
        await joinEvent(props.event.id);

        notifications.success(
          content.value.notifications.joinSuccess.title,
          content.value.notifications.joinSuccess.message.replace(
            '{title}',
            eventTitle,
          ),
        );
      }

      await loadEventDetails(props.event.id);

      if (eventDetails.value) {
        emit('updated', eventDetails.value);
      }
    } catch {
      if (wasParticipant) {
        notifications.error(
          content.value.notifications.leaveError.title,
          content.value.notifications.leaveError.message.replace(
            '{title}',
            eventTitle,
          ),
        );
      } else {
        notifications.error(
          content.value.notifications.joinError.title,
          content.value.notifications.joinError.message.replace(
            '{title}',
            eventTitle,
          ),
        );
      }
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
      w-full h-full max-w-100
      
      max-sm:max-w-full
    "
  >
    <div 
      class="
        relative
        flex flex-col flex-1
        h-full w-full
        transition-all transition-300 ease-in-out
      bg-main border-l-2 border-solid border-third shadow-sm rounded-l-lg

        max-sm:border-none max-sm:rounded-none
      "
    >
      <button 
        type="button"
        @click="emit('close')"
        class="group ml-auto mt-5 mr-7 max-sm:hidden"
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
        class="flex flex-col flex-1 gap-5 min-h-0 overflow-y-auto p-5 max-sm:gap-3 max-sm:p-3"
      >
        <div
          class="flex flex-col flex-1 gap-5 mb-4 max-sm:gap-2"
        >
          <h3
            class="text-3xl font-semibold text-text-main max-sm:text-2xl"
          >
            {{ currentEvent.title }}
          </h3>
          <p class="text-xl font-normal text-text-secondary min-h-50 max-sm:text-body-xl">
            {{ currentEvent.description }}
          </p>
        </div>
        <div 
          class="
            flex flex-col gap-2 text-body-xl font-normal text-text-main
            [&_span]:pl-2
            max-sm:text-body-sm
          "
        >
          <p>
            {{ content.creator }} <span>{{ currentEvent.creator.username }}</span>
          </p>
          <p>
            {{ content.start }} <span>{{ formattedStart }}</span>
          </p>
          <p>
            {{ content.location }}
            <a
              v-if="mapsUrl"
              :href="mapsUrl"
              target="_blank"
              rel="noopener noreferrer"
              class="pl-2 text-primary hover:text-primary-hover underline"
            >
              {{ locationLabel }}
            </a>
            <span v-else class="pl-2">{{ locationLabel }}</span>
          </p>
          <p>
            {{ content.latitude }} <span>{{ latitudeLabel }}</span>
          </p>
          <p>
            {{ content.longitude }} <span>{{ longitudeLabel }}</span>
          </p>
          <p>
            {{ content.create}} <span>{{ formattedCreatedAt }}</span>
          </p>
          <p>
            {{ content.maxParticipants }} <span>{{ maxParticipantsLabel }}</span>
          </p>
          <p v-if="!isCreator">
            {{ content.alreadyParticipants }} <span>{{ currentEvent.participants_count }}</span>
          </p>

          <UiButton v-else class=" !justify-between" @click="openParticipantsUsers">
            <p>
              {{ content.alreadyParticipants }} <span>{{ currentEvent.participants_count }}</span>
            </p>
            <Icon
              name="weui:arrow-outlined"
              class="size-6 text-main"
            />
          </UiButton>

          <p v-if="isStarted" class="text-text-secondary">
            {{ content.alreadyEnded }}
          </p>
        </div>
      </div>


      <div
        class="
          relative z-2
          grid grid-cols-2 gap-2.5 px-5 py-3
          shadow-[0_-2px_4px_0_rgb(0_0_0/0.2)]
          max-sm:p-3 max-sm:bg-third rounded-t-lg
        "
      >
        <UiButton
          class="col-span-2"
          style-type="cancel"
          v-if="showChangeEventButton"
          @click="handleChangeEvent"
        >
          {{ content.changeButton }}
        </UiButton>

        <UiButton 
          style-type="cancel"
          @click="emit('close')">
          {{ content.cancelButton }}
        </UiButton>
        
        <UiButton
          :style-type="isParticipant ? 'delete' : 'primary'"
          :disabled="isParticipationDisabled"
          @click="handleToggleParticipation"
        >
          <template v-if="isParticipant">
            {{ content.submitButton.leave }}
          </template>
          <template v-else>
            {{ content.submitButton.signUp }}
          </template>
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
          :content="content.participants"
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