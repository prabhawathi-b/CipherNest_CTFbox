FROM nginx:1.27-alpine

COPY html_index.html /usr/share/nginx/html/index.html
COPY nginx-cn06.conf /etc/nginx/conf.d/default.conf

RUN chown -R nginx:nginx /usr/share/nginx/html /var/cache/nginx /etc/nginx/conf.d && \
    touch /run/nginx.pid && chown nginx:nginx /run/nginx.pid

USER nginx
EXPOSE 8086
