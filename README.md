# 訂單管家 AI(Order Agent)

一個生產訂單管理的 AI Agent:用自然語言查訂單、看統計、標記延誤,並**即時可視化 Agent 的推理過程與工具呼叫**。

**🔗 線上 Demo:https://order-agent-56007855094.asia-east1.run.app**
(部署於 GCP Cloud Run 台灣機房;閒置會縮到零實例,第一次開啟請等待數秒冷啟動)

![screenshot](docs/screenshot.png)

## 可以問它什麼

- 「這週哪些訂單延誤了?」→ Agent 會先查今天日期、自己推算區間、再帶參數查資料庫
- 「哪個客戶貢獻的營收最高?用表格呈現」
- 「幫我標記所有逾期的訂單」→ 涉及資料修改,Agent 會**先向你確認才執行**

右側的「Agent 過程」面板會即時顯示每一步:🧠 思考 → 🔧 呼叫工具(含參數)→ 📄 工具結果 → ✍️ 生成回答。

## 架構

```mermaid
flowchart LR
    subgraph Browser["瀏覽器"]
        UI["Vue 3 + Pinia<br/>聊天介面 + AgentTracePanel"]
    end
    subgraph CloudRun["GCP Cloud Run(容器)"]
        API["FastAPI 服務層<br/>/api/chat(自訂 SSE 協定)"]
        ADK["Google ADK Runner<br/>order_agent(Gemini)"]
        DB[("SQLite<br/>訂單資料庫")]
    end
    VERTEX["Vertex AI<br/>gemini-3.5-flash"]

    UI -- "POST /api/chat" --> API
    API -- "SSE 事件流" --> UI
    API --> ADK
    ADK -- "function calling" --> DB
    ADK -- "ADC 認證(零 API key)" --> VERTEX
```

**資料流**:使用者提問 → FastAPI 把 ADK Runner 的原始事件流「翻譯」成自訂 SSE 協定 → 前端一條連線同時餵兩個視圖(文字事件 → 聊天泡泡打字機;工具事件 → 推理過程側欄)。

### 自訂 SSE 事件協定

後端不直接暴露 ADK 的內部事件格式,而是在服務層收斂成六種語意明確的事件(防腐層):

| type | 語意 | 前端行為 |
|------|------|---------|
| `delta` | 逐字文字片段 | 追加(打字機效果) |
| `text` | 段落完整彙總 | 覆蓋(避免 partial 重複) |
| `tool_call` | Agent 呼叫工具 | 側欄新增步驟(含參數) |
| `tool_result` | 工具執行結果 | 側欄顯示摘要(如「取得 12 筆」) |
| `done` | 本輪結束 | 收尾 |
| `error` | 錯誤 | 錯誤狀態 UI(不會無聲斷線) |

## 技術選型與理由

| 決策 | 理由 |
|------|------|
| **Google ADK** | Agent 推理迴圈、function calling、Session 管理開箱即用;`adk web` 開發介面適合驗證 Agent 行為;部署路徑直通 Cloud Run / Vertex AI |
| **SSE 而非 WebSocket** | LLM 聊天是「一次 POST、單向逐字回」——單向就夠。SSE 走標準 HTTP、基建友善;WebSocket 留給真正雙向的場景(如語音) |
| **自訂 /chat 端點而非 ADK 內建 api_server** | 內建端點格式是框架內部視角,欄位龐雜且隨版本變動;服務層翻譯成自己的協定,前後端契約由自己控制 |
| **工具用 in-process function 而非 MCP** | 工具只有單一消費者(本 Agent),MCP 是多餘的一層;若未來工具需跨客戶端共用,ADK 的 `McpToolset` 可無縫接上 |
| **Vertex AI + ADC 而非 AI Studio API key** | IAM 身分認證、全系統零金鑰;計費併入 GCP 專案;本機以開發者身分、雲端以服務帳戶身分,同一份程式碼自動切換 |
| **每次增量全量重渲染 Markdown** | markdown-it 渲染幾 KB 是微秒級;半截語法會隨字元到齊漸進成形。先選最笨但正確的方案,量測到瓶頸再優化 |

## 本機開發

需求:Python 3.11+、Node.js 22+、gcloud CLI(已 `gcloud auth application-default login`)

```powershell
# 後端
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
python db/init_db.py      # 建表
python db/seed.py         # 灌 300 筆模擬訂單(random.seed 固定,可重現)
# 設定 my_agent/.env:GOOGLE_GENAI_USE_VERTEXAI=TRUE、GOOGLE_CLOUD_PROJECT、GOOGLE_CLOUD_LOCATION
uvicorn server.main:app --port 8000

# 前端(另一個終端機)
cd frontend
npm install
npm run dev               # http://localhost:5173(/api 由 Vite proxy 轉發到 8000)

# 測試
pytest                    # 工具層單元測試(測性質,不測魔法數字)
```

## Docker

```powershell
docker compose up --build   # http://localhost:8000(前端由 FastAPI 同容器供應)
```

多階段建置:node 映像只負責打包 Vue,最終 python 映像僅含 dist 成品;金鑰與本機資料庫不進映像;容器監聽 `${PORT:-8000}`(相容 Cloud Run 的 PORT 注入合約)。

## 部署(Cloud Run)

```powershell
gcloud run deploy order-agent --source . --region asia-east1
```

前置(一次性):啟用 `aiplatform.googleapis.com`、給預設服務帳戶綁 `roles/cloudbuild.builds.builder` 與 `roles/aiplatform.user`、環境變數設 Vertex 三變數。

## 專案結構

```
order-agent/
├── my_agent/          # Agent 定義(instruction、工具掛載)+ tools.py(4 個工具)
├── server/            # FastAPI 服務層:/api/chat 自訂 SSE 協定
├── db/                # schema.sql、seed、SQLite
├── tests/             # pytest(8 個測試)
├── frontend/          # Vue 3 + TS + Pinia + UnoCSS
│   └── src/
│       ├── api/agent.ts       # SSE 解析(fetch + ReadableStream + buffer)
│       ├── stores/            # chat(訊息生命週期)、trace(推理步驟)
│       └── components/        # ChatWindow / MessageBubble / MessageInput / AgentTracePanel
├── Dockerfile         # 多階段建置
└── docker-compose.yml
```

## 已知限制(demo 取捨)

- **SQLite 在容器內**:實例重啟即重置回 seed 資料——demo 永遠乾淨;生產應外接 Cloud SQL,容器保持無狀態
- **InMemory Session**:多實例間不共享對話記憶;生產應換 DB-backed session service
- **單一使用者**:`user_id` 寫死;生產由登入身分帶入
