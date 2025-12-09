#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
图标库管理系统后端应用
版本: 0.1.5
"""

import os
import sys
from app import create_app

# 设置系统路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# 创建应用实例
app = create_app()

if __name__ == '__main__':
    # 获取主机和端口配置
    host = os.getenv('FLASK_HOST', '0.0.0.0')
    port = int(os.getenv('FLASK_PORT', 5000))
    debug = os.getenv('FLASK_DEBUG', 'True').lower() == 'true'
    
    # 启动应用
    print(f"图标库管理系统后端服务启动成功")
    print(f"版本: {app.config['APP_VERSION']}")
    print(f"访问地址: http://{host}:{port}")
    print(f"健康检查: http://{host}:{port}/health")
    print(f"API文档: http://{host}:{port}/api")
    
    # 运行应用服务器
    app.run(host=host, port=port, debug=debug)
