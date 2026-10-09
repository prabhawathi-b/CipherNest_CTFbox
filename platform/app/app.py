import hashlib
import sqlite3
import time
from pathlib import Path
from flask import Flask, request, jsonify, render_template_string

app = Flask(__name__)

DB_PATH = "/data/flags.db"

FLAG_HASHES = {
    "CN01": "ee02fadf8e0c9a56214fb4ec38e4306795b83ba1e5383780f61722a0967dc59c",
    "CN02": "69b4c17dd966c2a7d14dda176e84451a4350218861329ec822deaeaaf9894915",
    "CN03": "266f466177a1c307b24e8ec780ea56ba6d0f6226c6a5d3542f5aaf573d5eada6",
    "CN04": "f8c429e282c23c1426a1b9548763260d73983d50de32aa4d86046bcacba10e94",
    "CN05": "d38446dc8d4caafc7c9843e09c29b9a7fe882331cf072c7b21b5e2a9cdf54cb3",
    "CN06": "bdea6577d18a952716f6cabec46ba8bb276a31c2539887e7e02776ca3124ce80",
}

# (id, title, domain, difficulty, link, base_pair_symbol, side)
STAGE_INFO = [
    ("CN01", "Frame of Reference", "Steganography", "EASY", "/cn01/", "A", "left"),
    ("CN02", "Back Door Left Ajar", "Web Security", "EASY", "/cn02/", "T", "right"),
    ("CN03", "Weak Locks", "Cryptography", "MODERATE", "/cn03/challenge.txt", "C", "left"),
    ("CN04", "Buried Logs", "Digital Forensics", "MODERATE", "/cn04/", "G", "right"),
    ("CN05", "Whispers on the Wire", "Networking", "MOD-HARD", "/cn05-capture/", "A", "left"),
    ("CN06", "The Nest Revealed", "OSINT / Capstone", "HARD", "/cn06/", "T", "right"),
]

RATE_LIMIT = {}
RATE_LIMIT_WINDOW = 60
RATE_LIMIT_MAX = 10


def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    Path("/data").mkdir(exist_ok=True)
    conn = get_db()
    conn.execute("""
        CREATE TABLE IF NOT EXISTS submissions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            stage TEXT NOT NULL,
            result TEXT NOT NULL,
            ip TEXT,
            timestamp REAL NOT NULL
        )
    """)
    conn.commit()
    conn.close()


def check_rate_limit(ip: str) -> bool:
    now = time.time()
    attempts = RATE_LIMIT.get(ip, [])
    attempts = [t for t in attempts if now - t < RATE_LIMIT_WINDOW]
    if len(attempts) >= RATE_LIMIT_MAX:
        RATE_LIMIT[ip] = attempts
        return False
    attempts.append(now)
    RATE_LIMIT[ip] = attempts
    return True


