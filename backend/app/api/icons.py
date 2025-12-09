# 图标相关的API路由
import os
import json
import shutil
import re
from datetime import datetime
from flask import request, jsonify, send_from_directory, current_app
from werkzeug.utils import secure_filename
from .. import app_config, db, SQLALCHEMY_AVAILABLE
from ..models.icon import Icon
from ..models.category import Category
from ..models.base import SimpleIcon
from . import api_bp
from .auth import login_required

# 工具函数
def allowed_file(filename):
    """检查文件扩展名是否允许"""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in app_config.ALLOWED_EXTENSIONS

def sanitize_filename(filename):
    """生成安全的文件名"""
    filename = secure_filename(filename)
    # 移除特殊字符
    filename = re.sub(r'[^a-zA-Z0-9._-]', '_', filename)
    # 确保文件名长度合理
    name, ext = os.path.splitext(filename)
    if len(name) > 50:
        name = name[:50] + '_'
    return name + ext

# 初始化文件系统数据存储
def init_file_storage():
    """初始化文件系统存储"""
    # 确保数据目录存在
    if not os.path.exists(app_config.DATA_DIR):
        os.makedirs(app_config.DATA_DIR)
    
    # 初始化图标元数据文件
    if not os.path.exists(app_config.ICONS_DATA_FILE):
        with open(app_config.ICONS_DATA_FILE, 'w', encoding='utf-8') as f:
            json.dump([], f, ensure_ascii=False, indent=2)

# 文件系统存储的图标操作
def get_icons_from_file(category_id=None):
    """从文件系统获取图标列表"""
    init_file_storage()
    try:
        with open(app_config.ICONS_DATA_FILE, 'r', encoding='utf-8') as f:
            icons = json.load(f)
            if category_id is not None:
                icons = [icon for icon in icons if icon.get('category_id') == category_id]
            return icons
    except (json.JSONDecodeError, FileNotFoundError):
        return []

def get_icon_from_file(icon_id):
    """从文件系统获取单个图标"""
    icons = get_icons_from_file()
    return next((icon for icon in icons if icon.get('id') == icon_id), None)

def save_icons_to_file(icons):
    """保存图标列表到文件系统"""
    init_file_storage()
    with open(app_config.ICONS_DATA_FILE, 'w', encoding='utf-8') as f:
        json.dump(icons, f, ensure_ascii=False, indent=2)

def get_next_icon_id():
    """获取下一个图标ID"""
    icons = get_icons_from_file()
    if not icons:
        return 1
    return max([icon.get('id', 0) for icon in icons]) + 1

# 图标API路由
@api_bp.route('/icons', methods=['GET'])
def get_icons():
    """获取图标列表，支持按分类筛选"""
    category_id = request.args.get('category_id', type=int)
    
    if SQLALCHEMY_AVAILABLE:
        # 使用数据库存储
        query = Icon.query
        if category_id is not None:
            query = query.filter_by(category_id=category_id)
        
        icons = query.all()
        return jsonify([icon.to_dict() for icon in icons]), 200
    else:
        # 使用文件系统存储
        icons = get_icons_from_file(category_id)
        return jsonify(icons), 200

@api_bp.route('/icons/<int:icon_id>', methods=['GET'])
def get_icon(icon_id):
    """获取单个图标"""
    if SQLALCHEMY_AVAILABLE:
        # 使用数据库存储
        icon = Icon.query.get_or_404(icon_id)
        return jsonify(icon.to_dict()), 200
    else:
        # 使用文件系统存储
        icon = get_icon_from_file(icon_id)
        if icon:
            return jsonify(icon), 200
        else:
            return jsonify({"error": "图标不存在"}), 404

@api_bp.route('/icons', methods=['POST'])
@login_required
def upload_icon():
    """上传新图标"""
    # 检查是否有文件部分
    if 'file' not in request.files:
        return jsonify({"error": "没有文件部分"}), 400
    
    file = request.files['file']
    
    # 如果用户没有选择文件
    if file.filename == '':
        return jsonify({"error": "没有选择文件"}), 400
    
    # 检查文件扩展名
    if not allowed_file(file.filename):
        return jsonify({"error": "不支持的文件类型"}), 400
    
    # 获取其他表单数据
    category_id = request.form.get('category_id', 1, type=int)  # 默认使用ID为1的分类（未分类）
    tags = request.form.get('tags', '').split(',') if request.form.get('tags') else []
    description = request.form.get('description', '')
    
    # 生成安全的文件名
    filename = sanitize_filename(file.filename)
    
    # 确定存储路径
    if SQLALCHEMY_AVAILABLE:
        # 使用数据库存储
        category = Category.query.get_or_404(category_id)
        category_name = category.name
    else:
        # 使用文件系统存储
        from .categories import get_categories_from_file
        categories = get_categories_from_file()
        category = next((c for c in categories if c['id'] == category_id), None)
        if not category:
            category_name = '未分类'
            category_id = 1
        else:
            category_name = category['name']
    
    # 确保分类目录存在
    category_dir = os.path.join(app_config.ICON_STORAGE_PATH, category_name)
    if not os.path.exists(category_dir):
        os.makedirs(category_dir)
    
    # 保存文件
    file_path = os.path.join(category_dir, filename)
    file.save(file_path)
    
    # 保存图标信息
    if SQLALCHEMY_AVAILABLE:
        # 使用数据库存储
        icon = Icon(
            filename=filename,
            path=os.path.join(category_name, filename),  # 存储相对路径
            category_id=category_id,
            description=description
        )
        icon.tags = tags
        db.session.add(icon)
        db.session.commit()
        
        return jsonify(icon.to_dict()), 201
    else:
        # 使用文件系统存储
        icon_id = get_next_icon_id()
        now = datetime.now().isoformat()
        
        new_icon = {
            'id': icon_id,
            'filename': filename,
            'path': os.path.join(category_name, filename),  # 存储相对路径
            'category_id': category_id,
            'category_name': category_name,
            'tags': tags,
            'description': description,
            'created_at': now,
            'updated_at': now
        }
        
        icons = get_icons_from_file()
        icons.append(new_icon)
        save_icons_to_file(icons)
        
        return jsonify(new_icon), 201

