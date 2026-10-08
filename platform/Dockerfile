FROM python:3.12-slim

# --- Security: run as a dedicated non-root user (Section 9 requirement) ---
RUN groupadd -r ciphernest && useradd -r -g ciphernest -d /app -s /sbin/nologin ciphernest

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY app/ .

# Writable volume mount point for the flag/submission SQLite DB (Phase 9).
RUN mkdir -p /data && chown -R ciphernest:ciphernest /app /data

USER ciphernest

EXPOSE 5000

CMD ["gunicorn", "--bind", "0.0.0.0:5000", "--workers", "2", "app:app"]
