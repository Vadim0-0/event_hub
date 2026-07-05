const locales = [
  { code: 'en', name: 'English', language: 'en-US' },
  { code: 'ru', name: 'Russian', language: 'ru-RU' },
] as const

export type I18nLocaleCode = (typeof locales)[number]['code']

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
  detectBrowserLanguage: false as const,
}
