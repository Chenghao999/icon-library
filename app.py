# 简化版本的图标管理器
# 确保基本功能可用，减少依赖要求

# 应用版本号
APP_VERSION = "0.1.10"
from flask import Flask, render_template, request, redirect, url_for, flash, send_from_directory, jsonify, session, make_response, send_file
import os
import json
import logging
from datetime import datetime
import re
from urllib.parse import quote

# 尝试导入额外依赖，但即使失败也继续运行
try:
    from werkzeug.utils import secure_filename
    secure_filename_available = True
except ImportError:
    secure_filename_available = False

try:
    from flask_sqlalchemy import SQLAlchemy
    from dotenv import load_dotenv
    sqlalchemy_available = True
    # 尝试加载环境变量
    try:
        load_dotenv()
    except:
        pass
except ImportError:
    sqlalchemy_available = False

# 从环境变量获取管理员账号和密码
ADMIN_USERNAME = os.getenv('ADMIN_USERNAME')
ADMIN_PASSWORD = os.getenv('ADMIN_PASSWORD')

# 如果环境变量未设置，使用默认值并记录警告
if not ADMIN_USERNAME:
    print('警告: ADMIN_USERNAME 环境变量未设置，使用默认值')
    ADMIN_USERNAME = 'admin'
if not ADMIN_PASSWORD:
    print('警告: ADMIN_PASSWORD 环境变量未设置，使用默认值')
    ADMIN_PASSWORD = 'password123'

# 用户认证相关函数
def is_authenticated():
    """检查用户是否已认证"""
    return session.get('authenticated') and session.get('username') == ADMIN_USERNAME

def login_user():
    """用户登录"""
    session['authenticated'] = True
    session['username'] = ADMIN_USERNAME

def logout_user():
    """用户登出"""
    session.pop('authenticated', None)
    session.pop('username', None)

def login_required(f):
    """登录装饰器，用于保护需要认证的路由"""
    def decorated_function(*args, **kwargs):
        if not is_authenticated():
            return jsonify({'success': False, 'message': '请先登录'}), 401
        return f(*args, **kwargs)
    decorated_function.__name__ = f.__name__
    return decorated_function


# 注意：登录相关路由将在app实例创建后定义

# 简化的secure_filename实现
def simple_secure_filename(filename):
    """简化版的文件名安全处理"""
    # 移除或替换不安全字符
    filename = re.sub(r'[\\/:*?"<>|]', '_', filename)
    return filename.strip() or 'unnamed_file'

# 创建Flask应用
app = Flask(__name__)

# 登录相关路由
@app.route('/login', methods=['GET', 'POST'])
def login():
    """处理用户登录请求"""
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '').strip()
        
        # 验证用户名和密码
        if username == ADMIN_USERNAME and password == ADMIN_PASSWORD:
            login_user()
            # 登录成功后重定向到首页
            return redirect(url_for('index'))
        else:
            # 登录失败，显示错误信息
            return render_template('login.html', error='用户名或密码错误')
    
    # GET 请求，显示登录页面
    return render_template('login.html')


@app.route('/logout')
def logout():
    """处理用户登出请求"""
    logout_user()
    # 登出后重定向到首页
    return redirect(url_for('index'))


@app.route('/api/auth/status')
def auth_status():
    """检查用户认证状态的API端点"""
    return jsonify({
        'authenticated': is_authenticated(),
        'username': session.get('username') if is_authenticated() else None
    })
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'supersecretkey123')
app.config['ICON_STORAGE_PATH'] = os.getenv('ICON_STORAGE_PATH', 'data/static/icons')  # 使用data/static/icons作为默认路径，与docker卷挂载结构一致
app.config['SESSION_TYPE'] = 'filesystem'  # 使用文件系统存储会话
app.config['SESSION_PERMANENT'] = True  # 会话持久化

# Logging configuration
SAVE_LOGS = os.getenv('SAVE_LOGS', 'false').lower() == 'true'
LOG_PATH = os.getenv('LOG_PATH', 'data/logs')  # 使用data/logs作为默认路径，与docker卷挂载结构一致

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
    
    app.logger.info(f'Application logs configured to save to: {log_file_path}')
else:
    # Console logging only
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[logging.StreamHandler()]
    )

# 确保图标存储目录存在
if not os.path.exists(app.config['ICON_STORAGE_PATH']):
    os.makedirs(app.config['ICON_STORAGE_PATH'])
    
# 确保未分类目录存在
if not os.path.exists(os.path.join(app.config['ICON_STORAGE_PATH'], '未分类')):
    os.makedirs(os.path.join(app.config['ICON_STORAGE_PATH'], '未分类'))

# 确保data目录存在
if not os.path.exists('data'):
    os.makedirs('data')

# 文件系统存储的JSON数据文件
ICONS_DATA_FILE = 'data/icons_metadata.json'
CATEGORIES_DATA_FILE = 'data/categories.json'

