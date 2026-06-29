<script setup lang="ts">

  useHead({
    title: 'Index',
  });

  const heroProgress = ref(0)
  const howWorkProgress = ref(0)
  const pathLength = ref(0)

  const lenis = useLenis()

  // hero section
  useLenis(({ scroll }: { scroll: number }) => {
    const vh = window.innerHeight
    heroProgress.value = Math.min(scroll / vh, 1)
  });

  function scrollToHowWork() {
    lenis.value?.scrollTo('#howWork', {
      offset: 0,
      duration: 1.5,
    });
  };

  // Data for the “howWorks” section
  interface howWorksItem {
    icon: string
    title: string
    text: string
  };

  const howWorksItems: howWorksItem[] = [
    {
      icon: 'ion:create',
      title: 'Создайте событие',
      text: 'Укажите название, дату, место и описание. Назначьте максимум участников.',
    },
    {
      icon: 'material-symbols:join-left-rounded',
      title: 'Запишитесь на событие',
      text: 'Выберите понравившееся событие и присоединитесь к нему.',
    },
    {
      icon: 'boxicons:future',
      title: 'Узнавайте, какие события проходят',
      text: 'Можете смотреть, какие события будут проходить скоро.',
    },
    {
      icon: 'bitcoin-icons:share-filled',
      title: 'Поделитесь ссылкой',
      text: 'Отправьте ссылку друзьям или опубликуйте в соцсетях.',
    },
    {
      icon: 'lsicon:management-filled',
      title: 'Управляйте списком',
      text: 'Отслеживайте, кто записался, и связывайтесь с участниками.',
    },
  ];

  // howWork section
  const howWork = ref<HTMLElement | null>(null)

  useLenis(() => {
    const el = howWork.value
    if (!el) return
    const total = el.offsetHeight - window.innerHeight
    const scrolled = -el.getBoundingClientRect().top
    howWorkProgress.value = Math.min(Math.max(scrolled / total, 0), 1)
  });

  function howWorkItemStyle(index: number) {
    const n = howWorksItems.length
    const seg = 1 / n
    let p = (howWorkProgress.value - index * seg) / seg 
    p = Math.min(Math.max(p, 0), 1)
    return {
      opacity: p,
      transform: `translateY(${(1 - p) * 200}px)`,
    }
  };

  const pathRef = ref<SVGPathElement | null>(null);

  onMounted(() => {
    if (pathRef.value) pathLength.value = pathRef.value.getTotalLength()
  });

  const dashOffset = computed(() => pathLength.value * (1 - howWorkProgress.value));

  // Data for the “forWhom” section
  interface forWhomItem {
    icon: string
    title: string
    text: string
  };

  const forWhomItems: forWhomItem[] = [
    {
      icon: 'lucide:rocket',
      title: 'Для организаторов',
      text: 'Больше не нужно собирать ответы в мессенджерах. Все заявки в одном месте.',
    },
    {
      icon: 'fontisto:person',
      title: 'Для участников:',
      text: 'Легко находить интересные ивенты и записываться в один клик.',
    },
    {
      icon: 'ic:outline-task',
      title: 'Для всех:',
      text: 'Прозрачное количество мест. Вы всегда знаете, пойдет событие или нет.',
    },
  ];

  const forWhomBards = [40, 65, 30, 50, 80, 30, 55, 72, 48, 90]

  const forWhom = ref<HTMLElement | null>(null)
  const forWhomBarsVisible = ref(false)
  
  useIntersectionObserver(
    forWhom,
    ([entry]) => {
      forWhomBarsVisible.value = !!entry?.isIntersecting
    },
    { rootMargin: '0px 0px -80% 0px' },
  )

</script>

