import { pickScalar } from '~/composables/i18n/useLocalization';
import type { LocalizedScalar } from '~/types/i18n/localizedPage';
import type { EventSetupRaw } from '~/types/i18n/components/eventSetup';

function mapNotification(
  notification: {
    title: LocalizedScalar;
    message: LocalizedScalar;
  },
  locale: string,
) {
  return {
    title: pickScalar(notification.title, locale),
    message: pickScalar(notification.message, locale),
  };
};

export function mapEventSetup(data: EventSetupRaw, locale: string) {
  return {
    title: {
      addEvent: pickScalar(data.title.addEvent, locale),
      changeEvent: pickScalar(data.title.changeEvent, locale),
    },

    nameInput: {
      label: pickScalar(data.nameInput.label, locale),
      placeholder: pickScalar(data.nameInput.placeholder, locale),
      errors: {
        empty: pickScalar(data.nameInput.errors.empty, locale),
      }
    },
    descriptionInput: {
      label: pickScalar(data.descriptionInput.label, locale),
      placeholder: pickScalar(data.descriptionInput.placeholder, locale),
      errors: {
        empty: pickScalar(data.descriptionInput.errors.empty, locale),
      }
    },
    maxParticipantsInput: {
      label: pickScalar(data.maxParticipantsInput.label, locale),
      placeholder: pickScalar(data.maxParticipantsInput.placeholder, locale),
      errors: {
        empty: pickScalar(data.maxParticipantsInput.errors.empty, locale),
        minimumValue: pickScalar(data.maxParticipantsInput.errors.minimumValue, locale),
      }
    },
    locationInput: {
      label: pickScalar(data.locationInput.label, locale),
      placeholder: pickScalar(data.locationInput.placeholder, locale),
      errors: {
        empty: pickScalar(data.locationInput.errors.empty, locale),
      }
    },
    latitudeInput: {
      label: pickScalar(data.latitudeInput.label, locale),
    },
    longitudeInput: {
      label: pickScalar(data.longitudeInput.label, locale),
    },
    startDateInput: {
      label: pickScalar(data.startDateInput.label, locale),
      placeholder: pickScalar(data.startDateInput.placeholder, locale),
      errors: {
        empty: pickScalar(data.startDateInput.errors.empty, locale),
        onlyFuture: pickScalar(data.startDateInput.errors.onlyFuture, locale),
      }
    },
    startTimeInput: {
      label: pickScalar(data.startTimeInput.label, locale),
      placeholder: pickScalar(data.startTimeInput.placeholder, locale),
      errors: {
        empty: pickScalar(data.startTimeInput.errors.empty, locale),
        onlyFuture: pickScalar(data.startTimeInput.errors.onlyFuture, locale),
      }
    },

    cancelButton: pickScalar(data.cancelButton, locale),
    submitButton: {
      saving: pickScalar(data.submitButton.saving, locale),
      save: pickScalar(data.submitButton.save, locale),
      update: pickScalar(data.submitButton.update, locale),
    },
    deleteButton: pickScalar(data.deleteButton, locale),
    confirmButton: {
      deleting: pickScalar(data.confirmButton.deleting, locale),
      delete: pickScalar(data.confirmButton.delete, locale),
    },

    formErrors: {
      saveError: pickScalar(data.formErrors.saveError, locale),
      deleteError: pickScalar(data.formErrors.deleteError, locale),
    },

    notifications: {
      eventCreatedSuccess: mapNotification(data.notifications.eventCreatedSuccess, locale),
      eventUpdatedSuccess: mapNotification(data.notifications.eventUpdatedSuccess, locale),
      eventCreatedError: mapNotification(data.notifications.eventCreatedError, locale),
      eventUpdatedError: mapNotification(data.notifications.eventUpdatedError, locale),
      eventDeletedSuccess: mapNotification(data.notifications.eventDeletedSuccess, locale),
      eventDeletedError: mapNotification(data.notifications.eventDeletedError, locale),
    },
  };
};