# 简化的数据模型类（用于文件系统存储）
class SimpleCategory:
    def __init__(self, id, name):
        self.id = id
        self.name = name

class SimpleIcon:
    def __init__(self, id, filename, original_filename, category_id=1, category_name='未分类', **kwargs):
        self.id = id
        self.filename = filename
        self.original_filename = original_filename
        self.category_id = category_id
        self.category_name = category_name
        # 如果提供了upload_date参数，则使用它，否则创建新的
        self.upload_date = kwargs.get('upload_date', datetime.utcnow())
        # 如果提供了is_favorite参数，则使用它，否则默认为False
        self.is_favorite = kwargs.get('is_favorite', False)
    
    @property
    def url(self):
        # 生成图标URL路径，包含分类路径
        # 使用url_for生成相对路径，而不是绝对URL
        return url_for('serve_icon', filename=os.path.join(self.category_name, self.filename))

# 根据是否有SQLAlchemy选择不同的数据存储方式
if sqlalchemy_available:
    try:
        # 配置SQLAlchemy
        # 使用绝对路径来避免Docker容器中的权限问题
        db_path = os.path.join(os.getcwd(), 'data', 'icons.db')
        app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL', f'sqlite:///{db_path}')
        app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
        
        # 确保数据库目录有写入权限
        if not os.path.exists('data'):
            os.makedirs('data')
        
        # 尝试设置数据目录权限（如果可能）
        try:
            os.chmod('data', 0o755)
        except:
            print("警告: 无法修改data目录权限，但将继续尝试初始化数据库")
        
        # 初始化数据库
        db = SQLAlchemy(app)
        
        # 定义数据库模型
        class Category(db.Model):
            id = db.Column(db.Integer, primary_key=True)
            name = db.Column(db.String(50), unique=True, nullable=False)
            icons = db.relationship('Icon', backref='category', lazy=True)

        class Icon(db.Model):
            id = db.Column(db.Integer, primary_key=True)
            filename = db.Column(db.String(255), nullable=False)
            original_filename = db.Column(db.String(255), nullable=False)
            category_id = db.Column(db.Integer, db.ForeignKey('category.id'), nullable=True)
            upload_date = db.Column(db.DateTime, default=datetime.utcnow)
            is_favorite = db.Column(db.Boolean, default=False)
            
            @property
            def url(self):
                # 生成图标URL路径，包含分类路径
                # 使用url_for生成相对路径，而不是绝对URL
                category_folder = '未分类' if not self.category else self.category.name
                return url_for('serve_icon', filename=os.path.join(category_folder, self.filename))
            
            @property
            def category_name(self):
                return '未分类' if not self.category else self.category.name
    except Exception as e:
        print(f"SQLAlchemy初始化失败，将使用文件系统存储: {e}")
        sqlalchemy_available = False

# 文件系统存储函数
def load_json_data(filename, default_data=None):
    """从JSON文件加载数据"""
    if default_data is None:
        default_data = []
    
    try:
        if os.path.exists(filename):
            with open(filename, 'r', encoding='utf-8') as f:
                return json.load(f)
    except Exception as e:
        print(f"加载{filename}失败: {e}")
    
    return default_data

def save_json_data(filename, data):
    """保存数据到JSON文件"""
    try:
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2, default=str)
        return True
    except Exception as e:
        print(f"保存{filename}失败: {e}")
        return False

def get_file_categories():
    """从文件系统获取分类列表"""
    categories = load_json_data(CATEGORIES_DATA_FILE, [])
    if not categories:
        # 创建默认分类
        categories = [{'id': 1, 'name': '未分类'}]
        save_json_data(CATEGORIES_DATA_FILE, categories)
    
    # 转换为SimpleCategory对象列表
    return [SimpleCategory(**cat) for cat in categories]

def get_file_icons():
    """从文件系统获取所有图标"""
    icons_data = load_json_data(ICONS_DATA_FILE, [])
    categories_dict = {cat.id: cat.name for cat in get_file_categories()}
    
    # 转换为SimpleIcon对象列表
    icons = []
    for icon_data in icons_data:
        # 确保有category_name字段
        if 'category_name' not in icon_data:
            icon_data['category_name'] = categories_dict.get(icon_data.get('category_id'), '未分类')
        
        # 添加额外的安全检查，确保必要字段存在
        required_fields = ['id', 'filename', 'original_filename']
        missing_fields = [f for f in required_fields if f not in icon_data]
        if missing_fields:
            print(f"警告: 图标数据缺少必要字段 {missing_fields}, 跳过该图标")
            continue
            
        try:
            icons.append(SimpleIcon(**icon_data))
        except Exception as e:
            print(f"创建SimpleIcon对象失败: {e}, 图标数据: {icon_data}")
    
    return icons

