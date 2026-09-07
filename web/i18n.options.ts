export const locales = [
  { code: 'en', name: 'English', shortName: 'En', language: 'en-US' },
  { code: 'ru', name: 'Russian', shortName: 'Ru', language: 'ru-RU' },
] as const

export type I18nLocaleCode = (typeof locales)[number]['code']

export const LOCALE_COOKIE_KEY = 'event_hub_locale'

const defaultLocale: I18nLocaleCode = 'en'

export function resolveI18nLocaleCode(i18nLocale: string): I18nLocaleCode {
  const code = String(i18nLocale ?? '').split('-')[0]?.toLowerCase() ?? ''
  const found = locales.find((l) => l.code === code)
  if (found) return found.code
  return defaultLocale
}

export default {
  defaultLocale,
  locales: [...locales],
  strategy: 'prefix_except_default' as const,
  detectBrowserLanguage: {
    useCookie: true,
    cookieKey: LOCALE_COOKIE_KEY,
    redirectOn: 'root',
    alwaysRedirect: false,
    fallbackLocale: 'en',
  },
}
