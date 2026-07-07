import { defineStore } from 'pinia';

export type NotificationType = 'success' | 'error';

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

    setTimeout(() => remove(notification.id), 5000)

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

  return { items, push, success, error, remove };
});