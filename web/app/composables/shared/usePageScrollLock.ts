import type { MaybeRefOrGetter, Ref } from 'vue';
import { onScopeDispose, ref, toValue, watch } from 'vue';

const mobileLockCount = ref(0);
const alwaysLockCount = ref(0);

let isMobileRef: Ref<boolean> | null = null;
let previousOverflow = '';
let isBodyLocked = false;

function syncBodyScrollLock() {
  if (!import.meta.client) return;

  const isMobile = isMobileRef?.value ?? false;
  const shouldLock =
    alwaysLockCount.value > 0 || (isMobile && mobileLockCount.value > 0);

  if (shouldLock && !isBodyLocked) {
    previousOverflow = document.body.style.overflow;
    document.body.style.overflow = 'hidden';
    isBodyLocked = true;
    return;
  }

  if (!shouldLock && isBodyLocked) {
    document.body.style.overflow = previousOverflow;
    isBodyLocked = false;
  }
}

export function initPageScrollLock(isMobile: Ref<boolean>) {
  isMobileRef = isMobile;

  watch([mobileLockCount, alwaysLockCount, isMobile], syncBodyScrollLock, {
    immediate: true,
  });
}

export function usePageScrollLockWhen(
  condition: MaybeRefOrGetter<boolean>,
  options: { mobileOnly?: boolean } = {},
) {
  const mobileOnly = options.mobileOnly ?? true;
  let isLocked = false;

  function setLocked(active: boolean) {
    if (active && !isLocked) {
      if (mobileOnly) {
        mobileLockCount.value++;
      } else {
        alwaysLockCount.value++;
      }
      isLocked = true;
      syncBodyScrollLock();
      return;
    }

    if (!active && isLocked) {
      if (mobileOnly) {
        mobileLockCount.value = Math.max(0, mobileLockCount.value - 1);
      } else {
        alwaysLockCount.value = Math.max(0, alwaysLockCount.value - 1);
      }
      isLocked = false;
      syncBodyScrollLock();
    }
  }

  watch(() => toValue(condition), setLocked, { immediate: true });

  onScopeDispose(() => {
    setLocked(false);
  });
}
