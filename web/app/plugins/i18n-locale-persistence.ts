import type { Ref } from 'vue';

import { LOCALE_COOKIE_KEY, resolveI18nLocaleCode } from '~~/i18n.options';
import type { I18nLocaleCode } from '~~/i18n.options';

const LOCALE_COOKIE_MAX_AGE = 60 * 60 * 24 * 365;

export default defineNuxtPlugin((nuxtApp) => {
  if (import.meta.server) return;

  const locale = (nuxtApp.$i18n as { locale: Ref<string> }).locale;
  const localeCookie = useCookie<I18nLocaleCode | null>(LOCALE_COOKIE_KEY, {
    maxAge: LOCALE_COOKIE_MAX_AGE,
    sameSite: 'lax',
    path: '/',
  });

  watch(
    locale,
    (value) => {
      localeCookie.value = resolveI18nLocaleCode(value);
    },
    { immediate: true },
  );
});
