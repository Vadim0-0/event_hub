import { defineStore } from 'pinia';
import type { User } from '~/types/user';

export const useAuthStore = defineStore('auth', () => {
  const token = useCookie<string | null>('auth_token', { maxAge: 60 * 60 * 24 * 7 });
  const user = ref<User | null>(null);

  const isLoading = ref(false)
  const api = useApi()

  const isAuthenticated = computed(() => !!token.value);

  async function register(payload: { username: string; email: string; password: string }) {
    isLoading.value = true
    try {
      await api('/auth/register', {
        method: 'POST',
        body: payload,
      })
    } finally {
      isLoading.value = false
    }
  };

  async function verifyEmail(payload: { email: string; code: string }) {
    isLoading.value = true;
    try {
      const data = await api<{ access_token: string; user: User }>('/auth/verify-email', {
        method: 'POST',
        body: payload,
      });
      token.value = data.access_token;
      user.value = data.user;
      await navigateTo('/events/allEventsPage');
    } finally {
      isLoading.value = false;
    }
  };

  async function resendVerificationCode(email: string) {
    await api('/auth/resend-verification-code', {
      method: 'POST',
      body: { email },
    });
  };

  async function login(payload: { email: string; password: string }) {
    isLoading.value = true
    try {
      const data = await api<{ access_token: string }>('/auth/login', {
        method: 'POST',
        body: payload,
      })
      token.value = data.access_token
      await navigateTo('/events/allEventsPage')
      await fetchMe()
    } finally {
      isLoading.value = false
    }
  }

  async function fetchMe() {
    if (!token.value) return
    try {
      user.value = await api<User>('/auth/me')
    } catch (e: any) {
      if (e?.response?.status === 401) {
        logout()
      }
    }
  };

  function setUser(nextUser: User) {
    user.value = nextUser;
  };

  function logout() {
    token.value = null
    user.value = null
    navigateTo('/auth')
  };

  return {
    token,
    user,
    isLoading,
    isAuthenticated,
    register,
    verifyEmail,
    resendVerificationCode,
    login,
    fetchMe,
    setUser,
    logout
  };
});