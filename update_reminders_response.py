import sqlite3

conn = sqlite3.connect("crm.db")
cur = conn.cursor()

cur.execute("""
ALTER TABLE reminders 
ADD COLUMN response TEXT DEFAULT 'Pending'
""")

conn.commit()
conn.close()

print("✅ Reminder response column added")
