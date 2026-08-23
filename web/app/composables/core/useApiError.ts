type ValidationError = { loc: (string | number)[]; msg: string };
type ApiDetailObject = {
  message?: string;
  field?: string;
  retry_after?: number;
};

export function parseApiError(error: unknown) {
  const fieldErrors: Record<string, string> = {};
  let formError = '';
  let retryAfter: number | undefined;

  const detail = (error as any)?.data?.detail as string | ValidationError[] | ApiDetailObject | undefined;

  if (detail && typeof detail === 'object' && !Array.isArray(detail)) {
    if (typeof detail.message === 'string') {
      formError = detail.message;
      if (typeof detail.field === 'string') {
        fieldErrors[detail.field] = detail.message;
      }
      if (typeof detail.retry_after === 'number') {
        retryAfter = detail.retry_after;
      }
      return { fieldErrors, formError, retryAfter };
    }
  };

  if (typeof detail === 'string') {
    formError = detail;
    return { fieldErrors, formError, retryAfter };
  };

  if (Array.isArray(detail)) {
    for (const item of detail as ValidationError[]) {
      const field = item.loc.at(-1);
      if (typeof field === 'string') {
        fieldErrors[field] = item.msg;
      }
    };
    return { fieldErrors, formError, retryAfter };
  };

  formError = 'Something went wrong';
  return { fieldErrors, formError, retryAfter };
};