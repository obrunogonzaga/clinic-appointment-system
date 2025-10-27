#!/bin/sh

# Generate runtime configuration file
API_URL=${API_URL:-http://localhost:8000}
echo "window.ENV = { API_URL: '${API_URL}' };" > /usr/share/nginx/html/config.js
echo "Generated config.js with API_URL: ${API_URL}"

# Log effective backend URL for debugging behind proxies
echo "Using BACKEND_URL for proxy: ${BACKEND_URL:-<unset>}"

# Replace environment variables in nginx template
envsubst '${BACKEND_URL}' < /etc/nginx/conf.d/nginx.template.conf > /etc/nginx/conf.d/default.conf

# Remove the template file
rm /etc/nginx/conf.d/nginx.template.conf

# Start nginx
exec nginx -g 'daemon off;'
