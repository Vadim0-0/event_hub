import type { Ref } from 'vue';
import type { mapEditProfiler } from '~/mappers/components/editProfiler';
import type { EditProfilerFieldErrors } from '~/validators/editProfiler';

const API_FIELD_MAP = {
  current_password: 'currentPassword',
  new_password: 'newPassword',
  username: 'username',
  email: 'email',
  timezone: 'timezone',
  token: 'code',
} as const;

type EditProfilerContent = ReturnType<typeof mapEditProfiler>;
type ParsedApiError = ReturnType<typeof parseApiError>;

export function applyEditProfilerApiErrors(
  parsed: ParsedApiError,
  content: EditProfilerContent,
  fieldErrors: Ref<EditProfilerFieldErrors>,
  formError: Ref<string>,
) {
  for (const [apiField, message] of Object.entries(parsed.fieldErrors)) {
    if (!message) continue;

    const field = API_FIELD_MAP[apiField as keyof typeof API_FIELD_MAP];
    if (!field) continue;

    if (field === 'currentPassword') {
      fieldErrors.value.currentPassword = content.currentPasswordInput.errors.wrongPassword;
    } else if (field === 'newPassword') {
      fieldErrors.value.newPassword =
        message === 'New password must be different from the current one'
          ? content.newPasswordInput.errors.sameAsCurrent
          : content.newPasswordInput.errors.valueCharacters;
    } else {
      fieldErrors.value[field] = message;
    }
  };

  if (parsed.formError === 'Current password is incorrect') {
    fieldErrors.value.currentPassword = content.currentPasswordInput.errors.wrongPassword;
    formError.value = '';
    return;
  };

  if (parsed.formError === 'New password must be different from the current one') {
    fieldErrors.value.newPassword = content.newPasswordInput.errors.sameAsCurrent;
    formError.value = '';
    return;
  };

  if (parsed.formError === 'Invalid or expired confirmation code') {
    fieldErrors.value.code = parsed.formError;
    formError.value = '';
    return;
  };

  formError.value = parsed.formError;
};
