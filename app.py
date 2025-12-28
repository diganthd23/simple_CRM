from flask import Flask, render_template, request, redirect, session, url_for
import sqlite3, os

app = Flask(__name__)
app.secret_key = "crm_secret"

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB = os.path.join(BASE_DIR, "crm.db")

def get_db():
    return sqlite3.connect(DB)

def priority_from_score(score):
    if score >= 40:
        return "High"
    elif score >= 20:
        return "Medium"
    return "Low"

# ---------- LOGIN ----------
@app.route("/", methods=["GET","POST"])
def login():
    if request.method == "POST":
        if request.form["username"] == "employee" and request.form["password"] == "croma":
            session["user"] = "employee"
            return redirect("/dashboard")
    return render_template("login.html")

@app.route("/logout")
def logout():
    session.clear()
    return redirect("/")

# ---------- DASHBOARD ----------
@app.route("/dashboard")
def dashboard():
    if "user" not in session:
        return redirect("/")
    db = get_db()
    cur = db.cursor()

    total_leads = cur.execute("SELECT COUNT(*) FROM leads").fetchone()[0]
    closed_leads = cur.execute("SELECT COUNT(*) FROM leads WHERE status='Closed'").fetchone()[0]
    total_products = cur.execute("SELECT COUNT(*) FROM products").fetchone()[0]
    total_reminders = cur.execute("SELECT COUNT(*) FROM reminders").fetchone()[0]

    return render_template(
        "dashboard.html",
        total_leads=total_leads,
        closed_leads=closed_leads,
        total_products=total_products,
        total_reminders=total_reminders
    )

# ---------- PRODUCTS ----------
@app.route("/products", methods=["GET","POST"])
def products():
    if "user" not in session:
        return redirect("/")
    db = get_db()
    cur = db.cursor()

    if request.method == "POST":
        cur.execute(
            "INSERT INTO products (name,category,price) VALUES (?,?,?)",
            (request.form["name"], request.form["category"], request.form["price"])
        )
        db.commit()

    products = cur.execute("SELECT * FROM products").fetchall()
    return render_template("products.html", products=products)

# ---------- LEADS ----------
@app.route("/leads", methods=["GET", "POST"])
def leads():
    if "user" not in session:
        return redirect("/")

    db = get_db()
    cur = db.cursor()

    # ADD LEAD
    if request.method == "POST":
        cur.execute("""
            INSERT INTO leads (name, phone, email, product, budget)
            VALUES (?, ?, ?, ?, ?)
        """, (
            request.form["name"],
            request.form["phone"],
            request.form["email"],
            request.form["product"],
            request.form["budget"]
        ))
        db.commit()

    leads = cur.execute("SELECT * FROM leads").fetchall()
    products = cur.execute("SELECT name FROM products").fetchall()

    return render_template(
        "leads.html",
        leads=leads,
        products=products
    )
# ---------- CLOSE LEAD ----------
@app.route("/close_lead/<int:id>")
def close_lead(id):
    db = get_db()
    cur = db.cursor()

    lead = cur.execute(
        "SELECT name,product,budget,score FROM leads WHERE id=?",
        (id,)
    ).fetchone()

    if lead:
        new_score = lead[3] + 20
        cur.execute(
            "INSERT INTO deals (lead_name,product,amount,status) VALUES (?,?,?,?)",
            (lead[0], lead[1], lead[2], "Closed")
        )
        cur.execute(
            "UPDATE leads SET status='Closed', score=?, priority=? WHERE id=?",
            (new_score, priority_from_score(new_score), id)
        )
        db.commit()

    return redirect("/deals")

# ---------- DEALS ----------
@app.route("/deals")
def deals():
    db = get_db()
    cur = db.cursor()
    deals = cur.execute("SELECT * FROM deals").fetchall()
    return render_template("deals.html", deals=deals)

# ---------- REMINDERS ----------
@app.route("/reminders", methods=["GET","POST"])
def reminders():
    if "user" not in session:
        return redirect("/")
    db = get_db()
    cur = db.cursor()

    if request.method == "POST":
        cur.execute(
            "INSERT INTO reminders (lead_id,date) VALUES (?,?)",
            (request.form["lead_id"], request.form["date"])
        )
        db.commit()

    leads = cur.execute("SELECT id,name FROM leads").fetchall()
    reminders = cur.execute("""
        SELECT reminders.id, leads.name, reminders.date, reminders.response
        FROM reminders JOIN leads ON reminders.lead_id = leads.id
    """).fetchall()

    return render_template("reminders.html", reminders=reminders, leads=leads)

# ---------- UPDATE RESPONSE ----------
@app.route("/update_response/<int:rid>/<string:resp>")
def update_response(rid, resp):
    db = get_db()
    cur = db.cursor()

    lead_id = cur.execute(
        "SELECT lead_id FROM reminders WHERE id=?",
        (rid,)
    ).fetchone()[0]

    score_add = 10 if resp == "Responded" else 0
    cur.execute("UPDATE leads SET score = score + ? WHERE id=?", (score_add, lead_id))

    score = cur.execute("SELECT score FROM leads WHERE id=?", (lead_id,)).fetchone()[0]
    cur.execute("UPDATE leads SET priority=? WHERE id=?", (priority_from_score(score), lead_id))
    cur.execute("UPDATE reminders SET response=? WHERE id=?", (resp, rid))
    db.commit()

    return redirect("/reminders")

if __name__ == "__main__":
    app.run(debug=True)
@app.route("/reset_all_data")
def reset_all_data():
    db = get_db()
    cur = db.cursor()

    cur.execute("DELETE FROM reminders")
    cur.execute("DELETE FROM deals")
    cur.execute("DELETE FROM leads")
    cur.execute("DELETE FROM products")

    db.commit()
    return "All data cleared"
