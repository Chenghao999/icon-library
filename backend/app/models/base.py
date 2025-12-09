# 数据库模型基础文件

# 存储类型常量
STORAGE_TYPES = {
    'FILE_SYSTEM': 'file_system',
    'DATABASE': 'database'
}

# 简单的数据模型类（用于文件系统存储）
class SimpleCategory:
    """简单的分类模型，用于文件系统存储"""
    def __init__(self, id, name, created_at=None, updated_at=None):
        self.id = id
        self.name = name
        self.created_at = created_at
        self.updated_at = updated_at
        
    def to_dict(self):
        """转换为字典格式"""
        return {
            'id': self.id,
            'name': self.name,
            'created_at': self.created_at,
            'updated_at': self.updated_at
        }

class SimpleIcon:
    """简单的图标模型，用于文件系统存储"""
    def __init__(self, id, filename, path, category_id, category_name=None,
                 created_at=None, updated_at=None, tags=None, description=None):
        self.id = id
        self.filename = filename
        self.path = path
        self.category_id = category_id
        self.category_name = category_name
        self.created_at = created_at
        self.updated_at = updated_at
        self.tags = tags or []
        self.description = description
    
    def to_dict(self):
        """转换为字典格式"""
        return {
            'id': self.id,
            'filename': self.filename,
            'path': self.path,
            'category_id': self.category_id,
            'category_name': self.category_name,
            'created_at': self.created_at,
            'updated_at': self.updated_at,
            'tags': self.tags,
            'description': self.description
        }
