import type { BasePageData } from '~/types/localizedPage'
import { pickScalar } from './useLocalization'

function resolvePageData<T>(rawData: T | T[]): T {
  if (Array.isArray(rawData)) {
    const page = rawData[0]
    if (!page) throw new Error('Page data array is empty')
    return page
  }
  return rawData
}

export function usePageContent<T extends BasePageData, R>(
  rawData: T | T[],
  mapper: (data: T, locale: string) => R,
) {
  const { locale } = useI18n()

  const pageData = computed(() => resolvePageData(rawData))

  const content = computed(() =>
    mapper(pageData.value, locale.value),
  )

  const pageTitle = computed(() =>
    pickScalar(pageData.value.title, locale.value),
  )

  useHead({ title: pageTitle })

  return { content, pageTitle }
}