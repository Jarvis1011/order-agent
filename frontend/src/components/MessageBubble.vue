<script setup lang="ts">
import { computed } from 'vue'
import type { ChatMessage } from '@/types/chat'
import { renderMarkdown } from '@/utils/markdown'

const props = defineProps<{ message: ChatMessage }>()

// AI 回覆走 Markdown;使用者訊息保持純文字(不值得為它冒 v-html 的險,也保留原始換行)
const html = computed(() =>
  props.message.role === 'assistant' ? renderMarkdown(props.message.content) : '',
)
</script>

<template>
  <div class="flex gap-3" :class="message.role === 'user' ? 'flex-row-reverse' : ''">
    <!-- 頭像 -->
    <div
      class="h-8 w-8 shrink-0 rounded-full flex items-center justify-center text-sm select-none"
      :class="message.role === 'user' ? 'bg-accent/20 text-accent-soft' : 'bg-emerald-500/15 text-emerald-400'"
    >
      {{ message.role === 'user' ? '你' : 'AI' }}
    </div>

    <!-- 泡泡 -->
    <div
      class="max-w-[88%] rounded-2xl px-4 py-2.5 text-sm leading-relaxed break-words md:max-w-[72%]"
      :class="[
        message.role === 'user'
          ? 'bg-accent text-white rounded-tr-sm whitespace-pre-wrap'
          : 'bg-surface-raised text-slate-200 rounded-tl-sm',
        message.status === 'error' ? 'border border-red-500/60' : '',
      ]"
    >
      <template v-if="message.role === 'assistant'">
        <!-- eslint-disable-next-line vue/no-v-html — 來源經 markdown-it(html:false)轉義,安全 -->
        <div class="md-body" v-html="html" />
        <span v-if="message.status === 'streaming'" class="streaming-cursor" />
      </template>
      <span v-else>{{ message.content }}</span>

      <div v-if="message.status === 'error'" class="mt-1 text-xs text-red-400">
        ⚠ 回應中斷,請重試
      </div>
    </div>
  </div>
</template>
