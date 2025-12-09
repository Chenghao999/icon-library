# 图标管理器前后端分离架构设计

## 架构概述

本项目采用前后端分离架构，将原有的单体应用拆分为独立的后端API服务和前端静态应用，提高代码可维护性和扩展性。

### 技术栈

**后端：**
- Python Flask - API服务
- SQLite/文件系统 - 数据存储
- RESTful API - 接口规范

**前端：**
- HTML, CSS, JavaScript (原生)
- Axios (HTTP客户端)

## 目录结构

```
icon_store/
├── backend/                # 后端应用
│   ├── app/                # 应用代码
│   │   ├── __init__.py     # 应用初始化
│   │   ├── config.py       # 配置管理
│   │   ├── models/         # 数据模型
│   │   │   ├── __init__.py
│   │   │   ├── base.py     # 基础模型
│   │   │   ├── icon.py     # 图标模型
│   │   │   └── category.py # 分类模型
│   │   ├── api/            # API路由
│   │   │   ├── __init__.py
│   │   │   ├── auth.py     # 认证相关API
│   │   │   ├── icons.py    # 图标相关API
│   │   │   └── categories.py # 分类相关API
│   │   ├── services/       # 业务逻辑
│   │   │   ├── __init__.py
│   │   │   ├── auth_service.py
│   │   │   ├── icon_service.py
│   │   │   └── category_service.py
│   │   ├── utils/          # 工具函数
│   │   │   ├── __init__.py
│   │   │   ├── file_utils.py
│   │   │   └── security_utils.py
│   │   └── middlewares/    # 中间件
│   │       ├── __init__.py
│   │       └── auth.py     # 认证中间件
│   ├── data/               # 数据目录
│   ├── static/             # 静态资源(图标存储)
│   ├── requirements.txt    # 依赖文件
│   └── run.py              # 应用入口
├── frontend/               # 前端应用
│   ├── public/             # 公共资源
│   ├── src/                # 源代码
│   │   ├── components/     # 组件
│   │   ├── styles/         # 样式文件
│   │   ├── utils/          # 工具函数
│   │   ├── api/            # API调用
│   │   └── assets/         # 静态资源
│   ├── index.html          # 主HTML文件
│   └── README.md           # 前端说明文档
├── .env                    # 环境变量配置
├── docker-compose.yml      # Docker Compose配置
└── README.md               # 项目总说明
```

## API设计

### 认证API

- `POST /api/auth/login` - 用户登录
  - 请求体: `{"username": "...", "password": "..."}`
  - 响应: `{"success": true, "message": "登录成功"}` 或 `{"success": false, "message": "用户名或密码错误"}`

- `POST /api/auth/logout` - 用户登出
  - 响应: `{"success": true, "message": "登出成功"}`

- `GET /api/auth/status` - 检查认证状态
  - 响应: `{"authenticated": true, "username": "admin"}` 或 `{"authenticated": false}`

### 图标API

- `GET /api/icons` - 获取所有图标
  - 可选查询参数: `category_id` - 按分类筛选
  - 响应: 图标列表

- `POST /api/icons` - 上传新图标
  - 表单数据: `icon` (文件), `category_id` (可选)
  - 响应: `{"success": true, "icon_id": 1}` 或错误信息

- `GET /api/icons/<id>` - 获取特定图标
  - 响应: 图标详情

- `PUT /api/icons/<id>` - 更新图标信息
  - 请求体: `{"name": "...", "category_id": 1}`
  - 响应: `{"success": true}` 或错误信息

- `DELETE /api/icons/<id>` - 删除图标
  - 响应: `{"success": true}` 或错误信息

### 分类API

- `GET /api/categories` - 获取所有分类
  - 响应: 分类列表

- `POST /api/categories` - 创建新分类
  - 请求体: `{"name": "..."}`
  - 响应: `{"success": true, "category_id": 1}` 或错误信息

- `PUT /api/categories/<id>` - 更新分类
  - 请求体: `{"name": "..."}`
  - 响应: `{"success": true}` 或错误信息

- `DELETE /api/categories/<id>` - 删除分类
  - 响应: `{"success": true}` 或错误信息

## 数据流设计

1. 用户通过前端界面发起请求
2. 前端通过API与后端交互
3. 后端服务处理业务逻辑
4. 后端从数据库/文件系统读取或写入数据
5. 后端返回处理结果给前端
6. 前端更新界面显示

## 部署方式

### 开发环境

1. 后端开发服务器: `python backend/run.py`
2. 前端开发服务器: 使用静态文件服务器(如Live Server)

### Docker部署

使用更新后的docker-compose.yml同时部署前后端服务，并配置适当的网络连接。