<script setup lang="ts">
  import type { Event } from '~/types/domain/event';
  import {
    createEmptyEventSetupErrors,
    validateEventSetupForm,
    hasEventSetupErrors,
    type EventSetupFieldErrors,
  } from '~/validators/eventSetup';
  import eventSetupRaw from '~~/data/components/eventSetup.json';
  import { mapEventSetup } from '~/mappers/components/eventSetup';
  import type { EventSetupRaw } from '~/types/i18n/components/eventSetup';


  // === 1. PROPS / EMITS ===
  const props = defineProps<{
    mode: 'create' | 'edit'
    event?: Event | null
  }>();

  const emit = defineEmits<{
    close: []
    saved: []
    deleted: []
  }>();

  const { locale } = useI18n();
  const content = computed(() =>
    mapEventSetup((eventSetupRaw as EventSetupRaw[])[0]!, locale.value),
  );


  // === 2. COMPOSABLES ===
  const dayjs = useDayjs();
  const api = useApi();
  const notifications = useNotificationsStore();
  const mapStore = useMapStore();


  // === 3. FORM STATE ===
  const title = ref('');
  const description = ref('');
  const maxParticipants = ref<number | string>('');
  const startDate = ref('');
  const startTime = ref('');
  const location = ref('');
  const latitude = ref<number | null>(null);
  const longitude = ref<number | null>(null);


  // === 4. UI STATE ===
  const isSaving = ref(false);
  const saveError = ref('');
  const fieldErrors = ref<EventSetupFieldErrors>(createEmptyEventSetupErrors());
  const isDeleting = ref(false);
  const isDeleteConfirmOpen = ref(false);
  const deleteError = ref('');


  // === 5. DERIVED ===
  const isCreateMode = computed(() => props.mode === 'create');
  const startsAt = computed(() => {
    if (!startDate.value || !startTime.value) return null;
    const parsed = dayjs(`${startDate.value}T${startTime.value}`);
    return parsed.isValid() ? parsed : null;
  });

  const isStartInPast = computed(() => {
    if (!startsAt.value) return false;
    return startsAt.value.isBefore(dayjs());
  });


  // === 6. FORM HELPERS ===
  function resetForm() {
    title.value = '';
    description.value = '';
    maxParticipants.value = '';
    startDate.value = '';
    startTime.value = '';
    location.value = '';
    latitude.value = null;
    longitude.value = null;
  };

  function resetErrors() {
    fieldErrors.value = createEmptyEventSetupErrors();
    saveError.value = '';
  };

  function fillFormFromEvent(event: Event) {
    const eventStartsAt = dayjs(event.starts_at);
    title.value = event.title;
    description.value = event.description ?? '';
    maxParticipants.value = event.max_participants ?? '';
    startDate.value = eventStartsAt.format('YYYY-MM-DD');
    startTime.value = eventStartsAt.format('HH:mm');
    location.value = event.location ?? '';
    latitude.value = event.latitude ?? null;
    longitude.value = event.longitude ?? null;
  };

  function validateForm() {
    fieldErrors.value = validateEventSetupForm(
      {
        title: title.value,
        description: description.value,
        maxParticipants: maxParticipants.value,
        startDate: startDate.value,
        startTime: startTime.value,
      },
      {
        startsAt: startsAt.value,
        isStartInPast: isStartInPast.value,
        mode: props.mode,
      },
      {
        title: content.value.nameInput.errors,
        description: content.value.descriptionInput.errors,
        maxParticipants: content.value.maxParticipantsInput.errors,
        startDate: content.value.startDateInput.errors,
        startTime: content.value.startTimeInput.errors,
      },
    );

    return !hasEventSetupErrors(fieldErrors.value);
  };

  function buildPayload() {
    return {
      title: title.value.trim(),
      description: description.value.trim() || null,
      max_participants: Number(maxParticipants.value) || null,
      starts_at: startsAt.value!.toISOString(),
      location: location.value.trim() || null,
      latitude: latitude.value,
      longitude: longitude.value,
    }
  };

  function openMapPicker() {
    mapStore.open({
      location: location.value || null,
      latitude: latitude.value,
      longitude: longitude.value,
      onConfirm: (value) => {
        location.value = value.location;
        latitude.value = value.latitude;
        longitude.value = value.longitude;
      },
    });
  };


  // === 7. INIT FORM ===
  watch(
    () => [props.mode, props.event] as const,
    ([mode, event]) => {
      resetErrors();
      isDeleteConfirmOpen.value = false;
      deleteError.value = '';

      if (mode === 'edit' && event) {
        fillFormFromEvent(event)
        return
      };

      resetForm();
    },
    { immediate: true },
  );


  // === 8. CLEAR FIELD ERRORS ON INPUT ===
  watch(title, () => { fieldErrors.value.title = '' });
  watch(description, () => { fieldErrors.value.description = '' });
  watch(maxParticipants, () => { fieldErrors.value.maxParticipants = '' });
  watch(startDate, () => { fieldErrors.value.startDate = '' });
  watch(startTime, () => { fieldErrors.value.startTime = '' });


  // === 9. SUBMIT ===
  async function handleSave() {
    if (isSaving.value) return;

    resetErrors();
    if (!validateForm()) return;

    isSaving.value = true;

    try {
      const payload = buildPayload();

      if (isCreateMode.value) {
        await api('/events', { method: 'POST', body: payload });

        notifications.success(
          content.value.notifications.eventCreatedSuccess.title,
          content.value.notifications.eventCreatedSuccess.message,
        );
      } else if (props.event) {
        await api(`/events/${props.event.id}`, { method: 'PATCH', body: payload });

        notifications.success(
          content.value.notifications.eventUpdatedSuccess.title,
          content.value.notifications.eventUpdatedSuccess.message,
        );
      };

      emit('saved');
    } catch (e) {
      const parsed = parseApiError(e);

      fieldErrors.value = {
        ...fieldErrors.value,
        title: parsed.fieldErrors.title ?? fieldErrors.value.title,
        description: parsed.fieldErrors.description ?? fieldErrors.value.description,
        maxParticipants: parsed.fieldErrors.max_participants ?? fieldErrors.value.maxParticipants,
        startDate: parsed.fieldErrors.starts_at ?? fieldErrors.value.startDate,
      };

      saveError.value = parsed.formError || content.value.formErrors.saveError;

      notifications.error(
        isCreateMode.value
          ? content.value.notifications.eventCreatedError.title
          : content.value.notifications.eventUpdatedError.title,
        saveError.value,
      );

    } finally {
      isSaving.value = false;
    };
  };

  // === 10. Delete ===
  function openDeleteConfirm() {
    deleteError.value = '';
    isDeleteConfirmOpen.value = true;
  };

  function cancelDeleteConfirm() {
    isDeleteConfirmOpen.value = false;
    deleteError.value = '';
  };

  async function handleDelete() {
    if (!props.event || isDeleting.value || isSaving.value) return;

    deleteError.value = '';
    isDeleting.value = true;

    try {
      await api(`/events/${props.event.id}`, { method: 'DELETE' });

      notifications.success(
        content.value.notifications.eventDeletedSuccess.title,
        content.value.notifications.eventDeletedSuccess.message,
      );

      emit('deleted');
    } catch (e) {
      const parsed = parseApiError(e);
      deleteError.value = parsed.formError || content.value.formErrors.deleteError;

      notifications.error(
        content.value.notifications.eventDeletedError.title,
        deleteError.value,
      );
    } finally {
      isDeleting.value = false;
    };
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
      py-5
      h-full w-full min-h-0 overflow-hidden
      transition-all transition-300 ease-in-out
    bg-main border-l-2 border-solid border-third shadow-sm rounded-l-lg
    "
  >
    <button 
      type="button"
      class="group ml-auto mr-7"
      @click="emit('close')"
    >
      <Icon name="akar-icons:cross" 
        class="
          size-6 text-text-main
          transition-transform transition-300 ease-in-out
          group-hover:rotate-90
        " 
      />
    </button>

    <div class="mb-4 px-5">
      <h3 class="text-3xl font-semibold text-text-main">
        {{ isCreateMode ? content.title.addEvent : content.title.changeEvent}}
      </h3>
    </div>

    <div
      class="flex flex-col flex-1 gap-5 min-h-0 overflow-y-auto px-5"
      data-lenis-prevent
    >
      <div 
        class="
          flex flex-col gap-5
        "
      >
        <UiInput
          v-model="title"
          :label=content.nameInput.label
          :placeholder=content.nameInput.placeholder
          :error-message="fieldErrors.title"
        />
        <UiTextarea
          v-model="description"
          :label=content.descriptionInput.label
          :placeholder=content.descriptionInput.placeholder
          input-class="min-h-[200px]"
          :error-message="fieldErrors.description"
        />
      </div>
      <div 
        class="
          flex flex-col gap-5
        "
      >
        <UiInput
          v-model="maxParticipants"
          type="number"
          :label=content.maxParticipantsInput.label
          :placeholder=content.maxParticipantsInput.placeholder
          :error-message="fieldErrors.maxParticipants"
        />
        <UiInput
          :model-value="location"
          readonly
          :label=content.locationInput.label
          :placeholder=content.locationInput.placeholder
          input-class="cursor-pointer"
          @click="openMapPicker"
        />
        <div class="grid grid-cols-2 gap-2">
          <UiInput
            :model-value="latitude ?? ''"
            readonly
            :label=content.latitudeInput.label
            placeholder="-90"
          />
          <UiInput
            :model-value="longitude ?? ''"
            readonly
            :label=content.longitudeInput.label
            placeholder="-180"
          />
        </div>
        <UiDate 
          v-model="startDate"
          :label=content.startDateInput.label
          :placeholder=content.startDateInput.placeholder
          :error-message="fieldErrors.startDate"
        />
        <UiTime
          v-model="startTime"
          :label=content.startTimeInput.label
          :placeholder=content.startTimeInput.placeholder
          :error-message="fieldErrors.startTime"
        />
      </div>
    </div>

    <p v-if="saveError" class="text-error text-body-sm">
      {{ saveError }}
    </p>

    <p v-if="deleteError" class="text-error text-body-sm">
      {{ deleteError }}
    </p>

    <div class="
      grid grid-cols-2 gap-2.5 px-5
    ">
      <template  v-if="!isDeleteConfirmOpen">
        <UiButton style-type="cancel" @click="emit('close')" :disabled="isSaving">
          {{ content.cancelButton }}
        </UiButton>
  
        <UiButton style-type="primary" @click="handleSave" :disabled="isSaving">
          {{ isSaving ? content.submitButton.saving : (isCreateMode ? content.submitButton.save : content.submitButton.update ) }}
        </UiButton>
  
        <UiButton
          v-if="!isCreateMode"
          style-type="delete"
          class="col-span-2"
          :disabled="isSaving || isDeleting"
          @click="openDeleteConfirm"
        >
          {{ content.deleteButton}}
        </UiButton>
      </template>

      <template v-else>
        <UiButton
          style-type="cancel"
          :disabled="isDeleting"
          @click="cancelDeleteConfirm"
        >
          {{ content.cancelButton }}
        </UiButton>
  
        <UiButton
          style-type="delete"
          :disabled="isDeleting"
          @click="handleDelete"
        >
          {{ isDeleting ? content.confirmButton.deleting : content.confirmButton.delete}}
        </UiButton>
      </template>
    </div>

  </div>

  </div>
</template>

<style scoped lang="scss">
  
</style>