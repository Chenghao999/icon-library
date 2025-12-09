FROM python:3.9-slim

WORKDIR /app

# 安装图像处理所需的系统依赖
RUN apt-get update && apt-get install -y --no-install-recommends \
    libjpeg62-turbo-dev \
    zlib1g-dev \
    libfreetype6-dev \
    libwebp-dev \
    && rm -rf /var/lib/apt/lists/*

# 复制依赖配置文件
COPY requirements.txt .

# 安装依赖
RUN pip install --no-cache-dir -r requirements.txt

# 复制应用文件
COPY . .

# 创建必要的目录
RUN mkdir -p static/icons static/css templates data static/icons/未分类

# 设置环境变量
ENV FLASK_APP=app.py
ENV FLASK_ENV=production
ENV FLASK_RUN_HOST=0.0.0.0
ENV ICON_STORAGE_PATH=static/icons

# 确保图标目录有正确的权限
RUN chmod -R 755 static/icons

# 暴露端口
EXPOSE 5000

# 运行应用
CMD ["gunicorn", "-b", "0.0.0.0:5000", "app:app"]