FROM docker.1ms.run/python:3.9
# 使用完整版本的Python 3.9替代slim版本，并使用加速镜像源

WORKDIR /app

# 安装图像处理所需的系统依赖
RUN apt-get update && apt-get install -y --no-install-recommends \
    libjpeg62-turbo-dev \
    zlib1g-dev \
    libfreetype6-dev \
    libwebp-dev \
    && rm -rf /var/lib/apt/lists/*

# 创建普通用户
RUN useradd -m -u 1000 appuser

# 复制依赖配置文件
COPY requirements.txt .

# 安装依赖
RUN pip install --no-cache-dir -r requirements.txt

# 复制应用文件
COPY . .

# 创建必要的目录
RUN mkdir -p static/icons static/css templates data static/icons/未分类

# 设置正确的权限
RUN chown -R appuser:appuser /app/static /app/data
RUN chmod -R 755 /app/static /app/data

# 设置环境变量
ENV FLASK_APP=app.py
ENV FLASK_ENV=production
ENV FLASK_RUN_HOST=0.0.0.0
ENV ICON_STORAGE_PATH=/app/static/icons
ENV DATABASE_URL=sqlite:////app/data/icons.db

# 切换到非root用户
USER appuser

# 暴露端口
EXPOSE 5000

# 运行应用
CMD ["gunicorn", "app:app", "--bind", "0.0.0.0:5000", "--timeout", "120", "--log-level", "info", "--error-logfile", "-", "--access-logfile", "-"]