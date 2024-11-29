FROM nginx:alpine

RUN apk add --no-cache certbot openssl

RUN rm -f /etc/nginx/conf.d/default.conf && \
    mkdir -p /var/www/html && \
    mkdir -p /etc/letsencrypt

COPY conf.d/default.conf /etc/nginx/conf.d/default.conf

COPY scripts/setup-ssl.sh /setup-ssl.sh
RUN chmod +x /setup-ssl.sh

EXPOSE 80 443

ENTRYPOINT ["/setup-ssl.sh"]