<template>
  <section class="sticky top-0 flex flex-col items-center justify-center h-screen">
    <div 
      class="flex flex-col "
      :style="{
        transform: `scale(${1 - heroProgress * 0.3})`,
        opacity: 1 - heroProgress,
      }"
    >
      <div class="flex flex-col gap-2 mb-6">
        <div>
          <h1 class="text-center m-0 text-heading-xl text-text-main">
            Организуйте. Участвуйте. Вдохновляйтесь.
          </h1>
        </div>
        <div>
          <p class="text-center text-body-xl text-text-main">
            Создавайте свои события, находите единомышленников и управляйте участниками в пару кликов.
          </p>
        </div>
      </div>
      <div class="flex justify-center gap-2.5">
        <NuxtLink to="" class="btn-global text-2xl">
          <p>
            Создать событие 
          </p>
        </NuxtLink>
      </div>
    </div>

    <button
      @click="scrollToHowWork"
      class="absolute bottom-4 left-2/4 transition-none"
      :style="{
        transform: `scale(${1 - heroProgress * 0.3}) translateX(-50%)`,
        opacity: 1 - heroProgress,
      }"
     >
      <Icon 
        name="bi:mouse"
        class="size-8 text-text-main"
      />
    </button>
  </section>

  <section ref="howWork" id="howWork" class="relative z-10 bg-third min-h-[400vh]">
    <div class="sticky top-0 py-10 min-h-screen overflow-hidden flex items-start">
      <svg
        class="absolute inset-0 w-full h-full pointer-events-none z-0"
        viewBox="0 0 400 1000"
        preserveAspectRatio="none"
        :style="{ opacity: pathLength ? 1 : 0 }"
      >
        <path
          ref="pathRef"
          d="M 200 0 C -162 84 281 203 274 290 S -102 306 184 548 C 339 348 360 704 247 725 C 94 753 102 559 240 576 C 392 608 387 893 200 800 S 40 920 200 1000"
          fill="none"
          stroke="#8677FC"
          stroke-width="8"
          stroke-linecap="round"
          :stroke-dasharray="pathLength"
          :stroke-dashoffset="dashOffset"
        />
      </svg>
      <div class="container mx-auto pt-10">
        <ul class="flex flex-col items-start gap-10">
          <li
            v-for="(item, index) in howWorksItems"
            :key="index"
            class="flex items-start gap-5 w-full max-w-2/4 p-10 bg-primary-light rounded-2xl min-h-40 even:ml-auto"
            :style="howWorkItemStyle(index)"
          >
            <div>
              <Icon :name="item.icon" class="size-12 bg-primary-hover" />
            </div>
            <div class="flex flex-col gap-2">
              <div class="text-2xl text-text-main">
                <h3>{{ item.title }}</h3>
              </div>
              <div class="text-body-xl font-normal text-text-main">
                <p>{{ item.text }}</p>
              </div>
            </div>
          </li>
        </ul>
      </div>
    </div>
  </section>

  <section ref="forWhom" id="forWhom" class="relative flex flex-col justify-center z-10 h-screen py-20 bg-main">
    <div class="relative z-1 container mx-auto">
      <div>
        <ul class="grid grid-cols-3 gap-4">
          <li 
            v-for="(item, index) in forWhomItems"
            :key="index"
            class="flex flex-col gap-4 p-10 min-h-80  rounded-3xl bg-primary-light"
          >
            <div class="">
              <Icon :name="item.icon" class="size-15 bg-primary-hover" />
            </div>
            <div class="flex flex-col gap-5">
              <div class="text-2xl text-text-main">
                <h3>{{ item.title }}</h3>
              </div>
              <div class="text-body-xl font-normal text-text-main">
                <p>{{ item.text }}</p>
              </div>
            </div>
          </li>
        </ul>
      </div>
    </div>
    <div class="absolute bottom-0 left-0 flex justify-between items-end gap-2.5 w-full h-full z-0 pointer-events-none">
      <div
        v-for="(h, i) in forWhomBards"
        :key="i"
        class="flex-1 rounded-t-[40px] bg-primary/60 transition-[height] duration-700 ease-out"
        :style="{
          height: forWhomBarsVisible ? `${h}%` : '0%',
          transitionDelay: `${(forWhomBarsVisible ? i : (forWhomBards.length - 1 - i)) * 100}ms`,
        }"
      />
    </div>
  </section>

  <section id="advantages" class="relative flex flex-col h-screen py-30 bg-main z-10">
    <div class="container flex flex-col flex-1 mx-auto">
      <div class="relative flex flex-col flex-1 bg-third rounded-4xl">
        <ul>
          <li>
            <div>
              <h3>
                Мгновенная запись:
              </h3>
            </div>
            <div>
              <p>
                Без звонков и длинных форм.
              </p>
            </div>
          </li>
        </ul>
      </div>
    </div>
  </section>
</template>

<style scoped lang="scss">

</style>