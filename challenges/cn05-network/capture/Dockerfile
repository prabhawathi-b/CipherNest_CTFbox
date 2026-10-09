FROM python:3.12-slim AS builder

RUN pip install --no-cache-dir scapy

WORKDIR /build
COPY generate_pcap.py .
RUN python3 generate_pcap.py

FROM nginx:1.27-alpine AS final

COPY --from=builder /build/evidence_capture.pcap /usr/share/nginx/html/evidence_capture.pcap
COPY nginx-cn05.conf /etc/nginx/conf.d/default.conf

RUN chown -R nginx:nginx /usr/share/nginx/html /var/cache/nginx /etc/nginx/conf.d && \
    touch /run/nginx.pid && chown nginx:nginx /run/nginx.pid

USER nginx
EXPOSE 8085

COPY index.html /usr/share/nginx/html/index.html
