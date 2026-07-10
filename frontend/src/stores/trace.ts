import { ref } from 'vue'
import { defineStore } from 'pinia'
import type { TraceStep } from '@/types/chat'

let seq = 0
const nextId = () => `trace_${++seq}`

/** 工具回傳結果 → 側欄顯示用的一句話摘要 */
function summarize(response: unknown): string {
  // ADK 會把非 dict 的回傳值包一層 { result: ... }
  const r = (response as { result?: unknown })?.result ?? response
  if (Array.isArray(r)) return `取得 ${r.length} 筆結果`
  if (r && typeof r === 'object') {
    const json = JSON.stringify(r)
    return json.length > 90 ? `${json.slice(0, 90)}…` : json
  }
  return String(r ?? '')
}

export const useTraceStore = defineStore('trace', () => {
  const steps = ref<TraceStep[]>([])

  /** 每輪提問開始:清空上一輪,放入「思考中」 */
  function begin() {
    steps.value = [
      { id: nextId(), type: 'thinking', detail: '分析問題,規劃要使用的工具', status: 'running' },
    ]
  }

  function finishRunning() {
    for (const s of steps.value) {
      if (s.status === 'running') s.status = 'done'
    }
  }

  function toolCall(tool: string, args: unknown) {
    finishRunning()
    steps.value.push({
      id: nextId(),
      type: 'tool_call',
      tool,
      detail: JSON.stringify(args),
      status: 'running',
    })
  }

  function toolResult(tool: string, response: unknown) {
    finishRunning()
    steps.value.push({
      id: nextId(),
      type: 'tool_result',
      tool,
      detail: summarize(response),
      status: 'done',
    })
  }

  /** 文字開始流出 = 生成回答階段(同輪可能再呼叫工具,只在上一步不是 answering 時新增) */
  function answering() {
    const last = steps.value[steps.value.length - 1]
    if (last?.type !== 'answering') {
      finishRunning()
      steps.value.push({
        id: nextId(),
        type: 'answering',
        detail: '整理資料,生成回答中…',
        status: 'running',
      })
    }
  }

  /** 這輪結束(成功或失敗都要收尾) */
  function end() {
    finishRunning()
  }

  return { steps, begin, toolCall, toolResult, answering, end }
})
