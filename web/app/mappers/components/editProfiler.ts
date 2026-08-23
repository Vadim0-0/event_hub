import { pickScalar } from '~/composables/i18n/useLocalization';
import type { LocalizedScalar } from '~/types/i18n/localizedPage';
import type { EditProfilerRaw } from '~/types/i18n/components/editProfiler';

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


export function mapEditProfiler(data: EditProfilerRaw, locale: string) {
  return {
    title: pickScalar(data.title, locale),

    usernameInput: {
      label: pickScalar(data.usernameInput.label, locale),
      placeholder: pickScalar(data.usernameInput.placeholder, locale),
      errors: {
        valueCharacters: pickScalar(data.usernameInput.errors.valueCharacters, locale),
        allowedSymbols: pickScalar(data.usernameInput.errors.allowedSymbols, locale),
      }
    },
    timezoneInput: {
      label: pickScalar(data.timezoneInput.label, locale),
      placeholder: pickScalar(data.timezoneInput.placeholder, locale),
      errors: {
        empty: pickScalar(data.timezoneInput.errors.empty, locale),
      }
    },
    emailInput: {
      label: pickScalar(data.emailInput.label, locale),
      placeholder: pickScalar(data.emailInput.placeholder, locale),
      errors: {
        empty: pickScalar(data.emailInput.errors.empty, locale),
        resendTooSoon: pickScalar(data.emailInput.errors.resendTooSoon, locale),
      }
    },
    currentPasswordInput: {
      label: pickScalar(data.currentPasswordInput.label, locale),
      errors: {
        incorrect: pickScalar(data.currentPasswordInput.errors.incorrect, locale),
        wrongPassword: pickScalar(data.currentPasswordInput.errors.wrongPassword, locale),
        valueCharacters: pickScalar(data.currentPasswordInput.errors.valueCharacters, locale),
      }
    },
    newPasswordInput: {
      label: pickScalar(data.newPasswordInput.label, locale),
      errors: {
        valueCharacters: pickScalar(data.newPasswordInput.errors.valueCharacters, locale),
        sameAsCurrent: pickScalar(data.newPasswordInput.errors.sameAsCurrent, locale),
      },
    },

    preview: pickScalar(data.preview, locale),

    eventCreated: pickScalar(data.eventCreated, locale),
    joinedCreated: pickScalar(data.joinedCreated, locale),

    otpVerification: pickScalar(data.otpVerification, locale),
    enterCode: pickScalar(data.enterCode, locale),
    verificationCodeInput: {
      label: pickScalar(data.verificationCodeInput.label, locale),
      errors: {
        valueCharacters: pickScalar(data.verificationCodeInput.errors.valueCharacters, locale),
      }
    },

    cancelButton: pickScalar(data.cancelButton, locale),
    submitButton: {
      verify: pickScalar(data.submitButton.verify, locale),
      save: pickScalar(data.submitButton.save, locale),
    },

    notifications: {
      codeSent: mapNotification(data.notifications.codeSent, locale),
      profileUpdated: mapNotification(data.notifications.profileUpdated, locale),
      emailUpdated: mapNotification(data.notifications.emailUpdated, locale)
    }
  }
};