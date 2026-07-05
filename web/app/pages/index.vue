<script setup lang="ts">
  import indexRaw from '~~/data/pages/index.json'
  import { mapIndexPage } from '~/mappers/indexPage'
  import type { IndexPageRaw } from '~/types/indexPage'

  const { content } = usePageContent(
    indexRaw as IndexPageRaw[],
    mapIndexPage,
  )

  const hero = computed(() => content.value.hero)
  const howWorksItems = computed(() => content.value.howWorksItems)
  const forWhomItems = computed(() => content.value.forWhomItems)
  const forWhomBards = computed(() => content.value.forWhomBards)
  const advantagesItems = computed(() => content.value.advantagesItems)

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

  // howWork section
  const howWork = useTemplateRef<HTMLElement>('howWork')

  useLenis(() => {
    const el = howWork.value
    if (!el) return
    const total = el.offsetHeight - window.innerHeight
    const scrolled = -el.getBoundingClientRect().top
    howWorkProgress.value = Math.min(Math.max(scrolled / total, 0), 1)
  });

  function howWorkItemStyle(index: number) {
    const n =howWorksItems.value.length
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

  const forWhom = useTemplateRef<HTMLElement>('forWhom')
  const forWhomBarsVisible = ref(false)
  
  useIntersectionObserver(
    forWhom,
    ([entry]) => {
      forWhomBarsVisible.value = !!entry?.isIntersecting
    },
    { rootMargin: '0px 0px -80% 0px' },
  )


  const advantages = useTemplateRef<HTMLElement>('advantages')
  const advantagesVisible = ref(false)
  
  useIntersectionObserver(
    advantages,
    ([entry]) => {
      advantagesVisible.value = !!entry?.isIntersecting
    },
    { rootMargin: '0px 0px -80% 0px' },
  )

</script>

<template>
  <section id="hero" class="sticky top-0 flex flex-col items-center justify-center h-dvh ">
    <div 
      class="flex flex-col mx-4"
      :style="{
        transform: `scale(${1 - heroProgress * 0.3})`,
        opacity: 1 - heroProgress,
      }"
    >
      <div class="flex flex-col gap-5 mb-10">
        <div>
          <h1 
            v-for="(title, i) in hero.titles"
            :key="`hero-title-${i}`"
            class="
              text-center m-0 text-heading-xl text-text-main 
              max-md:text-heading-lg max-sm:text-3xl
            "
          >
            {{ title }}
          </h1>
        </div>
        <div>
          <p 
            v-for="(text, i) in hero.texts"
            :key="`hero-text-${i}`"
            class="text-center text-body-xl text-text-main max-sm:text-body-sm"
          >
            {{ text }}
          </p>
        </div>
      </div>
      <div class="flex justify-center gap-2.5">
        <NuxtLink :to="hero.button.to" class="btn-global text-2xl max-sm:text-xl">
          <p>
            {{ hero.button.text }}
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

  <section 
    ref="howWork" 
    id="howWork" 
    class="
      relative z-10 bg-third min-h-[400vh]  
    "
  >
    <div 
      class="
        sticky top-0 py-10 min-h-screen overflow-hidden flex items-start
        max-md:py-10
      "
    >
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
      <div 
        class="
          container mx-auto  pt-10 
          max-lg:pt-0 
          max-sm:px-4
        "
      >
        <ul 
          class="
            flex flex-col items-start gap-10
            max-sm:gap-5
          "
        >
          <li
            v-for="(item, index) in howWorksItems"
            :key="index"
            class="
              flex items-start gap-5 w-full max-w-2/4 p-10 bg-primary-light rounded-2xl min-h-40 even:ml-auto
              max-lg:max-w-3/4 max-lg:p-8
              max-sm:min-h-auto max-sm:max-w-max max-sm:p-4
            "
            :style="howWorkItemStyle(index)"
          >
            <div>
              <Icon :name="item.icon" 
                class="
                  size-12 bg-primary-hover
                  max-sm:size-10
                " 
              />
            </div>
            <div class="flex flex-col gap-2">
              <div 
                class="
                  text-2xl text-text-main
                  max-sm:text-[20px]
                "
              >
                <h3 
                  v-for="(t, i) in item.title"
                  :key="`item-title-${i}`"
                >
                  {{ t }}
                </h3>
              </div>
              <div 
                class="
                  text-body-xl font-normal text-text-main
                  max-sm:text-body-sm
                "
              >
                <p
                  v-for="(t, i) in item.text"
                  :key="`item-text-${i}`"
                >
                  {{ t }}
                </p>
              </div>
            </div>
          </li>
        </ul>
      </div>
    </div>
  </section>

  <section ref="forWhom" id="forWhom" 
    class="
      relative flex flex-col justify-center z-10 min-h-screen py-20 bg-main
      max-lg:py-10
    "
  >
    <div class="
        relative z-1 container mx-auto
        max-sm:px-4
      "
    >
      <div>
        <ul class="
          grid grid-cols-3 gap-4
          max-lg:grid-cols-1  
        ">
          <li 
            v-for="(item, index) in forWhomItems"
            :key="index"
            class="
              flex flex-col gap-4 p-10 min-h-80  rounded-3xl bg-primary-light transition-all duration-700 ease-out
              max-lg:min-h-50
              max-sm:min-h-auto max-sm:p-4 max-sm:py-6
              "
            :style="{
              transform: forWhomBarsVisible ? 'scale(1)' : 'scale(0.4)',
              opacity: forWhomBarsVisible ? '1' : '0',
              transitionDelay: `${(forWhomBarsVisible ? index : (forWhomBards.length - 1 - index)) * 250}ms`,
            }"
          >
            <div class="">
              <Icon :name="item.icon" 
                class="
                  size-15 bg-primary-hover
                  max-sm:size-10
                " 
              />
            </div>
            <div 
              class="
                flex flex-col gap-5
                max-sm:gap-3
              "
            >
              <div 
                class="
                  text-2xl text-text-main
                  max-sm:text-xl
                "
              >
                <h3
                  v-for="(t, i) in item.title"
                  :key="`item-title-${i}`"
                > 
                  {{ t }}
                </h3>
              </div>
              <div 
                class="
                  text-body-xl font-normal text-text-main
                  max-sm:text-body-sm
                "
              >
                <p
                  v-for="(t, i) in item.text"
                  :key="`item-title-${i}`"
                > 
                  {{ t }}
                </p>
              </div>
            </div>
          </li>
        </ul>
      </div>
    </div>
    <div 
      class="
        absolute bottom-0 left-0 flex justify-between items-end gap-2.5 w-full h-full z-0 pointer-events-none
        max-sm:gap-2
      "
    >
      <div
        v-for="(h, i) in forWhomBards"
        :key="i"
        class="flex-1 rounded-t-[40px] bg-primary/60 transition-[height] duration-700 ease-out"
        :style="{
          height: forWhomBarsVisible ? `${h}%` : '0%',
          transitionDelay: `${(forWhomBarsVisible ? i : (forWhomBards.length - 1 - i)) * 100}ms`,
        }"
        :class="{
          'max-sm:hidden': i === 3,
        }"
      />
    </div>
  </section>

  <section ref="advantages" id="advantages" 
    class="
      relative flex flex-col min-h-screen overflow-hidden py-30 bg-main z-10
      max-lg:py-20
      max-sm:py-10
    "
    >
    <div class="container flex flex-col justify-center flex-1 mx-auto">
      <div 
        class="
          relative flex flex-col flex-1 bg-third rounded-4xl min-h-[840px]
          max-lg:min-h-[740px]
        "
      >
        <ul 
          class="
            absolute top-0 left-0 w-full min-h-full inline-size
            max-sm:relative max-sm:py-5 max-sm:px-4 max-sm:flex max-sm:flex-col max-sm:items-center max-sm:gap-6
          "
        >
          <li 
            v-for="(item, index) in advantagesItems"
            :key="index"
            class="
              absolute flex flex-col items-center gap-4 p-[2cqi] pt-8 w-[25cqi] min-h-80 rounded-2xl bg-primary-light shadow-[0_4px_8px_rgba(0,0,0,0.06),0_20px_40px_rgba(0,0,0,0.14)] inline-size
              after:content-[''] after:absolute after:top-[3.8cqi] after:right-[50%] after:transform after:translate-x-2/4 after:w-[13px] after:h-[13px] after:bg-primary-hover after:rounded-[50%] transition-[transform, opacity] duration-700 ease-out
              max-lg:w-[35cqi] max-lg:min-h-50 
              max-sm:relative max-sm:w-full max-sm:max-w-96  max-sm:min-h-auto max-sm:p-4 max-sm:pt-10
            "
            :class="{
              'top-[7%] left-[3%] transform -rotate-6 max-lg:top-[4%] max-sm:top-[unset] max-sm:left-[unset] max-sm:rotate-[unset]': index === 0,
              'top-[12%] right-[36%] max-lg:top-[25%] max-sm:top-[unset] max-sm:right-[unset] max-sm:trotate-[unset]': index === 1,
              'top-[52%] right-[7%] transform rotate-10 max-sm:top-[unset] max-sm:right-[unset] max-sm:rotate-[unset]': index === 2,
              'top-[55%] left-[10%] transform rotate-6 max-sm:top-[unset] max-sm:left-[unset] max-sm:rotate-[unset]': index === 3,
              'top-[5%] right-[3%] transform -rotate-10 max-sm:top-[unset] max-sm:right-[unset] max-sm:rotate-[unset]': index === 4,
            }"
            :style="{
              transform: advantagesVisible ? 'scale(1)' : 'scale(1.4)',
              opacity: advantagesVisible ? '1' : '0',
              transitionDelay: `${(forWhomBarsVisible ? index : (forWhomBards.length - 1 - index)) * 100}ms`,
            }"
          >
          <template v-if="item.image">
            <NuxtImg 
              :src="item.image"
              alt=""
              class="w-full h-full object-cover rounded-xl"
            />
          </template>
          <template v-else>
            <div class="flex items-center justify-center">
              <Icon :name="item.icon!" 
                class="
                  size-[20cqi] bg-primary-hover
                  max-sm:size-10
                "
              />
            </div>
            <div class="flex flex-col items-center gap-[5cqi]">
              <div 
                class="
                  text-[8.8cqi] leading-[100%] text-text-main text-center
                  max-sm:text-xl
                "
              >
                <h3
                  v-for="(t, i) in item.title"
                  :key="`item-title-${i}`"
                > 
                  {{ t }}
                </h3>
              </div>
              <div 
                class="
                  text-[6.3cqi] leading-[140%] font-normal text-text-main text-center
                  max-sm:text-body-sm
                "
              >
                <p
                  v-for="(t, i) in item.text"
                  :key="`item-title-${i}`"
                > 
                  {{ t }}
                </p>
              </div>
            </div>
          </template>
          </li>
        </ul>
      </div>
    </div>
  </section>
</template>

<style scoped lang="scss">

</style>