import { ref } from 'vue';

const loaderCount = ref(0);
const registeredSources = new Map<string, Ref<boolean>>();

export function useLoader() {
  const isVisible = computed(() => {
    if (loaderCount.value > 0) return true;
    for (const source of registeredSources.values()) {
      if (source.value) return true
    };
    return false;
  });

  function registerSource(key: string, source: Ref<boolean>) {
    registeredSources.set(key, source);
    onScopeDispose(() => registeredSources.delete(key));
  };

  function show() {
    loaderCount.value++
  };

  function hide() {
    loaderCount.value = Math.max(0, loaderCount.value - 1)
  };

  async function showFor(ms: number) {
    show()
    await new Promise((resolve) => setTimeout(resolve, ms))
    hide()
  };

  async function withLoader<T>(fn: () => Promise<T>): Promise<T> {
    show()
    try {
      return await fn()
    } finally {
      hide()
    }
  };

  return { 
    isVisible, 
    registerSource,
    show, 
    hide, 
    showFor, 
    withLoader 
  };
};