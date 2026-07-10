"""建立資料庫結構(只在全新環境執行,如 Docker build)"""

import sqlite3
from pathlib import Path

root = Path(__file__).resolve().parent
db = sqlite3.connect(root / "orders.db")
db.executescript((root / "schema.sql").read_text(encoding="utf-8"))
db.close()
print("DB created")
