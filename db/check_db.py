import sqlite3

db = sqlite3.connect("db/orders.db")
tables = [r[0] for r in db.execute("SELECT name FROM sqlite_master WHERE type='table'")]
print("Tables:", tables)
for row in db.execute("SELECT id, status, amount, due_date FROM orders WHERE status='delayed' LIMIT 5"):
    print(row)
db.close()