def add_file_category(category_name):
    """添加新分类到文件系统"""
    categories = load_json_data(CATEGORIES_DATA_FILE, [])
    
    # 检查分类是否已存在
    for cat in categories:
        if cat['name'] == category_name:
            return False
    
    # 创建新分类目录
    category_path = os.path.join(app.config['ICON_STORAGE_PATH'], category_name)
    if not os.path.exists(category_path):
        os.makedirs(category_path)
    
    # 添加分类数据
    new_id = max([cat['id'] for cat in categories], default=0) + 1
    categories.append({'id': new_id, 'name': category_name})
    save_json_data(CATEGORIES_DATA_FILE, categories)
    
    return True

def add_file_icon(filename, original_filename, category_id=1, category_name='未分类'):
    """添加新图标到文件系统"""
    icons = load_json_data(ICONS_DATA_FILE, [])
    
    # 生成新ID
    new_id = max([icon['id'] for icon in icons], default=0) + 1
    
    # 添加图标数据
    new_icon = {
        'id': new_id,
        'filename': filename,
        'original_filename': original_filename,
        'category_id': category_id,
        'category_name': category_name,
        'upload_date': str(datetime.utcnow()),
        'is_favorite': False
    }
    
    icons.append(new_icon)
    save_json_data(ICONS_DATA_FILE, icons)
    
    return new_id

def delete_file_icon(icon_id):
    """从文件系统删除图标"""
    icons = load_json_data(ICONS_DATA_FILE, [])
    icon_to_delete = None
    
    # 查找要删除的图标
    for i, icon in enumerate(icons):
        if icon['id'] == icon_id:
            icon_to_delete = icon
            del icons[i]
            break
    
    if not icon_to_delete:
        return False
    
    # 保存更新后的数据
    save_json_data(ICONS_DATA_FILE, icons)
    
    # 删除文件
    file_path = os.path.join(app.config['ICON_STORAGE_PATH'], 
                           icon_to_delete.get('category_name', '未分类'), 
                           icon_to_delete['filename'])
    if os.path.exists(file_path):
        try:
            os.remove(file_path)
        except Exception as e:
            print(f"删除文件失败: {e}")
    
    return True

# 初始化数据库或文件系统存储
with app.app_context():
    # 确保基础目录存在
    if not os.path.exists('data'):
        os.makedirs('data')
    
    if not os.path.exists(app.config['ICON_STORAGE_PATH']):
        os.makedirs(app.config['ICON_STORAGE_PATH'])
    
    # 确保未分类目录存在
    default_category_path = os.path.join(app.config['ICON_STORAGE_PATH'], '未分类')
    if not os.path.exists(default_category_path):
        os.makedirs(default_category_path)
    
    # 根据是否有SQLAlchemy选择不同的初始化方式
    if sqlalchemy_available:
        try:
            # 使用数据库方式
            db.create_all()
            
            # 创建默认分类
            default_category = Category.query.filter_by(name='未分类').first()
            if not default_category:
                default_category = Category(name='未分类')
                db.session.add(default_category)
                db.session.commit()
            
            print("数据库初始化成功")
        except Exception as e:
            print(f"数据库初始化失败，将使用文件系统存储: {e}")
            sqlalchemy_available = False
            # 确保文件系统存储有默认分类
            get_file_categories()
    else:
        # 使用文件系统存储方式
        print("使用文件系统存储")
        # 确保有默认分类
        get_file_categories()

# 允许的文件扩展名
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'svg', 'ico', 'webp'}

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def generate_secure_filename(filename):
    # 生成安全的文件名，使用时间戳生成唯一文件名
    ext = filename.rsplit('.', 1)[1].lower() if '.' in filename else ''
    timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
    secure_name = f"icon_{timestamp}.{ext}" if ext else f"icon_{timestamp}"
    return secure_name

def create_category_folder(category_name):
    """创建分类文件夹"""
    category_path = os.path.join(app.config['ICON_STORAGE_PATH'], category_name)
    if not os.path.exists(category_path):
        os.makedirs(category_path)
    return category_path

def sanitize_path(path):
    """清理路径，防止路径遍历攻击"""
    # 移除可能的路径遍历攻击字符，但保留路径分隔符(/)
    sanitized = re.sub(r'[\\\:\*\?"\<\>\|]', '_', path)
    return sanitized

def get_categories():
    """获取所有分类，兼容两种存储方式"""
    if sqlalchemy_available:
        try:
            return Category.query.all()
        except Exception as e:
            print(f"获取数据库分类失败: {e}")
    return get_file_categories()

def get_icons():
    """获取所有图标，兼容两种存储方式"""
    if sqlalchemy_available:
        try:
            return Icon.query.all()
        except Exception as e:
            print(f"获取数据库图标失败: {e}")
    return get_file_icons()

# 路由定义
@app.route('/')
def index():
    # 获取所有分类和图标，兼容两种存储方式
    categories = get_categories()
    icons = get_icons()
    
    return render_template('index.html', categories=categories, icons=icons)

