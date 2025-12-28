import sqlite3

conn = sqlite3.connect("crm.db")
cur = conn.cursor()

cur.execute("ALTER TABLE leads ADD COLUMN score INTEGER DEFAULT 5")
cur.execute("ALTER TABLE leads ADD COLUMN priority TEXT DEFAULT 'Low'")

conn.commit()
conn.close()

print("✅ Lead scoring columns added")
