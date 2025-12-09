@echo off

echo 图标管理器Docker启动脚本
echo ------------------------

REM 创建必要的目录结构
mkdir static 2>nul
mkdir static\icons 2>nul
mkdir static\icons\未分类 2>nul
mkdir templates 2>nul

REM 检查是否存在Dockerfile，如果不存在则使用已有的
if not exist Dockerfile (
    echo 创建Dockerfile配置文件...
    echo FROM python:3.9-slim > Dockerfile
    echo WORKDIR /app >> Dockerfile
    echo RUN apt-get update ^^^&^^^& apt-get install -y libjpeg62-turbo-dev zlib1g-dev libfreetype6-dev libwebp-dev ^^^&^^^& apt-get clean ^^^&^^^& rm -rf /var/lib/apt/lists/* >> Dockerfile
    echo COPY requirements.txt . >> Dockerfile
    echo RUN pip install --no-cache-dir -r requirements.txt >> Dockerfile
    echo COPY . . >> Dockerfile
    echo RUN mkdir -p static/icons/未分类 templates >> Dockerfile
    echo ENV FLASK_APP=app.py >> Dockerfile
    echo ENV FLASK_ENV=production >> Dockerfile
    echo ENV ICON_STORAGE_PATH=/app/static/icons >> Dockerfile
    echo ENV SECRET_KEY=icon_manager_secret_key >> Dockerfile
    echo RUN chmod -R 755 /app/static/icons >> Dockerfile
    echo EXPOSE 5000 >> Dockerfile
    echo CMD ["gunicorn", "--bind", "0.0.0.0:5000", "app:app"] >> Dockerfile
)

echo 开始构建Docker镜像...
docker build -t icon-manager .

if %ERRORLEVEL% neq 0 (
    echo 构建失败，请检查错误信息
    pause
    exit /b 1
)

echo 构建成功，正在运行容器...
docker run -d -p 5000:5000 --name icon-manager -v %cd%\static\icons:/app/static/icons icon-manager

echo 容器已启动！
echo 访问地址: http://localhost:5000
echo 停止容器: docker stop icon-manager
echo 移除容器: docker rm icon-manager

echo ------------------------------------
echo 按任意键打开浏览器访问应用...
pause >nul
start http://localhost:5000