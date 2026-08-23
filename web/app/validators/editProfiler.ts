export type EditProfilerFormValues = {
  username: string;
  email: string;
  timezone: string;
  currentPassword: string;
  newPassword: string;
};

export type EditProfilerFieldErrors = {
  username: string;
  email: string;
  timezone: string;
  currentPassword: string;
  newPassword: string;
  code: string;
};

export function createEmptyEditProfilerErrors(): EditProfilerFieldErrors {
  return {
    username: '',
    email: '',
    timezone: '',
    currentPassword: '',
    newPassword: '',
    code: '',
  };
};

type EditProfilerValidationMessages = {
  username: { valueCharacters: string; allowedSymbols: string };
  email: { empty: string };
  timezone: { empty: string };
  currentPassword: { incorrect: string };
  newPassword: { valueCharacters: string };
};

export function validateEditProfilerForm(
  values: EditProfilerFormValues,
  messages: EditProfilerValidationMessages,
): EditProfilerFieldErrors {
  const errors = createEmptyEditProfilerErrors();

  if (values.username.trim().length < 3) {
    errors.username = messages.username.valueCharacters;
  }
  if (!/^[a-zA-Z0-9_ ]+$/.test(values.username.trim())) {
    errors.username = messages.username.allowedSymbols;
  }
  if (!values.email.trim()) {
    errors.email = messages.email.empty;
  }
  if (!values.timezone) {
    errors.timezone = messages.timezone.empty;
  }

  const wantsPasswordChange = values.currentPassword || values.newPassword;
  if (wantsPasswordChange) {
    if (!values.currentPassword) {
      errors.currentPassword = messages.currentPassword.incorrect;
    }
    if (values.newPassword.length < 8) {
      errors.newPassword = messages.newPassword.valueCharacters;
    }
  };

  return errors;
};

export function hasEditProfilerFieldErrors(errors: EditProfilerFieldErrors) {
  return Object.values(errors).some(Boolean);
};
