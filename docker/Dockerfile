# Multi-stage build for Django + SvelteKit application
FROM oraclelinux:9 AS frontend-builder

# Install Node.js 22 LTS via nvm for frontend build
ENV NVM_DIR=/root/.nvm
ENV NODE_VERSION=22
RUN dnf update -y && dnf install -y curl && dnf clean all
RUN curl -o- https://raw.githubusercontent.com/nvm-sh/nvm/v0.40.0/install.sh | bash && \
    . "$NVM_DIR/nvm.sh" && \
    nvm install --lts && \
    nvm alias default lts/* && \
    nvm use default

# Add Node.js to PATH
ENV PATH="$NVM_DIR/versions/node/$(cat $NVM_DIR/alias/default)/bin:$PATH"

WORKDIR /app/frontend
COPY frontend/package*.json ./
RUN . "$NVM_DIR/nvm.sh" && npm ci
COPY frontend/ .
RUN . "$NVM_DIR/nvm.sh" && npm run build

FROM oraclelinux:9 AS backend-base

# Install Python 3.12 and development tools
RUN dnf update -y && \
    dnf install -y python3.12 python3.12-pip python3.12-devel \
    gcc gcc-c++ make \
    pkgconfig \
    curl \
    && dnf clean all

# Add MySQL repo and install MySQL client development packages
RUN dnf install -y https://dev.mysql.com/get/mysql84-community-release-el9-1.noarch.rpm && \
    dnf install -y mysql-community-devel && \
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

# Install system dependencies
RUN dnf install -y \
    nc \
    && dnf clean all

WORKDIR /app

# Install Python dependencies
COPY backend/requirements.txt ./
RUN python3.12 -m pip install --no-cache-dir -r requirements.txt
RUN python3.12 -m pip install gunicorn mysqlclient
RUN python3.12 -m pip install sphinx sphinx-rtd-theme

# Copy backend code
COPY backend/ ./backend/

# Copy and build documentation
COPY docs/ ./docs/
RUN cd docs && sphinx-build -b html . _build/html

# Copy built frontend from previous stage
COPY --from=frontend-builder /app/frontend/build ./frontend/build

# Create entrypoint script
COPY docker/entrypoint.sh ./
RUN chmod +x entrypoint.sh

# Set environment variables
ENV PYTHONPATH=/app/backend
ENV DJANGO_SETTINGS_MODULE=app_tracker.settings
ENV PATH="/usr/bin:$PATH"
ENV PYTHON_CMD=python3.12

EXPOSE 8000 3000

CMD ["./entrypoint.sh"]
