# Stage 1: Build stage
FROM docker.1ms.run/python:3.9-slim AS builder
# Using domestic acceleration mirror source

WORKDIR /build

# Install build dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    g++ \
    libjpeg62-turbo-dev \
    zlib1g-dev \
    libfreetype6-dev \
    libwebp-dev \
    && rm -rf /var/lib/apt/lists/*

# Create virtual environment
RUN python -m venv /venv
ENV PATH="/venv/bin:$PATH"

# Install Python dependencies
COPY requirements.txt .
RUN pip install --upgrade pip \
    && pip install --no-cache-dir -r requirements.txt \
    && find /venv -name "__pycache__" -type d -exec rm -rf {} + 2>/dev/null

# Stage 2: Runtime stage
FROM docker.1ms.run/python:3.9-alpine
# Using domestic acceleration mirror source

WORKDIR /app

# Optimize Alpine environment
RUN sed -i 's/dl-cdn.alpinelinux.org/mirrors.ustc.edu.cn/g' /etc/apk/repositories \
    && apk update --no-cache \
    && apk add --no-cache \
    libjpeg \
    zlib \
    freetype \
    libwebp \
    tini \
    && adduser -u 1000 -D appuser

# Copy virtual environment
COPY --from=builder /venv /venv
ENV PATH="/venv/bin:$PATH"

# Copy only necessary files
COPY app.py .
COPY backend/app ./backend/app
COPY templates ./templates
COPY static/css ./static/css

# Create necessary directories
RUN mkdir -p static/icons data static/icons/未分类

# Set permissions
RUN chown -R appuser:appuser /app/static /app/data
RUN chmod -R 755 /app/static /app/data

# Environment variables
ENV FLASK_APP=app.py
ENV FLASK_ENV=production
ENV FLASK_RUN_HOST=0.0.0.0
ENV ICON_STORAGE_PATH=/app/static/icons
ENV DATABASE_URL=sqlite:////app/data/icons.db

# Use lightweight server
RUN pip install --no-cache-dir waitress

# Switch user
USER appuser

# Expose port
EXPOSE 5000

# Use tini as init process to ensure proper signal handling and child process management
# Use lightweight server
ENTRYPOINT ["tini", "--"]
CMD ["waitress-serve", "--host=0.0.0.0", "--port=5000", "app:app"]