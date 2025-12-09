# 图标服务层
import os
import json
from datetime import datetime
from ..config import default_config
from ..models.icon import Icon
from ..models.category import Category
from ..models.base import SimpleIcon
from ..utils.file_utils import FileUtils

class IconService:
    """图标服务类，提供图标的业务逻辑"""
    
    def __init__(self, db=None, storage_type='database'):
        """初始化
        
        Args:
            db: SQLAlchemy数据库实例
            storage_type: 存储类型，'database'或'file_system'
        """
        self.config = default_config()
        self.db = db
        self.storage_type = storage_type
    
    def get_all_icons(self, category_id=None):
        """获取所有图标，支持按分类筛选
        
        Args:
            category_id: 可选的分类ID
            
        Returns:
            图标列表
        """
        if self.storage_type == 'database' and self.db:
            # 数据库存储
            query = Icon.query
            if category_id is not None:
                query = query.filter_by(category_id=category_id)
            return [icon.to_dict() for icon in query.all()]
        else:
            # 文件系统存储
            icons = FileUtils.load_json_file(self.config.ICONS_DATA_FILE, [])
            if category_id is not None:
                icons = [icon for icon in icons if icon.get('category_id') == category_id]
            return icons
    
    def get_icon_by_id(self, icon_id):
        """根据ID获取图标
        
        Args:
            icon_id: 图标ID
            
        Returns:
            图标信息，如果不存在返回None
        """
        if self.storage_type == 'database' and self.db:
            # 数据库存储
            icon = Icon.query.get(icon_id)
            return icon.to_dict() if icon else None
        else:
            # 文件系统存储
            icons = FileUtils.load_json_file(self.config.ICONS_DATA_FILE, [])
            return next((icon for icon in icons if icon.get('id') == icon_id), None)
    
    def create_icon(self, filename, path, category_id, tags=None, description=None):
        """创建新图标
        
        Args:
            filename: 文件名
            path: 文件路径
            category_id: 分类ID
            tags: 标签列表
            description: 描述
            
        Returns:
            创建的图标信息
        """
        if self.storage_type == 'database' and self.db:
            # 数据库存储
            icon = Icon(
                filename=filename,
                path=path,
                category_id=category_id,
                description=description
            )
            if tags:
                icon.tags = tags
            
            self.db.session.add(icon)
            self.db.session.commit()
            
            return icon.to_dict()
        else:
            # 文件系统存储
            icons = FileUtils.load_json_file(self.config.ICONS_DATA_FILE, [])
            
            # 获取下一个ID
            next_id = max([icon.get('id', 0) for icon in icons], default=0) + 1
            now = datetime.now().isoformat()
            
            # 获取分类名称
            categories = FileUtils.load_json_file(self.config.CATEGORIES_DATA_FILE, [])
            category = next((c for c in categories if c['id'] == category_id), None)
            category_name = category['name'] if category else '未知分类'
            
            # 创建新图标
            new_icon = SimpleIcon(
                id=next_id,
                filename=filename,
                path=path,
                category_id=category_id,
                category_name=category_name,
                created_at=now,
                updated_at=now,
                tags=tags or [],
                description=description
            )
            
            # 保存到文件
            icons.append(new_icon.to_dict())
            FileUtils.save_json_file(self.config.ICONS_DATA_FILE, icons)
            
            return new_icon.to_dict()
    
    def update_icon(self, icon_id, updates):
        """更新图标
        
        Args:
            icon_id: 图标ID
            updates: 要更新的字段，字典格式
            
        Returns:
            更新后的图标信息，如果不存在返回None
        """
        if self.storage_type == 'database' and self.db:
            # 数据库存储
            icon = Icon.query.get(icon_id)
            if not icon:
                return None
            
            # 更新字段
            if 'category_id' in updates:
                icon.category_id = updates['category_id']
            if 'tags' in updates:
                icon.tags = updates['tags']
            if 'description' in updates:
                icon.description = updates['description']
            
            self.db.session.commit()
            return icon.to_dict()
        else:
            # 文件系统存储
            icons = FileUtils.load_json_file(self.config.ICONS_DATA_FILE, [])
            icon_index = next((i for i, icon in enumerate(icons) if icon['id'] == icon_id), None)
            
            if icon_index is None:
                return None
            
            icon = icons[icon_index]
            
            # 更新字段
            if 'category_id' in updates:
                icon['category_id'] = updates['category_id']
                # 获取分类名称
                categories = FileUtils.load_json_file(self.config.CATEGORIES_DATA_FILE, [])
                category = next((c for c in categories if c['id'] == updates['category_id']), None)
                if category:
                    icon['category_name'] = category['name']
            
            if 'tags' in updates:
                icon['tags'] = updates['tags']
            
            if 'description' in updates:
                icon['description'] = updates['description']
            
            icon['updated_at'] = datetime.now().isoformat()
            
            # 保存更新
            icons[icon_index] = icon
            FileUtils.save_json_file(self.config.ICONS_DATA_FILE, icons)
            
            return icon
    
    def delete_icon(self, icon_id):
        """删除图标
        
        Args:
            icon_id: 图标ID
            
        Returns:
            是否删除成功
        """
        # 首先获取图标信息，以便删除文件
        icon_info = self.get_icon_by_id(icon_id)
        if not icon_info:
            return False
        
        # 删除文件
        file_path = os.path.join(self.config.ICON_STORAGE_PATH, icon_info['path'])
        FileUtils.delete_file(file_path)
        
        if self.storage_type == 'database' and self.db:
            # 数据库存储
            icon = Icon.query.get(icon_id)
            if icon:
                self.db.session.delete(icon)
                self.db.session.commit()
                return True
        else:
            # 文件系统存储
            icons = FileUtils.load_json_file(self.config.ICONS_DATA_FILE, [])
            icons = [icon for icon in icons if icon.get('id') != icon_id]
            FileUtils.save_json_file(self.config.ICONS_DATA_FILE, icons)
            return True
        
        return False