export interface HeightTransitionOptions {
  duration?: number
  easing?: string
  marginTop?: number
};

export function useHeightTransition(options: HeightTransitionOptions = {}) {
  const duration = options.duration ?? 300;
  const easing = options.easing ?? 'ease';
  const marginTop = options.marginTop ?? 0;
  const marginTopPx = `${marginTop}px`;

  function transitionValue() {
    return [
      `height ${duration}ms ${easing}`,
      `margin-top ${duration}ms ${easing}`,
      `opacity ${duration}ms ${easing}`,
    ].join(', ')
  };

  function onBeforeEnter(el: Element) {
    const node = el as HTMLElement;
    node.style.overflow = 'hidden';
    node.style.height = '0px';
    node.style.marginTop = '0px';
    node.style.opacity = '0';
  };

  function onEnter(el: Element, done: () => void) {
    const node = el as HTMLElement;
    const target = node.scrollHeight;

    node.style.transition = transitionValue();
    void node.offsetHeight;
    node.style.height = `${target}px`;
    node.style.marginTop = marginTopPx;
    node.style.opacity = '1';

    const onEnd = (event: TransitionEvent) => {
      if (event.target !== node || event.propertyName !== 'height') return;
      node.removeEventListener('transitionend', onEnd);
      done();
    };
    node.addEventListener('transitionend', onEnd);
  };

  function onAfterEnter(el: Element) {
    const node = el as HTMLElement;
    node.style.height = '';
    node.style.overflow = '';
    node.style.transition = '';
    node.style.opacity = '';
    node.style.marginTop = '';
  };

  function onBeforeLeave(el: Element) {
    const node = el as HTMLElement
    node.style.overflow = 'hidden'
    node.style.height = `${node.scrollHeight}px`
    node.style.marginTop = marginTopPx
    node.style.opacity = '1'
    void node.offsetHeight
  }

  function onLeave(el: Element, done: () => void) {
    const node = el as HTMLElement;

    node.style.transition = transitionValue();
    void node.offsetHeight;
    node.style.height = '0px';
    node.style.marginTop = '0px';
    node.style.opacity = '0';

    const onEnd = (event: TransitionEvent) => {
      if (event.target !== node || event.propertyName !== 'height') return;
      node.removeEventListener('transitionend', onEnd);
      done();
    };
    node.addEventListener('transitionend', onEnd);
  };

  return {
    onBeforeEnter,
    onEnter,
    onAfterEnter,
    onBeforeLeave,
    onLeave,
  };
};
