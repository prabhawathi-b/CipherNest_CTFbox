"""
CipherNest Platform — Phase 1 placeholder.

This is intentionally minimal right now: a single landing route proving
the container builds, starts, and is reachable through Nginx. The real
challenge briefings, flag submission form, and flag-validation logic
(SHA-256 hash checks, submission logging, rate limiting) are added in
Phase 9 once all six challenges and their flags exist.
"""
from flask import Flask

app = Flask(__name__)


@app.route("/")
def index():
    return (
        "<h1>CipherNest</h1>"
        "<p><em>Unravel the Nest. Decode the Truth.</em></p>"
        "<p>Platform skeleton is running. Challenges are not deployed yet "
        "(Phase 1 of the build).</p>"
    )


@app.route("/health")
def health():
    return {"status": "ok", "service": "ciphernest-platform"}, 200


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
