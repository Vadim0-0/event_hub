import type { LocalizedScalar } from '~/types/i18n/localizedPage';

type LocalizedNotification = {
  title: LocalizedScalar;
  message: LocalizedScalar;
};

export type EventInfoRaw = {
  title: LocalizedScalar;

  creator: LocalizedScalar;
  start: LocalizedScalar;
  location: LocalizedScalar;
  latitude: LocalizedScalar;
  longitude: LocalizedScalar;
  create: LocalizedScalar;
  maxParticipants: LocalizedScalar;
  alreadyParticipants: LocalizedScalar;

  alreadyEnded: LocalizedScalar;

  cancelButton: LocalizedScalar;
  submitButton: {
    leave: LocalizedScalar;
    signUp: LocalizedScalar;
  };
  changeButton: LocalizedScalar;

  notifications: {
    joinSuccess: LocalizedNotification;
    leaveSuccess: LocalizedNotification;
    joinError: LocalizedNotification;
    leaveError: LocalizedNotification;
  };

  participants: {
    title: LocalizedScalar;

    loading: LocalizedScalar;
    error: LocalizedScalar;
    empty: LocalizedScalar;

    copyButton: {
      coping: LocalizedScalar;
      copy: LocalizedScalar;
    };
    deleteButton: {
      delete: LocalizedScalar;
      removing: LocalizedScalar;
    };
    loadButton: {
      loading: LocalizedScalar;
      loadMore: LocalizedScalar;
    };

    notifications: {
      removeSuccess: LocalizedNotification;
      removeError: LocalizedNotification;
    }
  };
};