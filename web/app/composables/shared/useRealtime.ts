type RealtimeHandler = (event: { type: string; payload: Record<string, unknown> }) => void;

export function useRealtime() {
  const authStore = useAuthStore();
  const config = useRuntimeConfig();
  const token = useCookie<string | null>('auth_token');
  const handlers = new Set<RealtimeHandler>();
  let socket: WebSocket | null = null;
  let reconnectTimer: ReturnType<typeof setTimeout> | null = null;

  function connect() {
    if (!import.meta.client) return;
    if (!token.value || socket) return;

    const base = (config.public.apiBase as string).replace(/^http/, 'ws');
    socket = new WebSocket(`${base}/realtime/ws?token=${token.value}`);

    socket.onmessage = (event) => {
      const data = JSON.parse(event.data);
      handlers.forEach((handler) => handler(data));
    };

    socket.onclose = () => {
      socket = null;
      scheduleReconnect();
    };
  }

  function scheduleReconnect() {
    if (!import.meta.client) return;
    if (reconnectTimer) return;

    reconnectTimer = setTimeout(() => {
      reconnectTimer = null;
      connect();
    }, 3000);
  }

  function disconnect() {
    if (reconnectTimer) {
      clearTimeout(reconnectTimer);
      reconnectTimer = null;
    }

    socket?.close();
    socket = null;
  }

  function onEvent(handler: RealtimeHandler) {
    handlers.add(handler);
    return () => handlers.delete(handler);
  }

  if (import.meta.client) {
    watch(
      () => authStore.isAuthenticated,
      (isAuth) => {
        if (isAuth) connect();
        else disconnect();
      },
      { immediate: true },
    );

    onScopeDispose(disconnect);
  }

  return {
    connect,
    disconnect,
    onEvent,
  };
}
