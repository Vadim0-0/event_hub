import { pickScalar, pickArray, expandItems } from '~/composables/useLocalization';
import type { IndexFooterRaw } from '~/types/indexFooter';

export function mapIndexFooter(data: IndexFooterRaw, locale: string) {
  const currentYear = new Date().getFullYear()

  return {
    email: data.email,
    social: data.social,
    text: pickArray(data.text, locale).map(line => 
      line.replace('{{ currentYear }}', String(currentYear))
    ),
  };
}
