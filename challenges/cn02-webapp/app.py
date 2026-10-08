import sqlite3
from flask import Flask, request, render_template, redirect, session

app = Flask(__name__)
app.secret_key = "ciphernest-cn02-dev-key"

DB_PATH = "/data/staff.db"

MAINTENANCE_NOTE = """
Maintenance Notes - Staff Portal (Legacy)
------------------------------------------
Scheduled decommission was postponed again. Config backup stored below
uses the old encoding scheme (legacy, not real encryption):

Encoded config: Q2lwaGVyTmVzdHtiMDBsM2FuXzFuajNjdDEwbl9tNHN0M3J9

Keyword used by the ops team for this quarter's backups: NEST

Stage 2 Flag: CipherNest{b00l3an_1nj3ct10n_m4st3r}
"""


def get_db():
    return sqlite3.connect(DB_PATH)


@app.route("/", methods=["GET", "POST"])
def login():
    error = None
    if request.method == "POST":
        username = request.form.get("username", "")
        password = request.form.get("password", "")

        query = f"SELECT * FROM staff WHERE username = '{username}' AND password = '{password}'"
        conn = get_db()
        cur = conn.cursor()
        try:
            cur.execute(query)
            row = cur.fetchone()
        except sqlite3.OperationalError:
            row = None
        conn.close()

        if row:
            session["authenticated"] = True
            return redirect("/cn02/maintenance")
        else:
            error = "Invalid credentials."

    return render_template("login.html", error=error)


@app.route("/maintenance")
def maintenance():
    if not session.get("authenticated"):
        return redirect("/cn02/")
    return render_template("maintenance.html", note=MAINTENANCE_NOTE)


@app.route("/health")
def health():
    return {"status": "ok", "service": "cn02-webapp"}


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8082)
