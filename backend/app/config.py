# 应用配置文件
import os
from datetime import timedelta

class Config:
    """基础配置类"""
    # 应用版本号
    APP_VERSION = "0.1.10"
    
    # 密钥配置
    SECRET_KEY = os.getenv('SECRET_KEY', 'supersecretkey123')
    
    # 图标存储路径
    ICON_STORAGE_PATH = os.getenv('ICON_STORAGE_PATH', '../static/icons')
    
    # 会话配置
    SESSION_TYPE = 'filesystem'  # 使用文件系统存储会话
    SESSION_PERMANENT = True  # 会话持久化
    PERMANENT_SESSION_LIFETIME = timedelta(days=7)  # 会话有效期
    
    # 数据库配置
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # JSON配置
    JSON_SORT_KEYS = False  # 保持JSON响应中键的原始顺序
    
    # 允许的文件扩展名
    ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'svg', 'ico', 'webp'}
    
    # 数据文件路径
    DATA_DIR = '../data'
    ICONS_DATA_FILE = os.path.join(DATA_DIR, 'icons_metadata.json')
    CATEGORIES_DATA_FILE = os.path.join(DATA_DIR, 'categories.json')
    
    @staticmethod
    def ensure_directories():
        """确保必要的目录存在"""
        # 确保图标存储目录存在
        if not os.path.exists(Config.ICON_STORAGE_PATH):
            os.makedirs(Config.ICON_STORAGE_PATH)
            
        # 确保未分类目录存在
        if not os.path.exists(os.path.join(Config.ICON_STORAGE_PATH, '未分类')):
            os.makedirs(os.path.join(Config.ICON_STORAGE_PATH, '未分类'))

        # 确保data目录存在
        if not os.path.exists(Config.DATA_DIR):
            os.makedirs(Config.DATA_DIR)

class DevelopmentConfig(Config):
    """开发环境配置"""
    DEBUG = True
    
    # 数据库路径使用绝对路径
    db_path = os.path.join(os.getcwd(), '../data', 'icons.db')
    SQLALCHEMY_DATABASE_URI = os.getenv('DATABASE_URL', f'sqlite:///{db_path}')

class ProductionConfig(Config):
    """生产环境配置"""
    DEBUG = False
    
    # 数据库路径使用绝对路径
    db_path = os.path.join(os.getcwd(), '../data', 'icons.db')
    SQLALCHEMY_DATABASE_URI = os.getenv('DATABASE_URL', f'sqlite:///{db_path}')

# 根据环境变量选择配置
config_by_name = {
    'dev': DevelopmentConfig,
    'prod': ProductionConfig
}

# 默认配置
default_config = DevelopmentConfig