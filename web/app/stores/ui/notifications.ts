import { defineStore } from 'pinia';
import { DEV_PREVIEW_NOTIFICATIONS } from '~/constants/devPreview';

export type NotificationType = 'success' | 'error' | 'info';

export interface AppNotification {
  id: number
  type: NotificationType
  title: string
  message: string
};

export const useNotificationsStore = defineStore('notifications', () => {
  const items = ref<AppNotification[]>([]);
  let nextId = 1;

  function push(payload: Omit<AppNotification, 'id'>) {
    const notification: AppNotification = { id: nextId++, ...payload }
    items.value.push(notification)

    if (items.value.length > 5) {
      items.value.shift()
    }

    const keepForPreview = import.meta.dev && DEV_PREVIEW_NOTIFICATIONS;
    if (!keepForPreview) {
      setTimeout(() => remove(notification.id), 5000);
    }

    return notification.id
  };

  function success(title: string, message: string) {
    return push({ type: 'success', title, message })
  };

  function error(title: string, message: string) {
    return push({ type: 'error', title, message })
  };

  function remove(id: number) {
    items.value = items.value.filter((item) => item.id !== id)
  };

  function info(title: string, message: string) {
    return push({ type: 'info', title, message })
  };

  return { 
    items, 
    push, 
    success, 
    error, 
    remove, 
    info 
  };
});