@echo off

REM 本地运行脚本 - 不使用Docker
setlocal enabledelayedexpansion

REM 创建必要的目录
mkdir static\icons 2>nul
mkdir static\icons\未分类 2>nul
mkdir static\icons\Uncategorized 2>nul

REM 设置环境变量
set FLASK_APP=app.py
set FLASK_ENV=development
set FLASK_RUN_HOST=0.0.0.0
set FLASK_RUN_PORT=5000
set ICON_STORAGE_PATH=static/icons

echo ==========================================
echo 正在启动图标管理器应用 - 本地运行模式
setlocal enabledelayedexpansion

REM 检查Python是否安装
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo 错误：未检测到Python环境，请先安装Python 3.8或更高版本
    echo 安装完成后重新运行此脚本
    pause
    exit /b 1
)

echo 正在安装依赖包...
pip install -r requirements.txt >nul 2>&1
if %errorlevel% neq 0 (
    echo 警告：依赖包安装可能不完整，但将尝试继续运行
)

echo 正在启动应用...
echo 应用启动后请访问 http://localhost:5000

REM 直接使用Python运行Flask应用
python app.py

if %errorlevel% neq 0 (
    echo 应用启动失败，请检查错误信息
    pause
    exit /b 1
)
