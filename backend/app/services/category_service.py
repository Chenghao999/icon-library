# 分类服务层
import os
import json
from datetime import datetime
from ..config import default_config
from ..models.category import Category
from ..models.base import SimpleCategory
from ..utils.file_utils import FileUtils

class CategoryService:
    """分类服务类，提供分类的业务逻辑"""
    
    def __init__(self, db=None, storage_type='database'):
        """初始化
        
        Args:
            db: SQLAlchemy数据库实例
            storage_type: 存储类型，'database'或'file_system'
        """
        self.config = default_config()
        self.db = db
        self.storage_type = storage_type
        
        # 初始化默认分类
        self._ensure_default_category()
    
    def _ensure_default_category(self):
        """确保默认分类存在"""
        default_categories = self.get_all_categories()
        has_default = any(cat['name'] == '未分类' for cat in default_categories)
        
        if not has_default:
            self.create_category('未分类')
    
    def get_all_categories(self):
        """获取所有分类
        
        Returns:
            分类列表
        """
        if self.storage_type == 'database' and self.db:
            # 数据库存储
            return [category.to_dict() for category in Category.query.all()]
        else:
            # 文件系统存储
            categories = FileUtils.load_json_file(self.config.CATEGORIES_DATA_FILE, [])
            # 确保有默认分类
            if not any(cat['name'] == '未分类' for cat in categories):
                default_category = SimpleCategory(1, '未分类')
                categories = [default_category.to_dict()] + categories
                FileUtils.save_json_file(self.config.CATEGORIES_DATA_FILE, categories)
            return categories
    
    def get_category_by_id(self, category_id):
        """根据ID获取分类
        
        Args:
            category_id: 分类ID
            
        Returns:
            分类信息，如果不存在返回None
        """
        if self.storage_type == 'database' and self.db:
            # 数据库存储
            category = Category.query.get(category_id)
            return category.to_dict() if category else None
        else:
            # 文件系统存储
            categories = FileUtils.load_json_file(self.config.CATEGORIES_DATA_FILE, [])
            return next((category for category in categories if category.get('id') == category_id), None)
    
    def create_category(self, name):
        """创建新分类
        
        Args:
            name: 分类名称
            
        Returns:
            创建的分类信息，如果分类名已存在返回None
        """
        # 检查分类名是否已存在
        if self.category_name_exists(name):
            return None
        
        if self.storage_type == 'database' and self.db:
            # 数据库存储
            category = Category(name=name)
            self.db.session.add(category)
            self.db.session.commit()
            
            # 创建分类目录
            category_dir = os.path.join(self.config.ICON_STORAGE_PATH, name)
            FileUtils.ensure_directory_exists(category_dir)
            
            return category.to_dict()
        else:
            # 文件系统存储
            categories = FileUtils.load_json_file(self.config.CATEGORIES_DATA_FILE, [])
            
            # 获取下一个ID
            next_id = max([cat.get('id', 0) for cat in categories], default=0) + 1
            now = datetime.now().isoformat()
            
            # 创建新分类
            new_category = SimpleCategory(
                id=next_id,
                name=name,
                created_at=now,
                updated_at=now
            )
            
            # 保存到文件
            categories.append(new_category.to_dict())
            FileUtils.save_json_file(self.config.CATEGORIES_DATA_FILE, categories)
            
            # 创建分类目录
            category_dir = os.path.join(self.config.ICON_STORAGE_PATH, name)
            FileUtils.ensure_directory_exists(category_dir)
            
            return new_category.to_dict()
    
    def update_category(self, category_id, new_name):
        """更新分类名称
        
        Args:
            category_id: 分类ID
            new_name: 新分类名称
            
        Returns:
            更新后的分类信息，如果分类不存在或名称已存在返回None
        """
        # 检查是否为默认分类
        current_category = self.get_category_by_id(category_id)
        if not current_category:
            return None
        
        if current_category['name'] == '未分类':
            return None  # 不能修改默认分类
        
        # 检查新名称是否已存在
        if new_name != current_category['name'] and self.category_name_exists(new_name):
            return None
        
        # 更新目录名
        old_dir = os.path.join(self.config.ICON_STORAGE_PATH, current_category['name'])
        new_dir = os.path.join(self.config.ICON_STORAGE_PATH, new_name)
        
        if os.path.exists(old_dir) and old_dir != new_dir:
            if not os.path.exists(new_dir):
                os.rename(old_dir, new_dir)
        
        if self.storage_type == 'database' and self.db:
            # 数据库存储
            category = Category.query.get(category_id)
            if not category:
                return None
            
            category.name = new_name
            self.db.session.commit()
            
            return category.to_dict()
        else:
            # 文件系统存储
            categories = FileUtils.load_json_file(self.config.CATEGORIES_DATA_FILE, [])
            category_index = next((i for i, cat in enumerate(categories) if cat['id'] == category_id), None)
            
            if category_index is None:
                return None
            
            # 更新分类信息
            category = categories[category_index]
            category['name'] = new_name
            category['updated_at'] = datetime.now().isoformat()
            
            # 保存更新
            categories[category_index] = category
            FileUtils.save_json_file(self.config.CATEGORIES_DATA_FILE, categories)
            
            return category
    
    def delete_category(self, category_id):
        """删除分类
        
        Args:
            category_id: 分类ID
            
        Returns:
            是否删除成功
        """
        # 检查是否为默认分类
        category = self.get_category_by_id(category_id)
        if not category or category['name'] == '未分类':
            return False  # 不能删除默认分类
        
        # 删除分类目录（注意：实际应用中可能需要更复杂的逻辑）
        category_dir = os.path.join(self.config.ICON_STORAGE_PATH, category['name'])
        if os.path.exists(category_dir):
            # 这里只是示例，实际应用中可能需要更安全的删除逻辑
            pass
        
        if self.storage_type == 'database' and self.db:
            # 数据库存储
            category_obj = Category.query.get(category_id)
            if not category_obj:
                return False
            
            # 获取默认分类
            default_category = Category.query.filter_by(name='未分类').first()
            
            # 更新该分类下的所有图标到默认分类
            for icon in category_obj.icons:
                icon.category_id = default_category.id
            
            self.db.session.delete(category_obj)
            self.db.session.commit()
            
            return True
        else:
            # 文件系统存储
            categories = FileUtils.load_json_file(self.config.CATEGORIES_DATA_FILE, [])
            categories = [cat for cat in categories if cat['id'] != category_id]
            FileUtils.save_json_file(self.config.CATEGORIES_DATA_FILE, categories)
            
            # 更新图标分类
            icons = FileUtils.load_json_file(self.config.ICONS_DATA_FILE, [])
            default_category = next((c for c in categories if c['name'] == '未分类'), None)
            
            for icon in icons:
                if icon['category_id'] == category_id and default_category:
                    icon['category_id'] = default_category['id']
                    icon['category_name'] = '未分类'
            
            FileUtils.save_json_file(self.config.ICONS_DATA_FILE, icons)
            
            return True
    
    def category_name_exists(self, name):
        """检查分类名称是否已存在
        
        Args:
            name: 分类名称
            
        Returns:
            布尔值，表示分类名是否已存在
        """
        if self.storage_type == 'database' and self.db:
            # 数据库存储
            return Category.query.filter_by(name=name).first() is not None
        else:
            # 文件系统存储
            categories = FileUtils.load_json_file(self.config.CATEGORIES_DATA_FILE, [])
            return any(category['name'] == name for category in categories)
