import { pickScalar } from '~/composables/useLocalization';
import type { AuthPageRaw } from '~/types/i18n/pages/authPage';
import type { LocalizedScalar } from '~/types/i18n/localizedPage';

function mapNotification(
  notification: { 
    title: LocalizedScalar; 
    text?: LocalizedScalar ;
  },
  locale: string,
) {
  return {
    title: pickScalar(notification.title, locale),
    text: notification.text ? pickScalar(notification.text, locale): '',
  }
};

function mapConfirmBtn(
  confirmBtn: {
    initialState: LocalizedScalar;
    loadStatus: LocalizedScalar;
  },
  locale: string,
) {
  return {
    initialState: pickScalar(confirmBtn.initialState, locale),
    loadStatus: pickScalar(confirmBtn.loadStatus, locale),
  }
};

export function mapAuthPage(data: AuthPageRaw, locale: string) {
  const { login, registration, verify } = data.sections;

  return {
    login: {
      title: pickScalar(login.title, locale),
      emailPlaceholder: pickScalar(login.emailInput.placeholder, locale),
      passwordPlaceholder: pickScalar(login.passwordInput.placeholder, locale),
      cancelButton: pickScalar(login.cancelButton, locale),
      confirmButton: {
        initial: pickScalar(login.confirmButton.initialState, locale),
        loading: pickScalar(login.confirmButton.loadStatus, locale),
      },
      createAccount: {
        text: pickScalar(login.createAccount.text, locale),
        button: pickScalar(login.createAccount.button, locale),
      },
      errors: {
        emailEmpty: pickScalar(login.errors.emailField.emptyError, locale),
        passwordEmpty: pickScalar(login.errors.passwordField.emptyError, locale),
        general: pickScalar(login.errors.generalError, locale),
        notVerify: pickScalar(login.errors.notVerify, locale),
      },
      notifications: {
        success: mapNotification(login.notifications.success, locale),
        send: mapNotification(login.notifications.send, locale),
      },
    },
    registration: {
      title: pickScalar(registration.title, locale),
      namePlaceholder: pickScalar(registration.nameInput.placeholder, locale),
      timezonePlaceholder: pickScalar(registration.timezoneInput.placeholder, locale),
      emailPlaceholder: pickScalar(registration.emailInput.placeholder, locale),
      passwordPlaceholder: pickScalar(registration.passwordInput.placeholder, locale),
      cancelButton: pickScalar(registration.cancelButton, locale),
      confirmButton: {
        initial: pickScalar(registration.confirmButton.initialState, locale),
        loading: pickScalar(registration.confirmButton.loadStatus, locale),
      },
      errors: {
        nameValue: pickScalar(registration.errors.nameField.valueError, locale),
        timezoneEmpty: pickScalar(registration.errors.timezoneField.emptyError, locale),
        emailEmpty: pickScalar(registration.errors.emailField.emptyError, locale),
        passwordValue: pickScalar(registration.errors.passwordField.valueError, locale),
        general: pickScalar(registration.errors.generalError, locale),
      },
      notifications: {
        success: mapNotification(registration.notifications.success, locale),
        error: mapNotification(registration.notifications.error, locale),
      },
    },
    verify: {
      title: pickScalar(verify.title, locale),
      text: pickScalar(verify.title, locale),
      verifyResend: {
        firstText: {
          main: pickScalar(verify.verifyResend.firstText.main, locale),
          time: pickScalar(verify.verifyResend.firstText.time, locale)
        },
        secondText: {
          main: pickScalar(verify.verifyResend.secondText.main, locale),
        }
      },
      cancelButton: pickScalar(verify.cancelButton, locale),
      confirmButton: {
        initial: pickScalar(verify.confirmButton.initialState, locale),
        loading: pickScalar(verify.confirmButton.loadStatus, locale),
      },
      errors: {
        verifyEmpty: pickScalar(verify.errors.verifyField.emptyError, locale),
        resend: pickScalar(verify.errors.resendError, locale),
      },
      notifications: {
        success: mapNotification(verify.notifications.success, locale),
        send: mapNotification(verify.notifications.send, locale),
      },
    },
  }
}