@app.route('/upload', methods=['POST'])
@login_required
def upload_icon():
    # 检查是否有文件上传
    if 'icon' not in request.files:
        flash('没有文件被上传')
        return redirect(request.url)
    
    file = request.files['icon']
    
    # 检查文件名是否为空
    if file.filename == '':
        flash('没有选择文件')
        return redirect(request.url)
    
    # 检查文件类型是否允许
    if file and allowed_file(file.filename):
        # 生成安全的文件名
        original_filename = secure_filename(file.filename) if secure_filename_available else simple_secure_filename(file.filename)
        unique_filename = generate_secure_filename(file.filename)
        
        # 获取分类
        category_id = request.form.get('category_id', '1')
        
        # 根据存储方式获取分类信息
        if sqlalchemy_available:
            try:
                category = Category.query.get(int(category_id))
                category_name = category.name if category else '未分类'
                
                # 如果没有选择分类，使用默认分类
                if not category:
                    category = Category.query.filter_by(name='未分类').first()
                    category_name = category.name
                    category_id = category.id
            except Exception as e:
                print(f"获取分类失败: {e}")
                category_name = '未分类'
                category_id = 1
        else:
            # 使用文件系统存储的分类
            categories = get_file_categories()
            category_name = '未分类'
            for cat in categories:
                if str(cat.id) == category_id:
                    category_name = cat.name
                    break
        
        # 创建分类文件夹
        category_path = create_category_folder(category_name)
        
        # 保存文件
        file_path = os.path.join(category_path, unique_filename)
        file.save(file_path)
        
        # 根据存储方式保存图标信息
        if sqlalchemy_available:
            try:
                # 保存到数据库
                new_icon = Icon(
                    filename=unique_filename,
                    original_filename=original_filename,
                    category_id=int(category_id)
                )
                db.session.add(new_icon)
                db.session.commit()
            except Exception as e:
                print(f"保存到数据库失败: {e}")
                # 回退到文件系统存储
                add_file_icon(unique_filename, original_filename, int(category_id), category_name)
        else:
            # 使用文件系统存储
            add_file_icon(unique_filename, original_filename, int(category_id), category_name)
        
        flash('图标上传成功')
    else:
        flash('不支持的文件格式')
    
    return redirect(url_for('index'))

@app.route('/icons/<path:filename>')
def serve_icon(filename):
    """支持分类目录的图标服务函数"""
    try:
        # 强制使用绝对路径
        storage_dir = os.path.abspath(app.config['ICON_STORAGE_PATH'])
        
        # 修复Windows路径分隔符问题
        filename = filename.replace('\\', '/')
        
        # 构建完整文件路径，支持分类目录
        file_path = os.path.join(storage_dir, filename.replace('/', os.path.sep))
        
        # 安全检查：确保文件在存储目录内
        if not os.path.abspath(file_path).startswith(storage_dir + os.path.sep):
            return jsonify({'error': '无效的文件路径'}), 400
        
        # 检查文件是否存在且可读
        if os.path.isfile(file_path) and os.access(file_path, os.R_OK):
            # 读取文件内容并直接返回
            with open(file_path, 'rb') as f:
                content = f.read()
            
            # 创建响应对象
            response = make_response(content)
            
            # 根据文件扩展名设置MIME类型
            ext = os.path.splitext(file_path)[1].lower()
            if ext in ['.png']:
                response.headers['Content-Type'] = 'image/png'
            elif ext in ['.jpg', '.jpeg']:
                response.headers['Content-Type'] = 'image/jpeg'
            elif ext in ['.svg']:
                response.headers['Content-Type'] = 'image/svg+xml'
            elif ext in ['.gif']:
                response.headers['Content-Type'] = 'image/gif'
            else:
                response.headers['Content-Type'] = 'application/octet-stream'
            
            return response
        else:
            # 文件不存在或不可读
            return jsonify({'error': '文件不存在'}), 404
    except:
        # 捕获所有异常，返回404
        return jsonify({'error': '文件不存在'}), 404

# 文件系统存储函数
def update_file_icon_name(icon_id, new_name):
    """更新文件系统中图标的名称"""
    icons = load_json_data(ICONS_DATA_FILE, [])
    
    for i, icon in enumerate(icons):
        if icon['id'] == icon_id:
            # 获取文件扩展名
            ext = icon['filename'].rsplit('.', 1)[1].lower() if '.' in icon['filename'] else ''
            
            # 清理新名称
            sanitized_name = sanitize_path(new_name)
            new_filename = f"{sanitized_name}.{ext}" if ext else sanitized_name
            
            # 获取分类文件夹
            category_folder = icon.get('category_name', '未分类')
            old_filepath = os.path.join(app.config['ICON_STORAGE_PATH'], category_folder, icon['filename'])
            new_filepath = os.path.join(app.config['ICON_STORAGE_PATH'], category_folder, new_filename)
            
            # 重命名文件
            if os.path.exists(old_filepath):
                os.rename(old_filepath, new_filepath)
                icon['filename'] = new_filename
                save_json_data(ICONS_DATA_FILE, icons)
                return True
            return False
    return False

