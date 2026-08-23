import type { LocalizedScalar } from '~/types/i18n/localizedPage';


type LocalizedNotification = {
  title: LocalizedScalar;
  message: LocalizedScalar;
};


export type EditProfilerRaw = {
  title: LocalizedScalar;

  usernameInput: {
    label: LocalizedScalar;
    placeholder: LocalizedScalar;
    errors: {
      valueCharacters: LocalizedScalar;
      allowedSymbols: LocalizedScalar;
    };
  };
  timezoneInput: {
    label: LocalizedScalar;
    placeholder: LocalizedScalar;
    errors: {
      empty: LocalizedScalar;
    };
  };
  emailInput: {
    label: LocalizedScalar;
    placeholder: LocalizedScalar;
    errors: {
      empty: LocalizedScalar;
      resendTooSoon: LocalizedScalar;
    };
  };
  currentPasswordInput: {
    label: LocalizedScalar;
    errors: {
      incorrect: LocalizedScalar;
      wrongPassword: LocalizedScalar;
      valueCharacters: LocalizedScalar;
    };
  };
  newPasswordInput: {
    label: LocalizedScalar;
    errors: {
      valueCharacters: LocalizedScalar;
      sameAsCurrent: LocalizedScalar;
    };
  };

  preview: LocalizedScalar;

  eventCreated: LocalizedScalar;
  joinedCreated: LocalizedScalar;

  otpVerification: LocalizedScalar;
  enterCode: LocalizedScalar;
  verificationCodeInput: {
    label: LocalizedScalar;
    errors: {
      valueCharacters: LocalizedScalar;
    };
  };

  cancelButton: LocalizedScalar;
  submitButton: {
    verify: LocalizedScalar;
    save: LocalizedScalar;
  };

  notifications: {
    codeSent: LocalizedNotification;
    profileUpdated: LocalizedNotification;
    emailUpdated: LocalizedNotification;
  }
};