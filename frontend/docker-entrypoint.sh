#!/bin/sh

# Replace environment variables in nginx template
envsubst '${BACKEND_URL}' < /etc/nginx/conf.d/nginx.template.conf > /etc/nginx/conf.d/default.conf

# Remove the template file
rm /etc/nginx/conf.d/nginx.template.conf

# Start nginx
exec nginx -g 'daemon off;'