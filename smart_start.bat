@echo off

REM 智能启动脚本 - 自动检测并适配依赖环境
echo ==========================================
echo 图标管理器智能启动脚本

REM 检查Python环境
python --version 2>nul || (echo 错误：未找到Python环境，请先安装Python 3.6+ && pause && exit /b 1)

REM 创建必要的目录结构
mkdir static\icons 2>nul
mkdir static\icons\Uncategorized 2>nul
mkdir static\icons\未分类 2>nul
mkdir data 2>nul
mkdir instance 2>nul

REM 创建依赖检测脚本
echo 正在检测依赖环境...
echo import sys; print('Python version:', sys.version) > check_deps.py
echo try:
    import flask
    print('Flask:', flask.__version__)
except ImportError:
    print('✗ Flask 未安装')
try:
    from flask_sqlalchemy import SQLAlchemy
    print('✓ Flask-SQLAlchemy 可用')
except ImportError:
    print('✗ Flask-SQLAlchemy 未安装')
try:
    import pymongo
    print('✓ pymongo:', pymongo.__version__)
except ImportError:
    print('✗ pymongo 未安装')
try:
    import pandas
    print('✓ pandas:', pandas.__version__)
except ImportError:
    print('✗ pandas 未安装')
try:
    import PIL
    print('✓ Pillow:', PIL.__version__)
except ImportError:
    print('✗ Pillow 未安装')
>> check_deps.py

REM 运行依赖检测
python check_deps.py
del check_deps.py

echo.
echo 环境检测完成，开始启动应用程序...
echo.

REM 设置必要的环境变量
set FLASK_APP=app.py
set FLASK_ENV=development

REM 启动应用程序
echo 正在启动图标管理器...
echo 访问地址：http://localhost:5000
echo 提示：按 Ctrl+C 停止服务
echo.

python -m flask run --host=0.0.0.0 --port=5000