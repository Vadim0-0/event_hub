export function useResendCooldown(initialSeconds = 60) {
  const secondsLeft = ref(0);
  let timer: ReturnType<typeof setInterval> | null = null;

  const isCooldownActive = computed(() => secondsLeft.value > 0);

  function clearTimer() {
    if (timer) {
      clearInterval(timer);
      timer = null;
    }
  }

  function start(seconds = initialSeconds) {
    clearTimer();
    secondsLeft.value = seconds;

    timer = setInterval(() => {
      secondsLeft.value--;
      if (secondsLeft.value <= 0) clearTimer();
    }, 1000);
  }

  onUnmounted(clearTimer);

  return { secondsLeft, isCooldownActive, start };
};