import type { User } from '~/types/domain/user';
import type { mapEditProfiler } from '~/mappers/components/editProfiler';
import { applyEditProfilerApiErrors } from '~/mappers/components/editProfilerErrors';
import {
  createEmptyEditProfilerErrors,
  hasEditProfilerFieldErrors,
  validateEditProfilerForm,
  type EditProfilerFieldErrors,
} from '~/validators/editProfiler';

export function useEditProfilerForm(
  content: Ref<ReturnType<typeof mapEditProfiler>>,
  onClose: () => void,
) {
  const auth = useAuthStore();
  const notifications = useNotificationsStore();
  const {
    updateUsername,
    updateTimezone,
    changePassword,
    requestEmailChange,
    confirmEmailChange,
  } = useUserApi();

  const isPanelActive = ref(false);
  const verifyVisible = ref(false);
  const isSubmitting = ref(false);

  const username = ref('');
  const email = ref('');
  const timezone = ref('UTC');
  const currentPassword = ref('');
  const newPassword = ref('');
  const verificationCode = ref('');

  const originalEmail = ref('');
  const originalTimezone = ref('UTC');
  const pendingNewEmail = ref('');

  const fieldErrors = ref<EditProfilerFieldErrors>(createEmptyEditProfilerErrors());
  const formError = ref('');

  const isEmailChanged = computed(() =>
    email.value.trim().toLowerCase() !== originalEmail.value.toLowerCase(),
  );

  const isVerifyMode = computed(() => verifyVisible.value);

  const submitButtonLabel = computed(() =>
    isVerifyMode.value ? content.value.submitButton.verify : content.value.submitButton.save,
  );

  const isSubmitDisabled = computed(() => {
    if (isSubmitting.value) return true;
    if (isVerifyMode.value) return verificationCode.value.length !== 6;
    return false;
  });

  function fillFormFromUser(user: User | null) {
    if (!user) return;

    username.value = user.username;
    email.value = user.email;
    originalEmail.value = user.email;
    timezone.value = user.timezone ?? 'UTC';
    originalTimezone.value = user.timezone ?? 'UTC';
  };

  function validateForm(): boolean {
    fieldErrors.value = validateEditProfilerForm(
      {
        username: username.value,
        email: email.value,
        timezone: timezone.value,
        currentPassword: currentPassword.value,
        newPassword: newPassword.value,
      },
      {
        username: content.value.usernameInput.errors,
        email: content.value.emailInput.errors,
        timezone: content.value.timezoneInput.errors,
        currentPassword: content.value.currentPasswordInput.errors,
        newPassword: content.value.newPasswordInput.errors,
      },
    );
    formError.value = '';
    return !hasEditProfilerFieldErrors(fieldErrors.value);
  };

  async function patchUser(request: () => Promise<User>) {
    const updated = await request();
    auth.setUser(updated);
    return updated;
  };

  async function withSubmit(task: () => Promise<void>) {
    isSubmitting.value = true;
    formError.value = '';

    try {
      await task();
    } catch (e) {
      applyEditProfilerApiErrors(parseApiError(e), content.value, fieldErrors, formError);
    } finally {
      isSubmitting.value = false;
    }
  };

  function closeModal() {
    isPanelActive.value = false;
    setTimeout(onClose, 300);
  };

  async function saveProfile() {
    if (!validateForm()) return;

    await withSubmit(async () => {
      if (username.value.trim() !== auth.user?.username) {
        await patchUser(() => updateUsername(username.value.trim()));
      }

      if (timezone.value !== originalTimezone.value) {
        const updated = await patchUser(() => updateTimezone(timezone.value));
        originalTimezone.value = updated.timezone ?? timezone.value;
      }

      if (currentPassword.value && newPassword.value) {
        await changePassword(currentPassword.value, newPassword.value);
        currentPassword.value = '';
        newPassword.value = '';
      }

      if (isEmailChanged.value) {
        await requestEmailChange(email.value.trim());

        pendingNewEmail.value = email.value.trim();
        verifyVisible.value = true;
        verificationCode.value = '';
        notifications.success(
          content.value.notifications.codeSent.title,
          `${content.value.notifications.codeSent.message} ${pendingNewEmail.value}`,
        );
        return;
      }

      notifications.success(
        content.value.notifications.profileUpdated.title,
        content.value.notifications.profileUpdated.message,
      );
      closeModal();
    });
  };

  async function handleConfirmEmailChange() {
    if (verificationCode.value.length !== 6) {
      fieldErrors.value.code = content.value.verificationCodeInput.errors.valueCharacters;
      return;
    }

    fieldErrors.value.code = '';

    await withSubmit(async () => {
      const updated = await confirmEmailChange(verificationCode.value);
      auth.setUser(updated);

      originalEmail.value = updated.email;
      email.value = updated.email;
      verifyVisible.value = false;
      pendingNewEmail.value = '';
      verificationCode.value = '';

      notifications.success(
        content.value.notifications.emailUpdated.title,
        content.value.notifications.emailUpdated.message,
      );
      closeModal();
    });
  };

  async function onSubmit() {
    if (isVerifyMode.value) {
      await handleConfirmEmailChange();
      return;
    }

    await saveProfile();
  };

  async function init() {
    await nextTick();
    requestAnimationFrame(() => {
      isPanelActive.value = true;
    });

    await auth.fetchMe();
    fillFormFromUser(auth.user);
  };

  return {
    isPanelActive,
    verifyVisible,
    isVerifyMode,
    username,
    email,
    timezone,
    currentPassword,
    newPassword,
    verificationCode,
    pendingNewEmail,
    fieldErrors,
    formError,
    isSubmitDisabled,
    isSubmitting,
    submitButtonLabel,
    closeModal,
    onSubmit,
    init,
  };
};
