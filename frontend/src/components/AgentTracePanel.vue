<script setup lang="ts">
import { nextTick, ref, watch } from 'vue'
import { storeToRefs } from 'pinia'
import { useTraceStore } from '@/stores/trace'
import type { TraceStep } from '@/types/chat'

// 手機:抽屜模式,由父層控制開關;桌機(md+):固定側欄,open 無作用
defineProps<{ open: boolean }>()
defineEmits<{ close: [] }>()

const { steps } = storeToRefs(useTraceStore())
const scrollEl = ref<HTMLElement | null>(null)

// 步驟增加時跟著捲到底,跟聊天視窗同一招
watch(
  steps,
  async () => {
    await nextTick()
    scrollEl.value?.scrollTo({ top: scrollEl.value.scrollHeight })
  },
  { deep: true },
)

const stepMeta: Record<TraceStep['type'], { icon: string; label: string }> = {
  thinking: { icon: '🧠', label: '思考' },
  tool_call: { icon: '🔧', label: '呼叫工具' },
  tool_result: { icon: '📄', label: '工具結果' },
  answering: { icon: '✍️', label: '生成回答' },
}
</script>

<template>
  <!-- 手機:固定定位的右側抽屜(translate 滑入滑出);md+:回歸靜態側欄 -->
  <aside
    class="fixed inset-y-0 right-0 z-50 flex w-[85vw] max-w-90 flex-col border-l border-line bg-surface-panel transition-transform duration-200 md:static md:z-auto md:w-80 md:shrink-0 md:translate-x-0 md:transition-none"
    :class="open ? 'translate-x-0' : 'translate-x-full'"
  >
    <div class="flex items-start justify-between border-b border-line px-5 py-4">
      <div>
        <h2 class="text-sm font-semibold text-slate-200">Agent 過程</h2>
        <p class="mt-0.5 text-xs text-slate-500">即時顯示推理與工具呼叫</p>
      </div>
      <!-- 手機:關閉抽屜 -->
      <button
        class="h-8 w-8 rounded-lg text-slate-400 hover:bg-surface-raised md:hidden"
        aria-label="關閉"
        @click="$emit('close')"
      >
        ✕
      </button>
    </div>

    <div ref="scrollEl" class="chat-scroll flex-1 overflow-y-auto px-5 py-4">
      <!-- 還沒提問過的空狀態 -->
      <div v-if="steps.length === 0" class="mt-10 text-center text-xs leading-relaxed text-slate-600">
        送出問題後,這裡會即時顯示<br />Agent 的推理步驟與工具呼叫
      </div>

      <ol
        v-else
        class="relative flex flex-col gap-4 before:absolute before:left-[11px] before:top-2 before:bottom-2 before:w-px before:bg-line"
      >
        <li v-for="step in steps" :key="step.id" class="relative flex gap-3 pl-0">
          <div
            class="z-1 h-6 w-6 shrink-0 rounded-full bg-surface-raised text-xs flex items-center justify-center"
            :class="step.status === 'running' ? 'animate-pulse ring-1 ring-accent' : ''"
          >
            {{ stepMeta[step.type].icon }}
          </div>
          <div class="min-w-0">
            <div class="text-xs font-medium text-slate-300">
              {{ stepMeta[step.type].label }}
              <span
                v-if="step.tool"
                class="ml-1 rounded bg-accent/15 px-1.5 py-0.5 font-mono text-[11px] text-accent-soft"
              >
                {{ step.tool }}
              </span>
            </div>
            <div
              v-if="step.detail"
              class="mt-1 break-all text-xs leading-relaxed text-slate-500"
              :class="step.type === 'tool_call' ? 'font-mono' : ''"
            >
              {{ step.detail }}
            </div>
          </div>
        </li>
      </ol>
    </div>

    <div class="border-t border-line px-5 py-3 text-[11px] text-slate-600">
      Powered by Google ADK · Gemini
    </div>
  </aside>
</template>
