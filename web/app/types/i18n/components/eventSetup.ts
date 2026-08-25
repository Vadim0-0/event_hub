import type { LocalizedScalar } from '~/types/i18n/localizedPage';

type LocalizedNotification = {
  title: LocalizedScalar;
  message: LocalizedScalar;
};

type LocalizedFieldErrors = {
  empty: LocalizedScalar;
  minimumValue: LocalizedFieldErrors;
  resendTooSoon: LocalizedScalar;
};

type LocalizedInputWithPlaceholder = {
  label: LocalizedScalar;
  placeholder: LocalizedScalar;
  errors: LocalizedFieldErrors;
};


export type EventSetupRaw = {
  title: {
    addEvent: LocalizedScalar;
    changeEvent: LocalizedScalar;
  };

  nameInput: {
    label: LocalizedScalar;
    placeholder: LocalizedScalar;
    errors: {
      empty: LocalizedScalar;
    };
  }
  descriptionInput: {
    label: LocalizedScalar;
    placeholder: LocalizedScalar;
    errors: {
      empty: LocalizedScalar;
    };
  };
  maxParticipantsInput: {
    label: LocalizedScalar;
    placeholder: LocalizedScalar;
    errors: {
      empty: LocalizedScalar;
      minimumValue: LocalizedScalar;
    };
  };  
  locationInput: {
    label: LocalizedScalar;
    placeholder: LocalizedScalar;
    errors: {
      empty: LocalizedScalar;
    };
  };
  latitudeInput: {
    label: LocalizedScalar;
  }
  longitudeInput: {
    label: LocalizedScalar;
  };
  startDateInput: LocalizedInputWithPlaceholder & {
    label: LocalizedScalar;
    placeholder: LocalizedScalar;
    errors: {
      empty: LocalizedScalar;
      onlyFuture: LocalizedScalar;
    };
  };
  startTimeInput: LocalizedInputWithPlaceholder & {
    label: LocalizedScalar;
    placeholder: LocalizedScalar;
    errors: {
      empty: LocalizedScalar;
      onlyFuture: LocalizedScalar;
    };
  };

  cancelButton: LocalizedScalar;
  submitButton: {
    saving: LocalizedScalar;
    save: LocalizedScalar;
    update: LocalizedScalar;
  };
  deleteButton: LocalizedScalar;
  confirmButton: {
    deleting: LocalizedScalar;
    delete: LocalizedScalar;
  };

  formErrors: {
    saveError: LocalizedScalar;
    deleteError: LocalizedScalar;
  };

  notifications: {
    eventCreatedSuccess: LocalizedNotification;
    eventUpdatedSuccess: LocalizedNotification;
    eventCreatedError: LocalizedNotification;
    eventUpdatedError: LocalizedNotification;
    eventDeletedSuccess: LocalizedNotification;
    eventDeletedError: LocalizedNotification;
  };
};
