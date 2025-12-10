# 第一阶段：构建阶段
FROM docker.1ms.run/python:3.9-slim AS builder
# 使用国内加速镜像源

WORKDIR /build

# 安装编译依赖
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    g++ \
    libjpeg62-turbo-dev \
    zlib1g-dev \
    libfreetype6-dev \
    libwebp-dev \
    && rm -rf /var/lib/apt/lists/*

# 创建虚拟环境
RUN python -m venv /venv
ENV PATH="/venv/bin:$PATH"

# 安装Python依赖
COPY requirements.txt .
RUN pip install --upgrade pip \
    && pip install --no-cache-dir -r requirements.txt \
    && find /venv -name "__pycache__" -type d -exec rm -rf {} + 2>/dev/null

# 第二阶段：运行阶段
FROM docker.1ms.run/python:3.9-alpine
# 使用国内加速镜像源

WORKDIR /app

# 优化Alpine环境
RUN sed -i 's/dl-cdn.alpinelinux.org/mirrors.ustc.edu.cn/g' /etc/apk/repositories \
    && apk update --no-cache \
    && apk add --no-cache \
    libjpeg \
    zlib \
    freetype \
    libwebp \
    tini \
    && adduser -u 1000 -D appuser

# 复制虚拟环境
COPY --from=builder /venv /venv
ENV PATH="/venv/bin:$PATH"

# 仅复制必要的文件
COPY app.py .
COPY backend/app ./backend/app
COPY templates ./templates
COPY static/css ./static/css

# 创建必要的目录
RUN mkdir -p static/icons data static/icons/未分类

# 设置权限
RUN chown -R appuser:appuser /app/static /app/data
RUN chmod -R 755 /app/static /app/data

# 环境变量
ENV FLASK_APP=app.py
ENV FLASK_ENV=production
ENV FLASK_RUN_HOST=0.0.0.0
ENV ICON_STORAGE_PATH=/app/static/icons
ENV DATABASE_URL=sqlite:////app/data/icons.db

# 使用轻量级服务器
RUN pip install --no-cache-dir waitress

# 切换用户
USER appuser

# 暴露端口
EXPOSE 5000

# 使用tini作为init进程，确保正确处理信号和子进程
# 使用更轻量的服务器
ENTRYPOINT ["tini", "--"]
CMD ["waitress-serve", "--host=0.0.0.0", "--port=5000", "app:app"]