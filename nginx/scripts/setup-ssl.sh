#!/bin/sh

# Wait for nginx config to be available
until [ -f /etc/nginx/conf.d/default.conf ]; do
  sleep 1
done

# Start nginx in background
nginx

# Wait for certbot to do its initial setup
sleep 5

# Start nginx in foreground
nginx -g 'daemon off;'