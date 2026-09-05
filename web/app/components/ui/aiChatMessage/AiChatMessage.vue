<script setup lang="ts">
  const props = defineProps<{
    body: string
    isMine: boolean
    time: string
  }>();

  const html = ref('');

  async function renderMarkdown(body: string) {
    if (import.meta.server) return;

    const [{ default: DOMPurify }, { marked }] = await Promise.all([
      import('isomorphic-dompurify'),
      import('marked'),
    ]);

    marked.setOptions({ breaks: true });

    const raw = marked.parse(body) as string;
    html.value = DOMPurify.sanitize(raw);
  }

  watch(
    () => props.body,
    (body) => {
      if (props.isMine) {
        html.value = '';
        return;
      }

      void renderMarkdown(body);
    },
    { immediate: true },
  );
</script>

<template>
  <div
    class="flex w-full"
    :class="isMine ? 'justify-end' : 'justify-start'"
  >
    <div
      class="flex flex-col items-end gap-1 max-w-3/5 min-w-52 p-2 rounded-sm max-sm:p-1 max-sm:px-2 max-sm:max-w-4/5"
      :class="isMine ? 'bg-primary' : 'bg-third'"
    >
      <p
        v-if="isMine"
        class="w-full text-body-sm font-medium text-main max-sm:text-sm"
      >
        {{ body }}
      </p>

      <p
        v-else-if="!html"
        class="w-full text-body-sm font-medium text-text-main whitespace-pre-wrap max-sm:text-sm"
      >
        {{ body }}
      </p>

      <div
        v-else
        class="ai-chat-message__markdown w-full text-body-sm font-medium text-text-main max-sm:text-sm"
        v-html="html"
      />

      <p
        class="text-sm whitespace-nowrap"
        :class="isMine ? 'text-secondary' : 'text-text-main'"
      >
        {{ time }}
      </p>
    </div>
  </div>
</template>

<style scoped lang="scss">
  .ai-chat-message__markdown {
    display: flex;
    flex-direction: column;
    gap: 10px;

    :deep(ul),
    :deep(ol) {
      display: flex;
      flex-direction: column;
      gap: 5px;
      padding-left: 20px;
    }

    :deep(strong) {
      font-weight: 600;
    }

    :deep(code) {
      padding: 1px 5px;
      border-radius: 1px;
      background: rgb(0 0 0 / 0.06);
    }
  }
</style>
