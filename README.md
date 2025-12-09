# 图标库管理系统

<p align="center">
  <img src="https://img.shields.io/badge/version-v0.1.5-blue.svg">
  <img src="https://img.shields.io/badge/license-MIT-green.svg">
  <img src="https://img.shields.io/badge/technology-Flask%20%2B%20Vanilla%20JS-blue.svg">
</p>

## 项目介绍

图标库管理系统是一个基于前后端分离架构的Web应用，用于管理和分发各种图标资源。系统支持图标上传、分类管理、搜索下载等功能，适用于团队内部图标资源的统一管理。

## 系统架构

### 前后端分离架构

该项目采用现代化的前后端分离架构：

- **后端**: 使用 Python Flask 框架构建 RESTful API 服务
- **前端**: 使用原生 JavaScript、HTML5 和 CSS3 构建单页应用
- **数据存储**: 支持 SQLite、MySQL、PostgreSQL 等多种数据库
- **文件存储**: 本地文件系统存储图标资源

### 目录结构

```
icon_store/
├── backend/               # 后端应用
│   ├── app/               # 应用主模块
│   │   ├── api/           # API路由层
│   │   ├── models/        # 数据模型层
│   │   ├── services/      # 业务逻辑层
│   │   ├── utils/         # 工具函数
│   │   ├── middlewares/   # 中间件
│   │   ├── config.py      # 配置文件
│   │   └── __init__.py    # 应用初始化
│   ├── uploads/           # 上传文件存储目录
│   ├── app.py             # 应用入口
│   ├── init_db.py         # 数据库初始化脚本
│   ├── requirements.txt   # Python依赖
│   ├── .env               # 环境变量
│   └── .env.example       # 环境变量示例
├── frontend/              # 前端应用
│   ├── public/            # 静态资源
│   ├── src/               # 源码
│   │   ├── api/           # API通信模块
│   │   ├── components/    # 组件
│   │   ├── styles/        # CSS样式
│   │   ├── utils/         # 工具函数
│   │   └── main.js        # 主脚本
│   ├── index.html         # 入口HTML
│   └── package.json       # NPM配置
├── start.bat              # Windows启动脚本
├── start.sh               # Linux/Mac启动脚本
└── README.md              # 项目说明文档
```

### 核心特性

1. **前后端完全分离**
   - 后端提供 RESTful API 接口
   - 前端通过 AJAX 调用接口获取数据
   - 支持跨域资源共享 (CORS)

2. **模块化设计**
   - 后端采用 MVC 架构模式
   - 分层设计：API层、服务层、数据访问层
   - 易于扩展和维护

3. **功能完整**
   - 图标上传、预览、下载
   - 分类管理
   - 用户认证
   - 响应式设计

## 快速开始

### 环境要求

- **Python**: 3.7+
- **Node.js**: 12.x+
- **浏览器**: Chrome, Firefox, Safari, Edge 等现代浏览器

### 一键启动

#### Windows系统

1. 确保已安装 Python 和 Node.js
2. 双击运行 `start.bat` 脚本
3. 浏览器访问 http://localhost:3000

#### Linux/Mac系统

1. 确保已安装 Python 和 Node.js
2. 设置脚本执行权限：`chmod +x start.sh`
3. 运行脚本：`./start.sh`
4. 浏览器访问 http://localhost:3000

### 手动安装

#### 后端安装

```bash
cd backend

# 创建虚拟环境（可选）
python -m venv venv
source venv/bin/activate  # Linux/Mac
venv\Scripts\activate  # Windows

# 安装依赖
pip install -r requirements.txt

# 配置环境变量
cp .env.example .env
# 编辑 .env 文件，设置数据库连接等参数

# 初始化数据库
python init_db.py

# 启动后端服务
python app.py
```

#### 前端安装

```bash
cd frontend

# 安装依赖
npm install

# 开发模式启动
npm run dev

# 或构建生产版本
npm run build
```

## API 文档

### 图标相关接口

- `GET /api/icons` - 获取图标列表
- `GET /api/icons/:id` - 获取单个图标信息
- `POST /api/icons` - 上传新图标
- `DELETE /api/icons/:id` - 删除图标
- `GET /api/icons/files/:filename` - 下载图标文件

### 分类相关接口

- `GET /api/categories` - 获取所有分类
- `POST /api/categories` - 创建新分类
- `DELETE /api/categories/:id` - 删除分类

### 认证相关接口

- `POST /api/auth/login` - 用户登录
- `POST /api/auth/logout` - 用户登出
- `GET /api/auth/status` - 获取登录状态

## 配置说明

### 后端配置

主要配置文件为 `.env`，可设置以下环境变量：

- `FLASK_APP` - Flask应用入口
- `FLASK_ENV` - 运行环境 (development/production)
- `FLASK_DEBUG` - 调试模式
- `FLASK_HOST` - 主机地址
- `FLASK_PORT` - 端口号
- `SECRET_KEY` - 应用密钥
- `SQLALCHEMY_DATABASE_URI` - 数据库连接URI
- `ICON_STORAGE_PATH` - 图标存储路径
- `MAX_CONTENT_LENGTH` - 最大上传文件大小
- `AUTH_USERNAME` - 认证用户名
- `AUTH_PASSWORD` - 认证密码

### 前端配置

前端配置主要在 `src/api/api.js` 中：

- `API_BASE_URL` - 后端API基础URL
- `ICON_BASE_URL` - 图标文件基础URL

## 开发指南

### 后端开发

1. 创建新的API路由：在 `app/api/` 目录下创建新的路由模块
2. 添加业务逻辑：在 `app/services/` 目录下实现业务功能
3. 定义数据模型：在 `app/models/` 目录下创建模型类
4. 添加工具函数：在 `app/utils/` 目录下添加辅助函数

### 前端开发

1. 创建组件：在 `src/components/` 目录下组织UI组件
2. 添加样式：在 `src/styles/` 目录下编写CSS样式
3. API调用：使用全局的 `api` 对象进行后端通信
4. 状态管理：在 `main.js` 中使用 `appState` 对象管理应用状态

## 安全注意事项

1. 生产环境必须修改 `.env` 文件中的默认认证信息
2. 生产环境建议使用 HTTPS 协议
3. 考虑使用更安全的认证机制替代简单认证
4. 合理设置文件上传大小限制，防止DoS攻击
5. 对上传的文件进行严格的类型和内容验证

## 许可证

本项目采用 MIT 许可证。详见 LICENSE 文件。

## 更新日志

### v0.1.5
- 重构为前后端分离架构
- 采用模块化设计，提升代码可维护性
- 优化API设计，支持更多功能
- 增加响应式前端界面
- 提供一键启动脚本

### v0.1.0
- 项目初始版本
- 基础图标管理功能