PAGE_TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
<meta charset="utf-8">
<title>CipherNest :: Digital Genome</title>
<style>
  :root {
    --space: #0B1020;
    --panel: #131a33;
    --panel-border: #262f52;
    --purple: #6366F1;
    --cyan: #22D3EE;
    --magenta: #D946EF;
    --white: #F1F5F9;
    --dim: #8891b5;
    --mono: "Consolas", "SF Mono", monospace;
    --accept: #22D3EE;
    --reject: #D946EF;
  }
  * { box-sizing: border-box; }
  body {
    background: var(--space);
    color: var(--white);
    font-family: var(--mono);
    margin: 0;
    padding: 0;
    background-image:
      radial-gradient(circle at 15% 15%, rgba(99,102,241,0.15) 0%, transparent 45%),
      radial-gradient(circle at 85% 25%, rgba(34,211,238,0.12) 0%, transparent 45%),
      radial-gradient(circle at 50% 90%, rgba(217,70,239,0.10) 0%, transparent 50%);
  }
  header {
    padding: 50px 24px 28px;
    text-align: center;
    border-bottom: 1px solid var(--panel-border);
  }
  header h1 {
    font-size: 2.6em;
    letter-spacing: 0.15em;
    margin: 0;
    background: linear-gradient(90deg, var(--purple), var(--cyan), var(--magenta));
    -webkit-background-clip: text;
    background-clip: text;
    color: transparent;
    font-weight: bold;
  }
  header .subtitle {
    color: var(--dim);
    font-size: 0.85em;
    letter-spacing: 0.05em;
    margin-top: 6px;
  }
  header .tagline {
    color: var(--cyan);
    font-style: italic;
    margin-top: 14px;
    font-size: 0.95em;
  }
  .briefing {
    max-width: 720px;
    margin: 32px auto;
    padding: 20px 24px;
    background: var(--panel);
    border: 1px solid var(--panel-border);
    border-left: 3px solid var(--purple);
    font-size: 0.85em;
    line-height: 1.7;
    color: var(--dim);
    font-family: Georgia, serif;
  }
  .genome {
    max-width: 820px;
    margin: 50px auto 70px;
    padding: 0 24px;
    position: relative;
  }
  .strand {
    position: absolute;
    left: 50%;
    top: 0;
    bottom: 0;
    width: 2px;
    background: linear-gradient(180deg, var(--purple), var(--cyan), var(--magenta));
    transform: translateX(-50%);
    opacity: 0.5;
  }
  .segment-row {
    display: flex;
    align-items: center;
    margin-bottom: 24px;
    position: relative;
  }
  .segment-row.left { justify-content: flex-start; }
  .segment-row.right { justify-content: flex-end; }
  .base-pair {
    position: absolute;
    left: 50%;
    transform: translateX(-50%);
    width: 30px;
    height: 30px;
    border-radius: 50%;
    background: var(--space);
    border: 2px solid var(--cyan);
    color: var(--cyan);
    display: flex;
    align-items: center;
    justify-content: center;
    font-weight: bold;
    font-size: 0.9em;
    z-index: 2;
    box-shadow: 0 0 12px rgba(34,211,238,0.4);
  }
  .segment-card {
    width: 46%;
    background: var(--panel);
    border: 1px solid var(--panel-border);
    border-radius: 4px;
    padding: 16px 18px;
    position: relative;
  }
  .segment-row.left .segment-card { border-right: 3px solid var(--purple); }
  .segment-row.right .segment-card { border-left: 3px solid var(--magenta); }
  .stage-id {
    color: var(--cyan);
    font-weight: bold;
    letter-spacing: 0.05em;
  }
  .stage-title {
    color: var(--white);
    margin-left: 8px;
  }
  .stage-meta {
    font-size: 0.7em;
    color: var(--dim);
    margin-top: 4px;
  }
  .stage-body {
    margin-top: 12px;
    display: flex;
    gap: 8px;
    flex-wrap: wrap;
    align-items: center;
  }
  .stage-link {
    font-size: 0.75em;
    color: var(--purple);
    text-decoration: none;
    border: 1px solid var(--purple);
    padding: 4px 10px;
    border-radius: 2px;
  }
  .stage-link:hover { background: rgba(99,102,241,0.15); }
  .flag-form {
    display: flex;
    gap: 6px;
    flex: 1;
    min-width: 200px;
  }
  .flag-form input {
    flex: 1;
    background: #0a0e1f;
    border: 1px solid var(--panel-border);
    color: var(--white);
    font-family: var(--mono);
    padding: 6px 8px;
    font-size: 0.78em;
    border-radius: 2px;
  }
  .flag-form button {
    background: var(--magenta);
    color: var(--space);
    border: none;
    padding: 6px 12px;
    font-weight: bold;
    cursor: pointer;
    border-radius: 2px;
    font-size: 0.75em;
  }
  .flag-form button:hover { background: var(--cyan); }
  .result {
    font-size: 0.72em;
    margin-top: 8px;
  }
  .result.accept { color: var(--accept); }
  .result.reject { color: var(--reject); }
  .genome-strip {
    text-align: center;
    margin: 40px auto 0;
    color: var(--dim);
    font-size: 0.7em;
    letter-spacing: 0.3em;
  }
  footer {
    text-align: center;
    padding: 30px;
    color: var(--dim);
    font-size: 0.7em;
    border-top: 1px solid var(--panel-border);
  }
  @media (max-width: 700px) {
    .segment-card { width: 80%; }
    .segment-row.left, .segment-row.right { justify-content: center; }
    .strand { display: none; }
    .base-pair { display: none; }
  }