@app.route('/rename/<int:icon_id>', methods=['POST'])
@login_required
def rename_icon(icon_id):
    new_name = request.form.get('new_name', '').strip()
    
    if not new_name:
        return jsonify({'success': False, 'message': '新名称不能为空'})
    
    # 根据存储方式更新图标名称
    if sqlalchemy_available:
        try:
            icon = Icon.query.get(icon_id)
            if not icon:
                return jsonify({'success': False, 'message': '图标不存在'})
            
            # 获取文件扩展名
            ext = icon.filename.rsplit('.', 1)[1].lower() if '.' in icon.filename else ''
            
            # 清理新名称
            sanitized_name = sanitize_path(new_name)
            new_filename = f"{sanitized_name}.{ext}" if ext else sanitized_name
            
            # 获取分类文件夹
            category_folder = '未分类' if not icon.category else icon.category.name
            old_filepath = os.path.join(app.config['ICON_STORAGE_PATH'], category_folder, icon.filename)
            new_filepath = os.path.join(app.config['ICON_STORAGE_PATH'], category_folder, new_filename)
            
            # 重命名文件
            if os.path.exists(old_filepath):
                os.rename(old_filepath, new_filepath)
                icon.filename = new_filename
                db.session.commit()
                return jsonify({'success': True, 'new_name': new_filename})
            
            return jsonify({'success': False, 'message': '文件不存在'})
        except Exception as e:
            print(f"数据库重命名失败: {e}")
            # 尝试使用文件系统重命名
            if update_file_icon_name(icon_id, new_name):
                return jsonify({'success': True, 'message': '图标已在文件系统中重命名', 'new_name': new_name})
            return jsonify({'success': False, 'message': f'重命名失败: {str(e)}'})
    else:
        # 使用文件系统存储
        if update_file_icon_name(icon_id, new_name):
            return jsonify({'success': True, 'message': '图标重命名成功', 'new_name': new_name})
        return jsonify({'success': False, 'message': '图标不存在或重命名失败'})

@app.route('/copy-url/<int:icon_id>')
def copy_icon_url(icon_id):
    try:
        # 兼容两种存储方式获取图标
        icon = None
        if sqlalchemy_available:
            try:
                icon = Icon.query.get(icon_id)
            except Exception as e:
                print(f"从数据库获取图标失败: {e}")
                
        if not icon:
            # 从文件系统存储中获取图标
            icons = get_file_icons()
            for i in icons:
                if i.id == icon_id:
                    icon = i
                    break
        
        if not icon:
            return jsonify({'success': False, 'message': '图标不存在'})
        
        # 返回图标URL，使用url_for生成完整URL用于复制
        # 构建完整的分类+文件名路径
        if hasattr(icon, 'category_name'):
            category_folder = icon.category_name
        else:
            category_folder = '未分类' if not icon.category else icon.category.name
            
        full_url = url_for('serve_icon', filename=os.path.join(category_folder, icon.filename), _external=True)
        return jsonify({'success': True, 'url': full_url})
    except Exception as e:
        print(f"复制图标URL失败: {e}")
        return jsonify({'success': False, 'message': '服务器错误'})

@app.route('/add-category', methods=['POST'])
@login_required
def add_category():
    try:
        category_name = request.form.get('category_name', '').strip()
        
        if not category_name:
            return jsonify({'success': False, 'message': '分类名称不能为空'})
        
        # 检查分类是否已存在
        category_exists = False
        category_id = None
        
        if sqlalchemy_available:
            try:
                existing = Category.query.filter_by(name=category_name).first()
                if existing:
                    return jsonify({'success': False, 'message': '该分类已存在'})
                
                # 创建新分类
                new_category = Category(name=category_name)
                db.session.add(new_category)
                db.session.commit()
                category_id = new_category.id
            except Exception as e:
                print(f"数据库操作失败: {e}")
                # 回退到文件系统存储
                if add_file_category(category_name):
                    categories = get_file_categories()
                    for cat in categories:
                        if cat.name == category_name:
                            category_id = cat.id
                            break
                else:
                    return jsonify({'success': False, 'message': '该分类已存在或创建失败'})
        else:
            # 使用文件系统存储
            if add_file_category(category_name):
                categories = get_file_categories()
                for cat in categories:
                    if cat.name == category_name:
                        category_id = cat.id
                        break
            else:
                return jsonify({'success': False, 'message': '该分类已存在或创建失败'})
        
        # 创建分类文件夹
        create_category_folder(category_name)
        
        return jsonify({
            'success': True, 
            'id': category_id, 
            'name': category_name
        })
    except Exception as e:
        print(f"添加分类时出错: {e}")
        return jsonify({'success': False, 'message': f'分类创建失败: {str(e)}'})

