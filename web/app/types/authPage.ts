import type { LocalizedScalar } from '~/types/localizedPage';

type LocalizedNotification = {
  title: LocalizedScalar;
  text?: LocalizedScalar;
};

type LocalizedConfirmButton = {
  initialState: LocalizedScalar;
  loadStatus: LocalizedScalar;
};

export type AuthPageRaw = {
  title: LocalizedScalar;
  sections: {
    login: {
      title: LocalizedScalar;
      emailInput: { 
        placeholder: LocalizedScalar;
      };
      passwordInput: { 
        placeholder: LocalizedScalar; 
      };
      cancelButton: LocalizedScalar;
      confirmButton: LocalizedConfirmButton;
      createAccount: {
        text: LocalizedScalar;
        button: LocalizedScalar;
      };
      errors: {
        emailField: { 
          emptyError: LocalizedScalar; 
        };
        passwordField: { 
          emptyError: LocalizedScalar; 
        };
        generalError: LocalizedScalar;
        notVerify: LocalizedScalar;
      };
      notifications: {
        success: LocalizedNotification;
        send: LocalizedNotification;
      };
    };
    registration: { 
      title: LocalizedScalar;
      nameInput: { 
        placeholder: LocalizedScalar;
      };
      emailInput: { 
        placeholder: LocalizedScalar;
      };
      passwordInput: { 
        placeholder: LocalizedScalar;
      };
      cancelButton: LocalizedScalar;
      confirmButton: LocalizedConfirmButton;
      errors: {
        nameField: { 
          valueError: LocalizedScalar; 
        };
        emailField: { 
          emptyError: LocalizedScalar; 
        };
        passwordField: { 
          valueError: LocalizedScalar; 
        };
        generalError: LocalizedScalar;
      };
      notifications: {
        success: LocalizedNotification;
        error: LocalizedNotification;
      };
    };
    verify: { 
      title: LocalizedScalar;
      text: LocalizedScalar;
      verifyResend: {
        firstText: {
          main: LocalizedScalar;
          time: LocalizedScalar;
        };
        secondText: {
          main: LocalizedScalar;
        }
      };
      cancelButton: LocalizedScalar;
      confirmButton: {
        initialState: LocalizedScalar;
        loadStatus: LocalizedScalar;
      };
      errors: {
        verifyField: { 
          emptyError: LocalizedScalar; 
        };
        resendError: LocalizedScalar;
      };
      notifications: {
        success: {
          title: LocalizedScalar;
          text: LocalizedScalar;
        };
        send: {
          title: LocalizedScalar;
          text: LocalizedScalar;
        };
      };
    };
  };
}