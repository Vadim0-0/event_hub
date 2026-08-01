export interface HeightTransitionOptions {
  duration?: number
  easing?: string
  marginTop?: number
  animateOpacity?: boolean
}

export function useHeightTransition(options: HeightTransitionOptions = {}) {
  const duration = options.duration ?? 300;
  const easing = options.easing ?? 'ease';
  const marginTop = options.marginTop ?? 0;
  const animateOpacity = options.animateOpacity ?? false;
  const marginTopPx = `${marginTop}px`;

  function transitionValue() {
    const parts = [
      `height ${duration}ms ${easing}`,
      `margin-top ${duration}ms ${easing}`,
    ];
    if (animateOpacity) {
      parts.push(`opacity ${duration}ms ${easing}`)
    };
    return parts.join(', ');
  };

  function prepareNode(node: HTMLElement) {
    node.style.boxSizing = 'border-box';
    node.style.overflow = 'hidden';
  };

  function clearInline(node: HTMLElement) {
    node.style.height = '';
    node.style.overflow = '';
    node.style.transition = '';
    node.style.opacity = '';
    node.style.marginTop = '';
    node.style.boxSizing = '';
  };

  function waitForHeightEnd(node: HTMLElement, done: () => void) {
    let settled = false;

    const finish = () => {
      if (settled) return;
      settled = true;
      node.removeEventListener('transitionend', onEnd);
      window.clearTimeout(timer);
      done();
    };

    const onEnd = (event: TransitionEvent) => {
      if (event.target !== node || event.propertyName !== 'height') return;
      finish();
    };

    node.addEventListener('transitionend', onEnd);
    const timer = window.setTimeout(finish, duration + 50);
  };

  function onBeforeEnter(el: Element) {
    const node = el as HTMLElement;
    prepareNode(node);
    node.style.height = '0px';
    node.style.marginTop = '0px';
    if (animateOpacity) node.style.opacity = '0';
  };

  function onEnter(el: Element, done: () => void) {
    const node = el as HTMLElement;
    prepareNode(node);

    // Wait a frame so nested content (icons, grids) finishes first layout
    requestAnimationFrame(() => {
      const target = node.scrollHeight;
      node.style.transition = transitionValue();
      void node.offsetHeight;
      node.style.height = `${target}px`;
      node.style.marginTop = marginTopPx;
      if (animateOpacity) node.style.opacity = '1';
      waitForHeightEnd(node, done);
    });
  };

  function onAfterEnter(el: Element) {
    clearInline(el as HTMLElement);
  };

  function onBeforeLeave(el: Element) {
    const node = el as HTMLElement;
    prepareNode(node);
    node.style.height = `${node.scrollHeight}px`;
    node.style.marginTop = marginTopPx;
    if (animateOpacity) node.style.opacity = '1';
    void node.offsetHeight;
  };

  function onLeave(el: Element, done: () => void) {
    const node = el as HTMLElement;
    prepareNode(node);
    node.style.transition = transitionValue();
    void node.offsetHeight;
    node.style.height = '0px';
    node.style.marginTop = '0px';
    if (animateOpacity) node.style.opacity = '0';
    waitForHeightEnd(node, done);
  };

  return {
    onBeforeEnter,
    onEnter,
    onAfterEnter,
    onBeforeLeave,
    onLeave,
  };
}
