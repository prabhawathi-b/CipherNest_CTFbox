FROM python:3.12-slim AS builder

WORKDIR /build
COPY evidence_source/ .
RUN python3 build_evidence.py

FROM nginx:1.27-alpine AS final

RUN apk add --no-cache apache2-utils && \
    htpasswd -bc /etc/nginx/.htpasswd archive_user Ar7ifact_Vau1t9 && \
    apk del apache2-utils

COPY --from=builder /build/staging_evidence.bin /usr/share/nginx/html/staging_evidence.bin
COPY nginx-cn04.conf /etc/nginx/conf.d/default.conf

RUN chown -R nginx:nginx /usr/share/nginx/html /var/cache/nginx /etc/nginx/conf.d && \
    touch /run/nginx.pid && chown nginx:nginx /run/nginx.pid

USER nginx
EXPOSE 8084
