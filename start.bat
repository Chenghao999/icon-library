@echo off

REM 图标库管理系统启动脚本
REM 版本 0.1.5

echo =================================================================
echo                  图标库管理系统启动脚本
echo =================================================================
echo 注意: 请确保已安装Python和Node.js环境
echo =================================================================

REM 检查backend目录是否存在
if not exist "backend" (
    echo 错误: backend目录不存在！
    pause
    exit /b 1
)

REM 检查frontend目录是否存在
if not exist "frontend" (
    echo 错误: frontend目录不存在！
    pause
    exit /b 1
)

REM 创建后端上传目录
mkdir "backend\uploads\icons" 2>nul

REM 启动后端服务
echo 正在启动后端服务...
start "Icon Store Backend" cmd /c "cd backend && python app.py"

REM 等待后端服务启动
echo 等待后端服务启动...
timeout /t 3 /nobreak >nul

REM 启动前端服务
echo 正在启动前端服务...
start "Icon Store Frontend" cmd /c "cd frontend && npm install && npm run dev"

echo =================================================================
echo 服务启动完成！
echo 后端服务: http://localhost:5000
echo 前端服务: http://localhost:3000
echo =================================================================
echo 按任意键关闭此窗口 (服务将继续在后台运行)

pause
