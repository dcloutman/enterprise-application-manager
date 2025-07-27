FROM oraclelinux:9

# Install Nginx
RUN dnf update -y && \
    dnf install -y nginx && \
    dnf clean all

# Create directory for static files
RUN mkdir -p /usr/share/nginx/html/static

# Start nginx
CMD ["nginx", "-g", "daemon off;"]

EXPOSE 80 443
