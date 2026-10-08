FROM python:3.12-slim

RUN pip install --no-cache-dir pyftpdlib

RUN useradd -m -d /home/svc_backup svc_backup
COPY flag.txt /home/svc_backup/flag.txt
RUN chown svc_backup:svc_backup /home/svc_backup/flag.txt

COPY ftp_server.py /app/ftp_server.py
WORKDIR /app

EXPOSE 21 2121-2130
CMD ["python3", "ftp_server.py"]
