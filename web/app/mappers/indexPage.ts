import { pickScalar, pickArray, expandItems } from '~/composables/useLocalization';
import type { IndexPageRaw } from '~/types/indexPage';

export function mapIndexPage(data: IndexPageRaw, locale: string) {
  const { hero, howWork, forWork, advantages } = data.sections;

  return {
    hero: {
      titles: pickArray(hero.title, locale), 
      texts: pickArray(hero.text, locale),
      button: {
        to: hero.button.to,
        text: pickScalar(hero.button.text, locale),
      },
    },
    howWorksItems: howWork.items.map(({ icon, title, text }) => ({
      icon,
      title: pickArray(title, locale),
      text: pickArray(text, locale),
    })),
    forWhomItems: forWork.items.map(({ icon, title, text }) => ({
      icon,
      title: pickArray(title, locale),
      text: pickArray(text, locale),
    })),
    forWhomBards: forWork.bards,
    advantagesItems: advantages.items.map((item) => {

      if ('image' in item) {
        return { image: item.image }
      };


      const { icon, title, text } = item;
      return {
        icon,
        title: pickArray(title, locale),
        text: pickArray(text, locale),
      };
    }),
  };
};