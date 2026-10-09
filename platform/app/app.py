import hashlib, hmac, os, re, sqlite3, time
from pathlib import Path
from flask import Flask, request, jsonify, render_template, redirect, session, url_for
from werkzeug.security import generate_password_hash, check_password_hash

DB_PATH = "/data/flags.db"
KEY_PATH = "/data/secret.key"

FLAG_HASHES = {
    "CN01": "ee02fadf8e0c9a56214fb4ec38e4306795b83ba1e5383780f61722a0967dc59c",
    "CN02": "69b4c17dd966c2a7d14dda176e84451a4350218861329ec822deaeaaf9894915",
    "CN03": "266f466177a1c307b24e8ec780ea56ba6d0f6226c6a5d3542f5aaf573d5eada6",
    "CN04": "f8c429e282c23c1426a1b9548763260d73983d50de32aa4d86046bcacba10e94",
    "CN05": "d38446dc8d4caafc7c9843e09c29b9a7fe882331cf072c7b21b5e2a9cdf54cb3",
    "CN06": "bdea6577d18a952716f6cabec46ba8bb276a31c2539887e7e02776ca3124ce80",
}

STAGES = [
    {"id": "CN01", "title": "Frame of Reference", "domain": "Steganography", "diff": "Easy", "link": "/cn01/", "label": "Open briefing"},
    {"id": "CN02", "title": "Back Door Left Ajar", "domain": "Web Security", "diff": "Easy", "link": "/cn02/", "label": "Open portal"},
    {"id": "CN03", "title": "Weak Locks", "domain": "Cryptography", "diff": "Moderate", "link": "/cn03/challenge.txt", "label": "Open artifact"},
    {"id": "CN04", "title": "Buried Logs", "domain": "Digital Forensics", "diff": "Moderate", "link": "/cn04/", "label": "Open archive"},
    {"id": "CN05", "title": "Whispers on the Wire", "domain": "Networking", "diff": "Moderate-Hard", "link": "/cn05-capture/", "label": "Open capture"},
    {"id": "CN06", "title": "The Nest Revealed", "domain": "OSINT / Capstone", "diff": "Hard", "link": "/cn06/", "label": "Open profile"},
]

RATE = {}
RATE_WINDOW, RATE_MAX = 60, 10


def load_key():
    Path("/data").mkdir(exist_ok=True)
    try:
        with open(KEY_PATH, "x") as f:
            f.write(os.urandom(32).hex())
    except FileExistsError:
        pass
    for _ in range(20):
        k = Path(KEY_PATH).read_text().strip()
        if k:
            return k
        time.sleep(0.1)
    raise RuntimeError("secret key unavailable")


app = Flask(__name__)
app.secret_key = load_key()
app.config.update(SESSION_COOKIE_SAMESITE="Lax", SESSION_COOKIE_HTTPONLY=True)


def db():
    c = sqlite3.connect(DB_PATH, timeout=10)
    c.row_factory = sqlite3.Row
    return c


def init_db():
    c = db()
    c.executescript("""
    CREATE TABLE IF NOT EXISTS submissions (id INTEGER PRIMARY KEY AUTOINCREMENT, stage TEXT NOT NULL, result TEXT NOT NULL, ip TEXT, timestamp REAL NOT NULL);
    CREATE TABLE IF NOT EXISTS users (id INTEGER PRIMARY KEY AUTOINCREMENT, username TEXT NOT NULL UNIQUE COLLATE NOCASE, pw_hash TEXT NOT NULL, created REAL NOT NULL);
    CREATE TABLE IF NOT EXISTS solves (user_id INTEGER NOT NULL, stage TEXT NOT NULL, ts REAL NOT NULL, PRIMARY KEY (user_id, stage));
    """)
    try:
        if "user_id" not in [r["name"] for r in c.execute("PRAGMA table_info(submissions)")]:
            c.execute("ALTER TABLE submissions ADD COLUMN user_id INTEGER")
    except sqlite3.OperationalError:
        pass  # another worker added it first
    c.commit()
    c.close()


def allowed(key):
    now = time.time()
    hits = [t for t in RATE.get(key, []) if now - t < RATE_WINDOW]
    ok = len(hits) < RATE_MAX
    if ok:
        hits.append(now)
    RATE[key] = hits
    return ok


