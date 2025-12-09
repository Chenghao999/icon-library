# API模块初始化文件
from flask import Blueprint

# 创建API蓝图
api_bp = Blueprint('api', __name__)

# 导入各个API路由模块
from . import auth, categories, icons
