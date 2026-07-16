import type { LocalizedScalar, LocalizedArray } from '~/types/localizedPage';

export type IndexPageRaw = {
  title: LocalizedScalar
  sections: {
    hero: {
      title: LocalizedArray
      text: LocalizedArray
      button: { to: string; text: LocalizedScalar }
    }
    howWork: {
      items: Array<{
        icon: string
        title: LocalizedArray
        text: LocalizedArray
      }>
    }
    forWork: {
      items: Array<{
        icon: string
        title: LocalizedArray
        text: LocalizedArray
      }>
      bards: number[]
    }
    advantages: {
      items: Array<
        | { icon: string; title: LocalizedArray; text: LocalizedArray }
        | { image: string }
      >
    }
  }
};