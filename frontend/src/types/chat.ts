export interface ChatMessage {
  id: string
  role: 'user' | 'assistant'
  content: string
  status: 'streaming' | 'done' | 'error' // ★ 關鍵:訊息有生命週期
}

/** Agent 執行過程的單一步驟(Step 16 接真資料,先定型別) */
export interface TraceStep {
  id: string
  type: 'thinking' | 'tool_call' | 'tool_result' | 'answering'
  /** 工具名稱,type 為 tool_call / tool_result 時才有 */
  tool?: string
  /** 顯示用的摘要,如參數 JSON 或「取得 12 筆結果」 */
  detail?: string
  status: 'running' | 'done'
}
