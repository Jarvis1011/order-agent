# ---- Stage 1:打包前端 ----
FROM node:22-slim AS frontend
WORKDIR /fe
COPY frontend/package*.json ./
RUN npm ci
COPY frontend .
RUN npm run build

# ---- Stage 2:後端 + 前端成品 ----
FROM python:3.13-slim
WORKDIR /app

# 先只複製 requirements 再安裝——沒改依賴時,Docker 會直接用快取層,重建秒級完成
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY my_agent ./my_agent
COPY server ./server
COPY db ./db
RUN python db/init_db.py && python db/seed.py

COPY --from=frontend /fe/dist ./frontend/dist

EXPOSE 8000
# host 0.0.0.0:容器內的 localhost 外面看不到,必須綁所有介面
# 埠聽 $PORT(Cloud Run 的合約,它會注入 PORT=8080);本機沒設就退回 8000
# 注意這裡用 shell 形式(非 JSON 陣列),環境變數才會被展開
CMD uvicorn server.main:app --host 0.0.0.0 --port ${PORT:-8000}
