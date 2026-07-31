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
};

export function validateEventSetupForm(
  values: EventSetupFormValues,
  options: ValidateOptions,
): EventSetupFieldErrors {
  const errors = createEmptyEventSetupErrors();

  if (!values.title.trim()) {
    errors.title = 'Enter event name';
  };

  if (!values.description.trim()) {
    errors.description = 'Enter description';
  };

  if (values.maxParticipants === '' || values.maxParticipants === null) {
    errors.maxParticipants = 'Enter max participants';
  } else if (Number(values.maxParticipants) < 1) {
    errors.maxParticipants = 'Minimum value is 1';
  };

  if (!values.startDate) {
    errors.startDate = 'Select start date';
  };

  if (!values.startTime) {
    errors.startTime = 'Select start time';
  };

  if (options.startsAt && options.isStartInPast) {
    errors.startDate = 'Date must be in the future';
    errors.startTime = 'Time must be in the future';
  };

  return errors;
};

export function hasEventSetupErrors(errors: EventSetupFieldErrors) {
  return Object.values(errors).some(Boolean);
};