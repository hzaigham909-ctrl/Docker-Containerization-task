FROM nginx:alpine

# Clean default config (optional but recommended)
RUN rm -f /etc/nginx/conf.d/default.conf

# Copy your fixed config
COPY nginx.conf /etc/nginx/conf.d/default.conf