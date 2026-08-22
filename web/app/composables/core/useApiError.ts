type ApiFieldError = { message: string; field: string };
type ValidationError = { loc: (string | number)[]; msg: string };

export function parseApiError(error: unknown) {
  const fieldErrors: Record<string, string> = {};
  let formError = '';

  const detail = (error as any)?.data?.detail;

  if (detail?.field && detail?.message) {
    fieldErrors[detail.field] = detail.message
    return { fieldErrors, formError }
  };

  if (typeof detail === 'string') {
    formError = detail
    return { fieldErrors, formError }
  };

  if (Array.isArray(detail)) {
    for (const item of detail as ValidationError[]) {
      const field = item.loc.at(-1)
      if (typeof field === 'string') {
        fieldErrors[field] = item.msg
      }
    }
    return { fieldErrors, formError }
  };

  formError = 'Something went wrong'
  return { fieldErrors, formError }
};