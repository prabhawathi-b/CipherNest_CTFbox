FROM python:3.12-slim AS builder

RUN pip install --no-cache-dir Pillow

RUN mkdir -p /build
WORKDIR /build

COPY generate_banner.py .
COPY embed_secret.py .
COPY secret.txt .

RUN python3 generate_banner.py
RUN python3 embed_secret.py

FROM nginx:1.27-alpine AS final

COPY --from=builder /build/ceylongov_banner.png /usr/share/nginx/html/ceylongov_banner.png
COPY html/index.html /usr/share/nginx/html/index.html
COPY nginx-cn01.conf /etc/nginx/conf.d/default.conf

RUN chown -R nginx:nginx /usr/share/nginx/html /var/cache/nginx /etc/nginx/conf.d && \
    touch /run/nginx.pid && chown nginx:nginx /run/nginx.pid

USER nginx

EXPOSE 8081
