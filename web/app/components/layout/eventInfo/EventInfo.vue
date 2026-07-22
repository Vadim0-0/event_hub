<script setup lang="ts">

  import type { Event } from '~/types/event';

  const props = defineProps<{
    event: Event
  }>();

  const emit = defineEmits<{
    close: []
  }>();

  const dayjs = useDayjs();

  const formattedStart = computed(() =>
    dayjs(props.event.starts_at).format('DD MMMM YYYY, HH:mm')
  );

  const formattedCreatedAt = computed(() =>
    dayjs(props.event.created_at).format('DD MMMM YYYY')
  );

  const maxParticipantsLabel = computed(() =>
    props.event.max_participants ?? '∞'
  );

  // Update Data
  const api = useApi();
  
  const eventDetails = ref<Event | null>(null);

  watch(
    () => props.event.id,
    async (id) => {
      eventDetails.value = await api<Event>(`/events/${id}`)
    },
    { immediate: true },
  )

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
            {{ event.title }}
          </h3>
          <p class="text-xl font-normal text-text-secondary min-h-[200px]">
            {{ event.description }}
          </p>
        </div>
        <div 
          class="
            flex flex-col gap-2 text-body-xl font-normal text-text-main
            [&_span]:pl-2
          "
        >
          <p>
            Creator: <span>{{ event.creator.username }}</span>
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
          <p>
            Already participants: <span>{{ event.participants_count }}</span>
          </p>
        </div>
      </div>
      <div
        class="grid grid-cols-2 gap-2"
      >
        <UiButton @click="emit('close')">
          Cancel
        </UiButton>
        
        <UiButton
          class="!bg-primary !text-main !border-primary hover:!bg-primary-hover"
        >
          Sign up
        </UiButton>

        <UiButton
          class="col-span-2 !bg-error/10 !border-error !text-error hover:!bg-error/30"
        >
          Покинуть событие
        </UiButton>
      </div>
    </div>
  </div>
</template>

<style scoped lang="scss">

</style>