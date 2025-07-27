FROM oraclelinux:8

# Install Nginx, Python and dependencies for nvm
RUN dnf update -y && \
    dnf install -y nginx python3 python3-pip curl && \
    dnf clean all

# Install nvm and Node.js 22 LTS
ENV NVM_DIR=/root/.nvm
RUN curl -o- https://raw.githubusercontent.com/nvm-sh/nvm/v0.40.0/install.sh | bash && \
    . "$NVM_DIR/nvm.sh" && \
    nvm install --lts && \
    nvm alias default lts/* && \
    nvm use default

# Add Node.js to PATH
ENV PATH="$NVM_DIR/versions/node/$(. "$NVM_DIR/nvm.sh" && nvm version default)/bin:$PATH"

# Copy nginx configuration
COPY nginx.conf /etc/nginx/nginx.conf

# Create directory for static files
RUN mkdir -p /usr/share/nginx/html/static

# Start nginx
CMD ["nginx", "-g", "daemon off;"]

EXPOSE 80 443