</style>
</head>
<body>

<header>
  <h1>CIPHERNEST</h1>
  <div class="subtitle">:: DIGITAL GENOME ::</div>
  <div class="tagline">"Decode the breach. Reconstruct the identity."</div>
</header>

<div class="briefing">
  CeylonGov Secure's staging environment was compromised. Six fragments of
  the intruder's digital genome are scattered across the environment.
  Recover each segment in sequence to reconstruct the full identity chain
  and prove how the breach occurred.
</div>

<div class="genome">
  <div class="strand"></div>
  {% for id, title, domain, difficulty, link, base, side in stages %}
  <div class="segment-row {{ side }}">
    <div class="base-pair">{{ base }}</div>
    <div class="segment-card">
      <div><span class="stage-id">{{ id }}</span><span class="stage-title">{{ title }}</span></div>
      <div class="stage-meta">{{ domain }} // {{ difficulty }}</div>
      <div class="stage-body">
        <a class="stage-link" href="{{ link }}" target="_blank">OPEN</a>
        <form class="flag-form" onsubmit="submitFlag(event, '{{ id }}')">
          <input type="text" id="input-{{ id }}" placeholder="CipherNest{...}">
          <button type="submit">SUBMIT</button>
        </form>
      </div>
      <div class="result" id="result-{{ id }}"></div>
    </div>
  </div>
  {% endfor %}
</div>

<div class="genome-strip">A T C G &mdash; A T C G &mdash; A T C G</div>

<footer>
  CipherNest CTF Play Box &mdash; IE3132 Penetration Testing &mdash; Group 37
</footer>

<script>
async function submitFlag(event, stage) {
  event.preventDefault();
  const input = document.getElementById('input-' + stage);
  const resultEl = document.getElementById('result-' + stage);
  const flag = input.value.trim();
  resultEl.textContent = 'sequencing...';
  resultEl.className = 'result';
  try {
    const resp = await fetch('/api/submit', {
      method: 'POST',
      headers: {'Content-Type': 'application/json'},
      body: JSON.stringify({stage: stage, flag: flag})
    });
    const data = await resp.json();
    if (data.correct) {
      resultEl.textContent = '? SEGMENT MATCHED - ' + stage + ' verified';
      resultEl.className = 'result accept';
    } else {
      resultEl.textContent = '? NO MATCH - ' + (data.message || 'incorrect sequence');
      resultEl.className = 'result reject';
    }
  } catch (e) {
    resultEl.textContent = '? ERROR - validator unreachable';
    resultEl.className = 'result reject';
  }
}
</script>

</body>
</html>
"""


@app.route("/")
def home():
    return render_template_string(PAGE_TEMPLATE, stages=STAGE_INFO)


@app.route("/api/submit", methods=["POST"])
def submit_flag():
    ip = request.remote_addr or "unknown"
    if not check_rate_limit(ip):
        return jsonify({"correct": False, "message": "rate limit exceeded, try again shortly"}), 429

    data = request.get_json(silent=True) or {}
    stage = (data.get("stage") or "").upper()
    flag = (data.get("flag") or "").strip()

    if stage not in FLAG_HASHES:
        return jsonify({"correct": False, "message": "unknown stage"}), 400

    submitted_hash = hashlib.sha256(flag.encode()).hexdigest()
    correct = submitted_hash == FLAG_HASHES[stage]

    conn = get_db()
    conn.execute(
        "INSERT INTO submissions (stage, result, ip, timestamp) VALUES (?, ?, ?, ?)",
        (stage, "accept" if correct else "reject", ip, time.time()),
    )
    conn.commit()
    conn.close()

    return jsonify({"correct": correct})


@app.route("/health")
def health():
    return {"status": "ok", "service": "ciphernest-platform"}


init_db()

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