def client_ip():
    return request.headers.get("X-Real-IP") or request.remote_addr or "unknown"


def current_user():
    uid = session.get("uid")
    if not uid:
        return None
    c = db()
    u = c.execute("SELECT id, username FROM users WHERE id=?", (uid,)).fetchone()
    c.close()
    return u


def solved_set(uid):
    c = db()
    rows = c.execute("SELECT stage FROM solves WHERE user_id=?", (uid,)).fetchall()
    c.close()
    return {r["stage"] for r in rows}


@app.context_processor
def inject_user():
    return {"user": current_user()}


@app.route("/")
def home():
    return render_template("landing.html")


@app.route("/register", methods=["GET", "POST"])
def register():
    if current_user():
        return redirect(url_for("dashboard"))
    error = None
    if request.method == "POST":
        name = request.form.get("username", "").strip()
        pw = request.form.get("password", "")
        if not re.fullmatch(r"[A-Za-z0-9_]{3,20}", name):
            error = "Callsign must be 3-20 letters, numbers or underscores."
        elif len(pw) < 8:
            error = "Password must be at least 8 characters."
        elif pw != request.form.get("confirm", ""):
            error = "Passwords do not match."
        else:
            c = db()
            try:
                cur = c.execute("INSERT INTO users (username, pw_hash, created) VALUES (?,?,?)",
                                (name, generate_password_hash(pw), time.time()))
                c.commit()
                session.clear()
                session["uid"] = cur.lastrowid
                return redirect(url_for("dashboard"))
            except sqlite3.IntegrityError:
                error = "That callsign is already taken."
            finally:
                c.close()
    return render_template("auth.html", mode="register", error=error)


@app.route("/login", methods=["GET", "POST"])
def login():
    if current_user():
        return redirect(url_for("dashboard"))
    error = None
    if request.method == "POST":
        if not allowed("login:" + client_ip()):
            error = "Too many attempts. Wait a minute and try again."
        else:
            c = db()
            u = c.execute("SELECT id, pw_hash FROM users WHERE username=?",
                          (request.form.get("username", "").strip(),)).fetchone()
            c.close()
            if u and check_password_hash(u["pw_hash"], request.form.get("password", "")):
                session.clear()
                session["uid"] = u["id"]
                return redirect(url_for("dashboard"))
            error = "Invalid callsign or password."
    return render_template("auth.html", mode="login", error=error)


@app.route("/logout", methods=["POST"])
def logout():
    session.clear()
    return redirect(url_for("home"))


@app.route("/dashboard")
def dashboard():
    u = current_user()
    if not u:
        return redirect(url_for("login"))
    done = solved_set(u["id"])
    nxt = next((s["id"] for s in STAGES if s["id"] not in done), None)
    pct = round(100 * len(done) / len(STAGES))
    return render_template("dashboard.html", stages=STAGES, done=done, nxt=nxt, pct=pct)


@app.route("/api/submit", methods=["POST"])
def submit_flag():
    u = current_user()
    ip = client_ip()
    if not allowed("u%s" % u["id"] if u else ip):
        return jsonify({"correct": False, "message": "Rate limit exceeded. Try again shortly."}), 429
    data = request.get_json(silent=True) or {}
    stage = (data.get("stage") or "").upper()
    flag = (data.get("flag") or "").strip()
    if stage not in FLAG_HASHES:
        return jsonify({"correct": False, "message": "Unknown stage."}), 400
    correct = hmac.compare_digest(hashlib.sha256(flag.encode()).hexdigest(), FLAG_HASHES[stage])
    c = db()
    c.execute("INSERT INTO submissions (stage, result, ip, timestamp, user_id) VALUES (?,?,?,?,?)",
              (stage, "accept" if correct else "reject", ip, time.time(), u["id"] if u else None))
    if correct and u:
        c.execute("INSERT OR IGNORE INTO solves (user_id, stage, ts) VALUES (?,?,?)", (u["id"], stage, time.time()))
    c.commit()
    c.close()
    resp = {"correct": correct}
    if not correct:
        resp["message"] = "That flag does not match. Check the format and try again."
    if u:
        resp["solved"] = len(solved_set(u["id"]))
    return jsonify(resp)


@app.route("/health")
def health():
    return {"status": "ok", "service": "ciphernest-platform"}


init_db()

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
