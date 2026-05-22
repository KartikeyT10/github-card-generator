FROM nginx:alpine

# Install envsubst (comes with gettext)
RUN apk add --no-cache gettext

# Copy the template index.html
COPY index.html /usr/share/nginx/html/index.html.template

# Default backend URL (can be overridden at runtime)
ENV BACKEND_URL=http://localhost:8080

# Use a custom entrypoint script to perform the replacement
RUN echo '#!/bin/sh' > /entrypoint.sh && \
    echo 'envsubst "\$BACKEND_URL" < /usr/share/nginx/html/index.html.template > /usr/share/nginx/html/index.html' >> /entrypoint.sh && \
    echo 'nginx -g "daemon off;"' >> /entrypoint.sh && \
    chmod +x /entrypoint.sh

EXPOSE 80

ENTRYPOINT ["/entrypoint.sh"]
