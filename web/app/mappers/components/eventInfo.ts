import { pickScalar } from '~/composables/i18n/useLocalization';
import type { LocalizedScalar } from '~/types/i18n/localizedPage';
import type { EventInfoRaw } from '~/types/i18n/components/eventInfo';

function mapNotification(
  notification: { 
    title: LocalizedScalar; 
    message: LocalizedScalar ;
  },
  locale: string,
) {
  return {
    title: pickScalar(notification.title, locale),
    message: pickScalar(notification.message, locale),
  }
};


export function mapEventInfo(data: EventInfoRaw, locale: string) {
  return {
    title: pickScalar(data.title, locale),

    creator: pickScalar(data.creator, locale),
    start: pickScalar(data.start, locale),
    location: pickScalar(data.location, locale),
    latitude: pickScalar(data.latitude, locale),
    longitude: pickScalar(data.longitude, locale),
    create: pickScalar(data.create, locale),
    maxParticipants: pickScalar(data.maxParticipants, locale),
    alreadyParticipants: pickScalar(data.alreadyParticipants, locale),

    alreadyEnded: pickScalar(data.alreadyEnded, locale),

    cancelButton: pickScalar(data.cancelButton, locale),
    submitButton: {
      leave: pickScalar(data.submitButton.leave, locale),
      signUp: pickScalar(data.submitButton.signUp, locale),
    },
    changeButton: pickScalar(data.changeButton, locale),

    participants: {
      title: pickScalar(data.participants.title, locale),

      loading: pickScalar(data.participants.loading, locale),
      error: pickScalar(data.participants.error, locale),
      empty: pickScalar(data.participants.empty, locale),

      copyButton: {
        coping: pickScalar(data.participants.copyButton.coping, locale),
        copy: pickScalar(data.participants.copyButton.copy, locale),
      },
      deleteButton: {
        delete: pickScalar(data.participants.deleteButton.delete, locale),
        removing: pickScalar(data.participants.deleteButton.removing, locale),
      },
      loadButton: {
        loading: pickScalar(data.participants.loadButton.loading, locale),
        loadMore: pickScalar(data.participants.loadButton.loadMore, locale),
      },

      notifications: {
        removeSuccess: mapNotification(data.participants.notifications.removeSuccess, locale),
        removeError: mapNotification(data.participants.notifications.removeError, locale),
      },
    }
  }
};