@app.route('/update-category', methods=['POST'])
@login_required
def update_category():
    """更新分类信息"""
    try:
        category_id = request.form.get('category_id', type=int)
        new_category_name = request.form.get('category_name')
        
        if not category_id or not new_category_name:
            return jsonify({'success': False, 'message': '分类ID和名称不能为空'})
            
        # 不允许修改默认分类
        if category_id == 1:
            return jsonify({'success': False, 'message': '默认分类不能修改'})
        
        # 查找分类
        category = SimpleCategory.query.get(category_id)
        if not category:
            return jsonify({'success': False, 'message': '分类不存在'})
            
        # 检查新名称是否与其他分类重复
        existing_category = SimpleCategory.query.filter(
            SimpleCategory.name == new_category_name,
            SimpleCategory.id != category_id
        ).first()
        if existing_category:
            return jsonify({'success': False, 'message': '分类名称已存在'})
        
        # 更新分类名称
        category.name = new_category_name
        db.session.commit()
        
        return jsonify({'success': True, 'id': category.id, 'name': category.name})
    except Exception as e:
        db.session.rollback()
        app.logger.error(f'更新分类时出错: {e}')
        return jsonify({'success': False, 'message': f'更新分类时出错: {str(e)}'})
def update_file_icon_category(icon_id, new_category_name, new_category_id=None):
    """在文件系统存储模式下更新图标的分类"""
    icons = load_json_data(ICONS_DATA_FILE, [])
    
    for icon in icons:
        if icon['id'] == icon_id:
            # 获取旧分类名称
            old_category_name = icon.get('category_name', '未分类')
            
            # 构建文件路径
            old_file_path = os.path.join(app.config['ICON_STORAGE_PATH'], old_category_name, icon['filename'])
            new_file_path = os.path.join(app.config['ICON_STORAGE_PATH'], new_category_name, icon['filename'])
            
            # 如果文件存在，移动它
            if os.path.exists(old_file_path):
                os.rename(old_file_path, new_file_path)
            
            # 更新图标信息
            icon['category_name'] = new_category_name
            if new_category_id is not None:
                icon['category_id'] = new_category_id
            else:
                # 如果没有提供分类ID，尝试根据名称查找
                categories = get_file_categories()
                for cat in categories:
                    if cat.name == new_category_name:
                        icon['category_id'] = cat.id
                        break
            
            # 保存更新后的数据
            save_json_data(ICONS_DATA_FILE, icons)
            return True
    return False

def delete_file_category(category_id):
    """从文件系统删除分类"""
    categories = load_json_data(CATEGORIES_DATA_FILE, [])
    
    # 查找要删除的分类
    category_to_delete = None
    category_index = -1
    
    for i, cat in enumerate(categories):
        if cat['id'] == category_id:
            category_to_delete = cat
            category_index = i
            break
    
    if not category_to_delete:
        return False
    
    # 不能删除默认分类
    if category_id == 1:
        return False
    
    # 获取分类名称
    category_name = category_to_delete['name']
    
    # 获取该分类下的所有图标
    icons = load_json_data(ICONS_DATA_FILE, [])
    has_icons = False
    
    for icon in icons:
        if icon.get('category_id') == category_id or icon.get('category_name') == category_name:
            # 将图标移到默认分类
            icon['category_id'] = 1
            icon['category_name'] = '未分类'
            has_icons = True
    
    # 保存更新后的图标数据
    if has_icons:
        save_json_data(ICONS_DATA_FILE, icons)
    
    # 从分类列表中删除
    del categories[category_index]
    save_json_data(CATEGORIES_DATA_FILE, categories)
    
    # 删除分类文件夹（如果存在）
    category_path = os.path.join(app.config['ICON_STORAGE_PATH'], category_name)
    if os.path.exists(category_path):
        try:
            # 检查文件夹是否为空
            if not os.listdir(category_path):
                os.rmdir(category_path)
        except Exception as e:
            print(f"删除分类文件夹失败: {e}")
    
    return True

