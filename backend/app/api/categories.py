# 分类相关的API路由
import os
import json
from flask import request, jsonify, send_from_directory
from .. import app_config, db, SQLALCHEMY_AVAILABLE
from ..models.category import Category
from ..models.base import SimpleCategory
from . import api_bp
from .auth import login_required

# 初始化文件系统数据存储
def init_file_storage():
    """初始化文件系统存储"""
    # 确保数据目录存在
    if not os.path.exists(app_config.DATA_DIR):
        os.makedirs(app_config.DATA_DIR)
    
    # 初始化分类数据文件
    if not os.path.exists(app_config.CATEGORIES_DATA_FILE):
        with open(app_config.CATEGORIES_DATA_FILE, 'w', encoding='utf-8') as f:
            default_category = SimpleCategory(1, '未分类')
            json.dump([default_category.to_dict()], f, ensure_ascii=False, indent=2)

# 文件系统存储的分类操作
def get_categories_from_file():
    """从文件系统获取分类列表"""
    init_file_storage()
    try:
        with open(app_config.CATEGORIES_DATA_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    except (json.JSONDecodeError, FileNotFoundError):
        return []

def save_categories_to_file(categories):
    """保存分类列表到文件系统"""
    init_file_storage()
    with open(app_config.CATEGORIES_DATA_FILE, 'w', encoding='utf-8') as f:
        json.dump(categories, f, ensure_ascii=False, indent=2)

# 分类API路由
@api_bp.route('/categories', methods=['GET'])
def get_categories():
    """获取所有分类"""
    if SQLALCHEMY_AVAILABLE:
        # 使用数据库存储
        categories = Category.query.all()
        return jsonify([category.to_dict() for category in categories]), 200
    else:
        # 使用文件系统存储
        categories = get_categories_from_file()
        return jsonify(categories), 200

@api_bp.route('/categories/<int:category_id>', methods=['GET'])
def get_category(category_id):
    """获取单个分类"""
    if SQLALCHEMY_AVAILABLE:
        # 使用数据库存储
        category = Category.query.get_or_404(category_id)
        return jsonify(category.to_dict()), 200
    else:
        # 使用文件系统存储
        categories = get_categories_from_file()
        category = next((c for c in categories if c['id'] == category_id), None)
        if category:
            return jsonify(category), 200
        else:
            return jsonify({"error": "分类不存在"}), 404

@api_bp.route('/categories', methods=['POST'])
@login_required
def create_category():
    """创建新分类"""
    data = request.get_json() or {}
    
    name = data.get('name')
    if not name or name.strip() == '':
        return jsonify({"error": "分类名称不能为空"}), 400
    
    if SQLALCHEMY_AVAILABLE:
        # 检查分类名是否已存在
        existing = Category.query.filter_by(name=name).first()
        if existing:
            return jsonify({"error": "分类名称已存在"}), 400
        
        # 创建新分类
        category = Category(name=name)
        db.session.add(category)
        db.session.commit()
        
        # 确保分类目录存在
        category_dir = os.path.join(app_config.ICON_STORAGE_PATH, name)
        if not os.path.exists(category_dir):
            os.makedirs(category_dir)
        
        return jsonify(category.to_dict()), 201
    else:
        # 文件系统存储
        categories = get_categories_from_file()
        
        # 检查分类名是否已存在
        if any(c['name'] == name for c in categories):
            return jsonify({"error": "分类名称已存在"}), 400
        
        # 生成新ID
        new_id = max([c['id'] for c in categories], default=0) + 1
        
        # 创建新分类
        new_category = {
            "id": new_id,
            "name": name
        }
        categories.append(new_category)
        save_categories_to_file(categories)
        
        # 确保分类目录存在
        category_dir = os.path.join(app_config.ICON_STORAGE_PATH, name)
        if not os.path.exists(category_dir):
            os.makedirs(category_dir)
        
        return jsonify(new_category), 201

@api_bp.route('/categories/<int:category_id>', methods=['PUT'])
@login_required
def update_category(category_id):
    """更新分类信息"""
    data = request.get_json() or {}
    new_name = data.get('name')
    
    if not new_name or new_name.strip() == '':
        return jsonify({"error": "分类名称不能为空"}), 400
    
    if SQLALCHEMY_AVAILABLE:
        # 获取要更新的分类
        category = Category.query.get_or_404(category_id)
        
        # 如果分类名称已更改，检查新名称是否已存在
        if category.name != new_name:
            existing = Category.query.filter_by(name=new_name).first()
            if existing:
                return jsonify({"error": "分类名称已存在"}), 400
            
            # 更新文件系统中的目录名
            old_dir = os.path.join(app_config.ICON_STORAGE_PATH, category.name)
            new_dir = os.path.join(app_config.ICON_STORAGE_PATH, new_name)
            if os.path.exists(old_dir) and old_dir != new_dir:
                if not os.path.exists(new_dir):
                    os.rename(old_dir, new_dir)
        
        # 更新分类名称
        category.name = new_name
        db.session.commit()
        
        return jsonify(category.to_dict()), 200
    else:
        # 文件系统存储
        categories = get_categories_from_file()
        category = next((c for c in categories if c['id'] == category_id), None)
        
        if not category:
            return jsonify({"error": "分类不存在"}), 404
        
        # 如果分类名称已更改，检查新名称是否已存在
        if category['name'] != new_name:
            if any(c['name'] == new_name and c['id'] != category_id for c in categories):
                return jsonify({"error": "分类名称已存在"}), 400
            
            # 更新文件系统中的目录名
            old_dir = os.path.join(app_config.ICON_STORAGE_PATH, category['name'])
            new_dir = os.path.join(app_config.ICON_STORAGE_PATH, new_name)
            if os.path.exists(old_dir) and old_dir != new_dir:
                if not os.path.exists(new_dir):
                    os.rename(old_dir, new_dir)
        
        # 更新分类名称
        category['name'] = new_name
        save_categories_to_file(categories)
        
        return jsonify(category), 200

@api_bp.route('/categories/<int:category_id>', methods=['DELETE'])
@login_required
def delete_category(category_id):
    """删除分类"""
    # 不允许删除默认的"未分类"
    if SQLALCHEMY_AVAILABLE:
        category = Category.query.get_or_404(category_id)
        if category.name == '未分类':
            return jsonify({"error": "不能删除默认的未分类"}), 400
        
        # 更新该分类下的所有图标到"未分类"
        default_category = Category.query.filter_by(name='未分类').first()
        for icon in category.icons:
            icon.category_id = default_category.id
        
        # 删除分类目录
        category_dir = os.path.join(app_config.ICON_STORAGE_PATH, category.name)
        if os.path.exists(category_dir):
            # 注意：这里只是删除目录，实际应用中可能需要更复杂的逻辑
            pass
        
        # 删除分类
        db.session.delete(category)
        db.session.commit()
        
        return jsonify({"message": "分类已删除"}), 200
    else:
        # 文件系统存储
        categories = get_categories_from_file()
        category = next((c for c in categories if c['id'] == category_id), None)
        
        if not category:
            return jsonify({"error": "分类不存在"}), 404
        
        if category['name'] == '未分类':
            return jsonify({"error": "不能删除默认的未分类"}), 400
        
        # 删除分类目录
        category_dir = os.path.join(app_config.ICON_STORAGE_PATH, category['name'])
        if os.path.exists(category_dir):
            # 注意：这里只是删除目录，实际应用中可能需要更复杂的逻辑
            pass
        
        # 删除分类
        categories = [c for c in categories if c['id'] != category_id]
        save_categories_to_file(categories)
        
        return jsonify({"message": "分类已删除"}), 200
