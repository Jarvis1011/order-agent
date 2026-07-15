# CLAUDE.md

訂單管家 AI(Order Agent)——生產訂單管理的 AI Agent,含推理過程可視化。線上:https://order-agent-56007855094.asia-east1.run.app

## 架構速覽

- `my_agent/`:ADK Agent 定義(`agent.py` instruction + 工具掛載)與 `tools.py`(4 個工具:get_today / query_orders / get_sales_summary / flag_delayed_orders,直連 SQLite)
- `server/main.py`:FastAPI 服務層。核心是把 ADK Runner 事件流翻譯成自訂六型 SSE 協定(delta/text/tool_call/tool_result/done/error);生產環境同時 serve `frontend/dist`
- `frontend/`:Vue 3 + TS + Pinia + UnoCSS。`api/agent.ts` 解析 SSE(fetch + ReadableStream + buffer);`stores/chat.ts`(訊息生命週期 streaming/done/error)、`stores/trace.ts`(側欄步驟);RWD:md 以下側欄變抽屜
- `db/`:schema + seed(random.seed(42) 可重現);`tests/`:pytest 測性質不測魔法數字

## 關鍵約定(改動時必守)

- 認證走 **Vertex AI + ADC,全系統零 API key**。設定在 `my_agent/.env`(gitignored,新機器要手建):GOOGLE_GENAI_USE_VERTEXAI=TRUE / GOOGLE_CLOUD_PROJECT=order-agent-502014 / GOOGLE_CLOUD_LOCATION=global;本機需 `gcloud auth application-default login`
- SSE 事件:文字 partial→delta(前端追加)、非 partial→text(前端覆蓋);**function_call/response 只在非 partial 事件轉發**(去重,別改回去)
- 後端路由一律 `/api` 前綴(dev proxy 與生產同容器路徑一致);容器監聽 `${PORT:-8000}`(Cloud Run 合約,CMD 必須 shell 形式)
- **部署 = push main**:GitHub Actions 跑 pytest + type-check,全過後以 WIF(零金鑰)自動部署 Cloud Run。手動備援:`gcloud run deploy order-agent --source . --region asia-east1`

## 本機啟動

後端:venv + `pip install -r requirements.txt` + `python db/init_db.py && python db/seed.py` + `uvicorn server.main:app --port 8000`
前端:`cd frontend && npm install && npm run dev`(5173,/api 由 Vite 代理到 8000)
驗證:`pytest` 全綠、`cd frontend && npm run type-check`

## 已知取捨

- SQLite/InMemorySession 在容器內短命——demo 特性,生產應外接 Cloud SQL + DB session
- 本機 `docker compose up` 目前打不到 Vertex(容器內無 ADC 憑證),Docker 僅用於 Cloud Run 建置路徑
- 模型字串在 `my_agent/agent.py`,當設定管理,demo 前釘死版本