@app.route('/delete-category/<int:category_id>', methods=['POST'])
def delete_category(category_id):
    try:
        # 不能删除默认分类
        if category_id == 1:
            return jsonify({'success': False, 'message': '默认分类不能删除'})
        
        # 定义一个变量保存分类名称
        category_name = None
        
        # 根据存储方式执行删除操作
        if sqlalchemy_available:
            try:
                # 查找分类
                category = Category.query.get(category_id)
                if not category:
                    return jsonify({'success': False, 'message': '分类不存在'})
                
                category_name = category.name
                
                # 检查分类下是否有图标
                if category.icons:
                    # 获取默认分类
                    default_category = Category.query.filter_by(name='未分类').first()
                    if not default_category:
                        default_category = Category(name='未分类')
                        db.session.add(default_category)
                    
                    # 将所有图标移到默认分类
                    for icon in category.icons:
                        # 获取旧文件路径
                        old_file_path = os.path.join(app.config['ICON_STORAGE_PATH'], category_name, icon.filename)
                        new_file_path = os.path.join(app.config['ICON_STORAGE_PATH'], '未分类', icon.filename)
                        
                        # 移动文件
                        if os.path.exists(old_file_path):
                            # 检查新路径是否已存在文件，需要处理文件冲突
                            if os.path.exists(new_file_path):
                                base, ext = os.path.splitext(icon.filename)
                                timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
                                new_filename = f"{base}_{timestamp}{ext}"
                                new_file_path = os.path.join(app.config['ICON_STORAGE_PATH'], '未分类', new_filename)
                                os.rename(old_file_path, new_file_path)
                                icon.filename = new_filename
                            else:
                                os.rename(old_file_path, new_file_path)
                        
                        # 更新图标分类
                        icon.category_id = default_category.id
                
                # 删除分类
                db.session.delete(category)
                db.session.commit()
                
                # 删除分类文件夹
                if category_name:
                    category_path = os.path.join(app.config['ICON_STORAGE_PATH'], category_name)
                    if os.path.exists(category_path):
                        try:
                            os.rmdir(category_path)
                        except Exception as e:
                            print(f"删除分类文件夹失败: {e}")
                            # 文件夹删除失败不影响分类删除
            except Exception as e:
                db.session.rollback()
                print(f"从数据库删除分类失败: {e}")
                # 尝试从文件系统删除
                if not delete_file_category(category_id):
                    return jsonify({'success': False, 'message': '删除分类失败'})
        else:
            # 使用文件系统存储
            if not delete_file_category(category_id):
                return jsonify({'success': False, 'message': '分类不存在或删除失败'})
        
        return jsonify({'success': True, 'message': '分类已成功删除'})
    except Exception as e:
        print(f"删除分类时出错: {e}")
        return jsonify({'success': False, 'message': f'删除失败: {str(e)}'})

@app.route('/update-category/<int:icon_id>', methods=['POST'])
@login_required
def update_icon_category(icon_id):
    try:
        # 获取图标信息
        icon = None
        old_category_name = '未分类'
        filename = None
        
        # 根据存储方式获取图标信息
        if sqlalchemy_available:
            try:
                icon = Icon.query.get(icon_id)
                if not icon:
                    return jsonify({'success': False, 'message': '图标不存在'})
                
                # 获取旧分类信息
                old_category = icon.category
                old_category_name = old_category.name if old_category else '未分类'
                filename = icon.filename
            except Exception as e:
                print(f"数据库查询失败: {e}")
                # 尝试从文件系统获取
                icons = get_file_icons()
                for i in icons:
                    if i.id == icon_id:
                        old_category_name = i.category_name
                        filename = i.filename
                        break
        else:
            # 使用文件系统存储
            icons = get_file_icons()
            for i in icons:
                if i.id == icon_id:
                    old_category_name = i.category_name
                    filename = i.filename
                    break
        
        if not filename:
            return jsonify({'success': False, 'message': '图标不存在'})
        
        # 获取新分类信息
        category_id = request.form.get('category_id')
        new_category_name = '未分类'
        new_category_id = 1
        
        if category_id:
            if sqlalchemy_available:
                try:
                    new_category = Category.query.get(category_id)
                    if new_category:
                        new_category_name = new_category.name
                        new_category_id = new_category.id
                except Exception as e:
                    print(f"获取新分类失败: {e}")
                    # 从文件系统获取
                    categories = get_file_categories()
                    for cat in categories:
                        if str(cat.id) == category_id:
                            new_category_name = cat.name
                            new_category_id = cat.id
                            break
            else:
                categories = get_file_categories()
                for cat in categories:
                    if str(cat.id) == category_id:
                        new_category_name = cat.name
                        new_category_id = cat.id
                        break
        else:
            # 如果没有选择分类，使用默认分类
            if sqlalchemy_available:
                try:
                    default_category = Category.query.filter_by(name='未分类').first()
                    if default_category:
                        new_category_name = default_category.name
                        new_category_id = default_category.id
                except:
                    pass
        
        # 如果分类未改变，不做处理
        if old_category_name == new_category_name:
            return jsonify({'success': True})
        
        # 获取文件路径
        old_file_path = os.path.join(app.config['ICON_STORAGE_PATH'], old_category_name, filename)
        new_file_path = os.path.join(app.config['ICON_STORAGE_PATH'], new_category_name, filename)
        
        # 确保新分类目录存在
        create_category_folder(new_category_name)
        
        # 移动文件
        if os.path.exists(old_file_path):
            # 检查是否需要重命名（避免文件冲突）
            if os.path.exists(new_file_path):
                # 生成新文件名
                base, ext = os.path.splitext(filename)
                timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
                new_filename = f"{base}_{timestamp}{ext}"
                new_file_path = os.path.join(app.config['ICON_STORAGE_PATH'], new_category_name, new_filename)
                
                # 更新文件名
                os.rename(old_file_path, new_file_path)
                
                # 更新存储中的文件名
                if sqlalchemy_available and icon:
                    try:
                        icon.filename = new_filename
                    except:
                        pass
                else:
                    # 更新文件系统中的文件名
                    update_file_icon_name(icon_id, os.path.splitext(new_filename)[0])
            else:
                os.rename(old_file_path, new_file_path)
        
        # 更新存储
        if sqlalchemy_available:
            try:
                if icon:
                    icon.category_id = new_category_id
                    db.session.commit()
            except Exception as e:
                print(f"更新数据库失败: {e}")
                # 更新文件系统
                update_file_icon_category(icon_id, new_category_name, new_category_id)
        else:
            # 更新文件系统
            update_file_icon_category(icon_id, new_category_name, new_category_id)
        
        return jsonify({'success': True, 'category_name': new_category_name})
    except Exception as e:
        print(f"更新分类时出错: {e}")
        return jsonify({'success': False, 'message': f'分类更新失败: {str(e)}'})

