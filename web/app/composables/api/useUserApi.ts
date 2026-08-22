import type { User } from '~/types/domain/user';

export function useUserApi() {
  const api = useApi();

  function updateUsername(username: string) {
    return api<User>('/users/me', {
      method: 'PATCH',
      body: { username },
    });
  }

  function updateTimezone(timezone: string) {
    return api<User>('/users/me', {
      method: 'PATCH',
      body: { timezone },
    });
  }

  function changePassword(currentPassword: string, newPassword: string) {
    return api('/users/me/password', {
      method: 'PATCH',
      body: {
        current_password: currentPassword,
        new_password: newPassword,
      },
    });
  }

  function requestEmailChange(newEmail: string) {
    return api('/users/me/email-change/request', {
      method: 'POST',
      body: { new_email: newEmail },
    });
  }

  function confirmEmailChange(token: string) {
    return api<User>('/users/me/email-change/confirm', {
      method: 'POST',
      body: { token },
    });
  }

  return {
    updateUsername,
    updateTimezone,
    changePassword,
    requestEmailChange,
    confirmEmailChange,
  };
};