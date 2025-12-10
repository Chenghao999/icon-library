#!/bin/bash

# 图标库管理系统启动脚本
# 版本 0.1.10

echo "================================================================="
echo "                  图标库管理系统启动脚本"
echo "================================================================="
echo "注意: 请确保已安装Python和Node.js环境"
echo "================================================================="

# 检查backend目录是否存在
if [ ! -d "backend" ]; then
    echo "错误: backend目录不存在！"
    exit 1
fi

# 检查frontend目录是否存在
if [ ! -d "frontend" ]; then
    echo "错误: frontend目录不存在！"
    exit 1
fi

# 创建后端上传目录
mkdir -p "backend/uploads/icons"

# 启动后端服务
echo "正在启动后端服务..."
cd backend && python app.py &
BACKEND_PID=$!

# 等待后端服务启动
echo "等待后端服务启动..."
sleep 3

# 启动前端服务
echo "正在启动前端服务..."
cd ../frontend && npm install && npm run dev &
FRONTEND_PID=$!

echo "================================================================="
echo "服务启动完成！"
echo "后端服务: http://localhost:5000"
echo "前端服务: http://localhost:3000"
echo "================================================================="
echo "按 Ctrl+C 关闭所有服务"

# 等待用户中断
wait $BACKEND_PID $FRONTEND_PID

# 清理服务
kill $BACKEND_PID $FRONTEND_PID 2>/dev/null
echo "服务已关闭"
