import { resolveI18nLocaleCode } from '~~/i18n.options'
import type { LocalizedScalar, LocalizedArray } from '~/types/localizedPage'

export function pickScalar(field: LocalizedScalar, locale: string): string {
  const code = resolveI18nLocaleCode(locale)
  return field[code] ?? field.en ?? field.ru ?? ''
}

export function pickArray(field: LocalizedArray, locale: string): string[] {
  const code = resolveI18nLocaleCode(locale)
  return field[code] ?? field.en ?? field.ru ?? []
}

export function expandItems<T extends { icon: string; title: LocalizedArray; text: LocalizedArray }>(
  items: T[],
  locale: string,
) {
  return items.flatMap(({ icon, title, text }) => {
    const titles = pickArray(title, locale)
    const texts = pickArray(text, locale)
    const count = Math.max(titles.length, texts.length, 1)

    return Array.from({ length: count }, (_, i) => ({
      icon,
      title: titles[i] ?? '',
      text: texts[i] ?? '',
    }))
  })
}