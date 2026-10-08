FROM python:3.12-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY app.py .
COPY init_db.py .
COPY templates/ templates/

RUN mkdir -p /data && python3 init_db.py

RUN useradd -r -u 1001 ciphernest && chown -R ciphernest:ciphernest /app /data
USER ciphernest

EXPOSE 8082
CMD ["python3", "app.py"]
