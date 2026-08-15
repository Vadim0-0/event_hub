type RealtimeHandler = (event: { type: string; payload: Record<string, unknown> }) => void;

export function useRealtime() {
  const authStore = useAuthStore();
  const config = useRuntimeConfig();
  const handlers = new Set<RealtimeHandler>();
  let socket: WebSocket | null = null;
  let reconnectTimer: ReturnType<typeof setTimeout> | null = null;

  function connect() {
    const token = useCookie<string | null>('auth_token').value;
    if (!token || socket) return;

    const base = (config.public.apiBase as string).replace(/^http/, 'ws');
    socket = new WebSocket(`${base}/realtime/ws?token=${token}`);

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
    if (reconnectTimer) return
    reconnectTimer = setTimeout(() => {
      reconnectTimer = null
      connect()
    }, 3000)
  };

  function disconnect() {
    socket?.close();
    socket = null;
  };

  function onEvent(handler: RealtimeHandler) {
    handlers.add(handler);
    return () => handlers.delete(handler);
  };

  watch(
    () => authStore.isAuthenticated,
    (isAuth) => {
      if (isAuth) connect()
      else disconnect()
    },
    { immediate: true },
  );

  return { 
    connect, 
    disconnect, 
    onEvent,
  };
};