@api_bp.route('/icons/<int:icon_id>', methods=['PUT'])
@login_required
def update_icon(icon_id):
    """更新图标信息"""
    data = request.get_json() or {}
    
    if SQLALCHEMY_AVAILABLE:
        # 使用数据库存储
        icon = Icon.query.get_or_404(icon_id)
        
        # 更新图标信息
        if 'category_id' in data:
            icon.category_id = data['category_id']
        
        if 'tags' in data:
            icon.tags = data['tags']
        
        if 'description' in data:
            icon.description = data['description']
        
        db.session.commit()
        
        return jsonify(icon.to_dict()), 200
    else:
        # 使用文件系统存储
        icons = get_icons_from_file()
        icon_index = next((i for i, icon in enumerate(icons) if icon['id'] == icon_id), None)
        
        if icon_index is None:
            return jsonify({"error": "图标不存在"}), 404
        
        # 更新图标信息
        icon = icons[icon_index]
        
        if 'category_id' in data:
            # 如果分类改变，需要移动文件
            from .categories import get_categories_from_file
            categories = get_categories_from_file()
            
            # 获取新分类信息
            new_category = next((c for c in categories if c['id'] == data['category_id']), None)
            if new_category:
                old_path = os.path.join(app_config.ICON_STORAGE_PATH, icon['path'])
                new_rel_path = os.path.join(new_category['name'], icon['filename'])
                new_path = os.path.join(app_config.ICON_STORAGE_PATH, new_rel_path)
                
                # 移动文件
                if os.path.exists(old_path) and old_path != new_path:
                    # 确保新目录存在
                    os.makedirs(os.path.dirname(new_path), exist_ok=True)
                    shutil.move(old_path, new_path)
                    
                # 更新图标信息
                icon['category_id'] = data['category_id']
                icon['category_name'] = new_category['name']
                icon['path'] = new_rel_path
        
        if 'tags' in data:
            icon['tags'] = data['tags']
        
        if 'description' in data:
            icon['description'] = data['description']
        
        icon['updated_at'] = datetime.now().isoformat()
        icons[icon_index] = icon
        save_icons_to_file(icons)
        
        return jsonify(icon), 200

@api_bp.route('/icons/<int:icon_id>', methods=['DELETE'])
@login_required
def delete_icon(icon_id):
    """删除图标"""
    if SQLALCHEMY_AVAILABLE:
        # 使用数据库存储
        icon = Icon.query.get_or_404(icon_id)
        
        # 删除文件
        file_path = os.path.join(app_config.ICON_STORAGE_PATH, icon.path)
        if os.path.exists(file_path):
            os.remove(file_path)
        
        # 删除数据库记录
        db.session.delete(icon)
        db.session.commit()
        
        return jsonify({"message": "图标已删除"}), 200
    else:
        # 使用文件系统存储
        icons = get_icons_from_file()
        icon_index = next((i for i, icon in enumerate(icons) if icon['id'] == icon_id), None)
        
        if icon_index is None:
            return jsonify({"error": "图标不存在"}), 404
        
        # 删除文件
        icon = icons[icon_index]
        file_path = os.path.join(app_config.ICON_STORAGE_PATH, icon['path'])
        if os.path.exists(file_path):
            os.remove(file_path)
        
        # 删除图标记录
        icons.pop(icon_index)
        save_icons_to_file(icons)
        
        return jsonify({"message": "图标已删除"}), 200

@api_bp.route('/icons/<int:icon_id>/file', methods=['GET'])
def serve_icon_file(icon_id):
    """提供图标文件下载"""
    if SQLALCHEMY_AVAILABLE:
        # 使用数据库存储
        icon = Icon.query.get_or_404(icon_id)
        icon_path = icon.path
    else:
        # 使用文件系统存储
        icon = get_icon_from_file(icon_id)
        if not icon:
            return jsonify({"error": "图标不存在"}), 404
        icon_path = icon['path']
    
    # 获取文件的完整路径
    full_path = os.path.join(app_config.ICON_STORAGE_PATH, icon_path)
    
    # 检查文件是否存在
    if not os.path.exists(full_path):
        return jsonify({"error": "图标文件不存在"}), 404
    
    # 提供文件下载
    directory = os.path.dirname(full_path)
    filename = os.path.basename(full_path)
    
    return send_from_directory(directory, filename, as_attachment=False)
