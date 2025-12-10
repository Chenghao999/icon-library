# 数据库目录

此目录用于存储应用程序的数据库文件。

## 说明

- `icons.db` - SQLite数据库文件（由应用程序自动创建）
- 此文件已在`.gitignore`中配置为忽略
- 首次运行应用程序时会自动初始化数据库结构

## 如何初始化数据库

1. 确保已安装所有依赖：`pip install -r requirements.txt`
2. 运行初始化脚本：`python backend/init_db.py`
3. 或者直接启动应用程序，会自动创建必要的表结构