@echo off

echo 图标管理器本地运行脚本（兼容Python 3.13）
echo ------------------------

REM 创建必要的目录结构
echo 创建必要的目录结构...
mkdir static 2>nul
mkdir static\icons 2>nul
mkdir static\icons\未分类 2>nul
mkdir templates 2>nul
mkdir data 2>nul

REM 检查是否已安装pip，如果没有则提示安装Python
echo 检查Python环境...
pip --version >nul 2>nul
if %ERRORLEVEL% neq 0 (
    echo 错误: 未找到pip，请先安装Python 3.6或更高版本
    echo 推荐安装Python 3.10或3.11以获得最佳兼容性
    pause
    exit /b 1
)

REM 安装所需依赖（使用--user选项避免权限问题）
echo 正在安装Python依赖...
echo 注意：使用--user选项安装到用户目录，避免权限问题
echo 如果安装过程较慢，请耐心等待...
pip install --user -r requirements.txt

if %ERRORLEVEL% neq 0 (
    echo 依赖安装失败！
    echo 请尝试以下解决方案：
    echo 1. 确保有网络连接
    echo 2. 尝试使用管理员权限运行此脚本
    echo 3. 如果仍然失败，可以尝试单独安装Flask: pip install --user flask
    echo 4. 然后运行: python app.py （即使部分依赖未安装，基本功能可能仍可用）
    echo ----------------------------------------
    echo 按1继续安装（重试），按2跳过依赖安装直接运行应用
    choice /c 12 /n
    if %ERRORLEVEL% equ 2 (
        echo 跳过依赖安装，尝试直接运行应用...
    ) else (
        pause
        exit /b 1
    )
)

echo 环境变量设置中...
REM 设置环境变量
set FLASK_APP=app.py
set FLASK_ENV=development
set SECRET_KEY=icon_manager_secret_key
set ICON_STORAGE_PATH=./static/icons

echo 正在启动图标管理器...
echo ----------------------------------------
echo 访问地址: http://localhost:5000
echo ----------------------------------------
echo 提示：
echo - 请在浏览器中打开上述地址访问图标管理器
echo - 如需停止应用，请关闭此窗口或按Ctrl+C

REM 直接使用Python运行应用，避免flask命令的问题
python app.py

if %ERRORLEVEL% neq 0 (
    echo 应用启动失败！
    echo 可能的原因：
    echo 1. 端口5000已被占用
    echo 2. 依赖缺失
    echo 3. 权限问题
    echo 请尝试以管理员权限运行此脚本
)

echo 应用已停止
pause