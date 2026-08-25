import type { Dayjs } from 'dayjs'

export type EventSetupFormValues = {
  title: string
  description: string
  maxParticipants: number | string
  startDate: string
  startTime: string
};

export type EventSetupFieldErrors = {
  title: string
  description: string
  maxParticipants: string
  startDate: string
  startTime: string
};

type EventSetupValidationMessages = {
  title: { empty: string };
  description: { empty: string };
  maxParticipants: { empty: string; minimumValue: string };
  startDate: { empty: string; onlyFuture: string };
  startTime: { empty: string; onlyFuture: string };
};

export function createEmptyEventSetupErrors(): EventSetupFieldErrors {
  return {
    title: '',
    description: '',
    maxParticipants: '',
    startDate: '',
    startTime: '',
  };
};

type ValidateOptions = {
  startsAt: Dayjs | null;
  isStartInPast: boolean;
  mode?: 'create' | 'edit';
};

export function validateEventSetupForm(
  values: EventSetupFormValues,
  options: ValidateOptions,
  messages: EventSetupValidationMessages,
): EventSetupFieldErrors {
  const errors = createEmptyEventSetupErrors();
  const isCreateMode = options.mode !== 'edit';

  if (!values.title.trim()) {
    errors.title = messages.title.empty;
  };

  if (isCreateMode && !values.description.trim()) {
    errors.description = messages.description.empty;
  };

  if (values.maxParticipants === '' || values.maxParticipants === null) {
    if (isCreateMode) {
      errors.maxParticipants = messages.maxParticipants.empty;
    }
  } else if (Number(values.maxParticipants) < 1) {
    errors.maxParticipants = messages.maxParticipants.minimumValue;
  };

  if (!values.startDate) {
    errors.startDate = messages.startDate.empty;
  };

  if (!values.startTime) {
    errors.startTime = messages.startTime.empty;
  };

  if (options.startsAt && options.isStartInPast) {
    errors.startDate = messages.startDate.onlyFuture;
    errors.startTime = messages.startTime.onlyFuture;
  };

  return errors;
};

export function hasEventSetupErrors(errors: EventSetupFieldErrors) {
  return Object.values(errors).some(Boolean);
};