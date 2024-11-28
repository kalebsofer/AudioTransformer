FROM nginx:alpine

# Install required packages
RUN apk add --no-cache certbot openssl

# Create required directories
RUN rm -f /etc/nginx/conf.d/default.conf && \
    mkdir -p /var/www/html && \
    mkdir -p /etc/letsencrypt

# Copy configuration
COPY conf.d/default.conf /etc/nginx/conf.d/default.conf

# Create SSL setup script
COPY scripts/setup-ssl.sh /setup-ssl.sh
RUN chmod +x /setup-ssl.sh

EXPOSE 80 443

ENTRYPOINT ["/setup-ssl.sh"]