@app.route('/delete/<int:icon_id>', methods=['POST'])
@login_required
def delete_icon(icon_id):
    try:
        icon = None
        category_name = '未分类'
        filename = None
        
        # 根据存储方式获取图标信息
        if sqlalchemy_available:
            try:
                icon = Icon.query.get(icon_id)
                if not icon:
                    return jsonify({'success': False, 'message': '图标不存在'})
                
                # 获取分类名称
                category_name = icon.category.name if icon.category else '未分类'
                filename = icon.filename
                
                # 删除数据库记录
                db.session.delete(icon)
                db.session.commit()
            except Exception as e:
                print(f"从数据库删除失败: {e}")
                # 尝试从文件系统删除
                delete_file_icon(icon_id)
                return jsonify({'success': True, 'message': '图标已从文件系统中删除'})
        else:
            # 使用文件系统存储
            # 查找图标信息
            icons = get_file_icons()
            for i in icons:
                if i.id == icon_id:
                    icon = i
                    category_name = i.category_name
                    filename = i.filename
                    break
            
            if not icon:
                return jsonify({'success': False, 'message': '图标不存在'})
            
            # 删除文件系统中的记录
            if not delete_file_icon(icon_id):
                return jsonify({'success': False, 'message': '删除失败: 图标记录不存在'})
        
        # 构建文件路径并删除文件
        if filename:
            file_path = os.path.join(app.config['ICON_STORAGE_PATH'], category_name, filename)
            
            # 删除文件
            if os.path.exists(file_path):
                try:
                    os.remove(file_path)
                except Exception as e:
                    print(f"删除文件失败: {e}")
                    return jsonify({'success': False, 'message': '图标数据已删除，但文件删除失败'})
        
        return jsonify({'success': True})
    except Exception as e:
        print(f"删除图标时出错: {e}")
        return jsonify({'success': False, 'message': f'删除失败: {str(e)}'})

@app.route('/batch-upload', methods=['POST'])
@login_required
def batch_upload_icons():
    if 'icons' not in request.files:
        return jsonify({'success': False, 'message': '没有文件被上传'})
    
    files = request.files.getlist('icons')
    if not files:
        return jsonify({'success': False, 'message': '没有选择文件'})
    
    # 获取分类信息
    category_id = request.form.get('category')
    category_name = '未分类'
    
    # 根据存储方式获取分类
    if sqlalchemy_available:
        try:
            category = Category.query.get(category_id) if category_id else None
            if not category:
                category = Category.query.filter_by(name='未分类').first()
                category_id = category.id if category else 1
            category_name = category.name if category else '未分类'
        except Exception as e:
            print(f"获取分类失败: {e}")
            category_id = 1
            category_name = '未分类'
    else:
        # 使用文件系统存储的分类
        categories = get_file_categories()
        if category_id:
            for cat in categories:
                if str(cat.id) == category_id:
                    category_name = cat.name
                    category_id = cat.id
                    break
        else:
            category_id = 1
            category_name = '未分类'
    
    # 创建分类文件夹（如果不存在）
    category_path = create_category_folder(category_name)
    
    uploaded_count = 0
    
    for file in files:
        if file and allowed_file(file.filename):
            try:
                filename = generate_secure_filename(file.filename)
                filepath = os.path.join(category_path, filename)
                file.save(filepath)
                
                # 根据存储方式创建图标记录
                if sqlalchemy_available:
                    try:
                        new_icon = Icon(
                            filename=filename,
                            original_filename=file.filename,
                            category_id=category_id
                        )
                        db.session.add(new_icon)
                    except Exception as e:
                        print(f"保存到数据库失败: {e}")
                        # 回退到文件系统存储
                        add_file_icon(filename, file.filename, category_id, category_name)
                else:
                    # 使用文件系统存储
                    add_file_icon(filename, file.filename, category_id, category_name)
                
                uploaded_count += 1
            except Exception as e:
                print(f"处理文件失败 {file.filename}: {e}")
    
    # 提交数据库更改
    if sqlalchemy_available:
        try:
            db.session.commit()
        except Exception as e:
            print(f"数据库提交失败: {e}")
    
    return jsonify({
        'success': True, 
        'message': f'成功上传 {uploaded_count} 个图标',
        'uploaded_count': uploaded_count
    })

if __name__ == '__main__':
    # 支持直接运行Python文件
    app.run(host='0.0.0.0', port=5000, debug=True)
