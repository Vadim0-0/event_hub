export const DEV_PREVIEW_NOTIFICATIONS = false;

const DEV_TITLES = ['Success', 'Error', 'Info', 'Warning', 'Update'];
const DEV_MESSAGES = [
  'Operation completed successfully',
  'Something went wrong',
  'You have a new message',
  'Profile was updated',
  'Event created',
];

function randomItem<T>(items: T[]): T {
  return items[Math.floor(Math.random() * items.length)]!;
}

function randomNotificationPayload() {
  const types = ['success', 'error', 'info'] as const;
  return {
    type: randomItem([...types]),
    title: randomItem(DEV_TITLES),
    message: randomItem(DEV_MESSAGES),
  };
}

export { randomNotificationPayload };