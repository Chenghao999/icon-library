# 应用初始化文件
import os
import logging
from flask import Flask, jsonify
from flask_cors import CORS

# 尝试导入数据库相关模块
SQLALCHEMY_AVAILABLE = False
db = None

try:
    from flask_sqlalchemy import SQLAlchemy
    SQLALCHEMY_AVAILABLE = True
except ImportError:
    print("警告: SQLAlchemy 不可用，将使用文件系统存储")

# 导入配置
from app.config import default_config

# 全局变量
app_config = None

def create_app(config_name='dev'):
    """创建Flask应用实例
    
    Args:
        config_name: 配置名称 ('dev' 或 'prod')
    
    Returns:
        Flask应用实例
    """
    global app_config, db
    
    # 创建应用实例
    app = Flask(__name__)
    
    # 使用默认配置
    app_config = default_config()
    app.config.from_object(app_config)
    
    # Logging configuration
    SAVE_LOGS = os.getenv('SAVE_LOGS', 'false').lower() == 'true'
LOG_PATH = os.getenv('LOG_PATH', '/app/data/logs')  # 使用/app/data/logs作为默认路径，与docker卷挂载结构一致
    
    if SAVE_LOGS:
        # Ensure log directory exists
        if not os.path.exists(LOG_PATH):
            os.makedirs(LOG_PATH)
        
        # Configure file logging
        log_file_path = os.path.join(LOG_PATH, 'application.log')
        
        # Set log level and format
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(log_file_path, encoding='utf-8'),  # Specify UTF-8 encoding
                logging.StreamHandler()
            ]
        )
        
        app.logger.info(f'Backend application logs configured to save to: {log_file_path}')
    else:
        # Console logging only
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            handlers=[logging.StreamHandler()]
        )
    
    # 初始化CORS支持，允许跨域请求
    CORS(app, resources={r"/api/*": {"origins": "*"}})
    
    # 确保必要的目录存在
    app_config.ensure_directories()
    
    # 初始化数据库连接
    if SQLALCHEMY_AVAILABLE:
        try:
            db = SQLAlchemy(app)
            print("数据库连接初始化成功")
        except Exception as e:
            print(f"数据库初始化失败: {e}")
            SQLALCHEMY_AVAILABLE = False
    
    # 注册蓝图
    from app.api import api_bp
    app.register_blueprint(api_bp, url_prefix='/api')
    
    # 初始化数据库模型（如果使用数据库存储）
    with app.app_context():
        if SQLALCHEMY_AVAILABLE:
            try:
                # 延迟导入模型以避免循环引用
                from app.models.category import Category
                from app.models.icon import Icon
                
                # 创建表
                db.create_all()
                
                # 检查是否存在默认分类，如果不存在则创建
                default_category = Category.query.filter_by(name='未分类').first()
                if not default_category:
                    default_category = Category(name='未分类')
                    db.session.add(default_category)
                    db.session.commit()
                    print("创建默认分类 '未分类'")
                    
            except Exception as e:
                print(f"数据库模型初始化失败: {e}")
                SQLALCHEMY_AVAILABLE = False
    
    # 添加错误处理
    @app.errorhandler(404)
    def not_found(error):
        return jsonify({"error": "资源不存在"}), 404
    
    @app.errorhandler(500)
    def internal_error(error):
        return jsonify({"error": "服务器内部错误"}), 500
    
    @app.errorhandler(401)
    def unauthorized(error):
        return jsonify({"error": "未授权访问"}), 401
    
    # 添加健康检查端点
    @app.route('/health')
    def health_check():
        return jsonify({
            "status": "ok",
            "version": app_config.APP_VERSION,
            "storage_type": "database" if SQLALCHEMY_AVAILABLE else "file_system"
        })
    
    return app

# 导出可用的存储类型
from app.models.base import STORAGE_TYPES
