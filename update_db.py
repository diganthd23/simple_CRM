import sqlite3

conn = sqlite3.connect("crm.db")
cur = conn.cursor()

# create new table properly
cur.execute("""
CREATE TABLE IF NOT EXISTS reminders_new (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    lead_id INTEGER,
    date TEXT,
    note TEXT
)
""")

# copy old data if any (optional)
cur.execute("""
INSERT INTO reminders_new (lead_id, date, note)
SELECT NULL, date, note FROM reminders
""")

cur.execute("DROP TABLE reminders")
cur.execute("ALTER TABLE reminders_new RENAME TO reminders")

conn.commit()
conn.close()

print("✅ Reminder table updated")
