<script setup lang="ts">
import { ref } from 'vue'
import { storeToRefs } from 'pinia'
import { useChatStore } from '@/stores/chat'

const store = useChatStore()
const { isStreaming } = storeToRefs(store)
const draft = ref('')

function submit() {
  if (isStreaming.value) return
  store.sendMessage(draft.value)
  draft.value = ''
}

// Enter 送出、Shift+Enter 換行(中文輸入法選字中的 Enter 不觸發)
function onKeydown(e: KeyboardEvent) {
  if (e.key === 'Enter' && !e.shiftKey && !e.isComposing) {
    e.preventDefault()
    submit()
  }
}
</script>

<template>
  <div class="border-t border-line bg-surface-panel px-3 py-3 md:px-6 md:py-4">
    <div class="mx-auto flex max-w-3xl items-end gap-3">
      <textarea
        v-model="draft"
        rows="1"
        :disabled="isStreaming"
        :placeholder="isStreaming ? 'AI 回覆中…' : '問問訂單管家,例如:這週哪些訂單延誤了?'"
        class="max-h-40 min-h-11 flex-1 resize-none rounded-xl border border-line bg-surface-raised px-4 py-2.5 text-sm text-slate-200 outline-none transition-colors placeholder:text-slate-500 focus:border-accent disabled:cursor-not-allowed disabled:opacity-50"
        @keydown="onKeydown"
      />
      <!-- 串流中變成「停止」——像 ChatGPT 一樣可以打斷 AI -->
      <button
        v-if="isStreaming"
        class="h-11 shrink-0 rounded-xl border border-red-500/50 px-5 text-sm font-medium text-red-400 transition-colors hover:bg-red-500/10"
        @click="store.stopStreaming()"
      >
        ⏹ 停止
      </button>
      <button
        v-else
        :disabled="!draft.trim()"
        class="h-11 shrink-0 rounded-xl bg-accent px-5 text-sm font-medium text-white transition-opacity hover:opacity-90 disabled:cursor-not-allowed disabled:opacity-40"
        @click="submit"
      >
        送出
      </button>
    </div>
  </div>
</template>
