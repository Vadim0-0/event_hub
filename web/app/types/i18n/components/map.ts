import type { LocalizedScalar } from '~/types/i18n/localizedPage';

export type MapRaw = {
  searchInput: {
    label: LocalizedScalar;
    placeholder: LocalizedScalar;
  };
  loading: LocalizedScalar;

  cancelButton: LocalizedScalar;
  confirmButton: LocalizedScalar;

  formErrors: {
    loadError: LocalizedScalar;
  };
};
