# 图标模型文件
import json
from datetime import datetime
from .. import db

class Icon(db.Model):
    """图标数据库模型"""
    __tablename__ = 'icons'
    
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    filename = db.Column(db.String(255), nullable=False, index=True)
    path = db.Column(db.String(500), nullable=False)
    category_id = db.Column(db.Integer, db.ForeignKey('categories.id', ondelete='SET NULL'), nullable=True)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # 使用JSON字段存储标签和描述（如果数据库支持）
    _tags = db.Column('tags', db.Text, nullable=True, default='[]')
    description = db.Column(db.Text, nullable=True)
    
    @property
    def tags(self):
        """获取标签列表"""
        if self._tags:
            try:
                return json.loads(self._tags)
            except (json.JSONDecodeError, TypeError):
                return []
        return []
    
    @tags.setter
    def tags(self, value):
        """设置标签列表"""
        if isinstance(value, list):
            self._tags = json.dumps(value)
        elif isinstance(value, str):
            # 如果传入的是字符串，则尝试解析为JSON
            try:
                parsed = json.loads(value)
                if isinstance(parsed, list):
                    self._tags = value
                else:
                    self._tags = json.dumps([])
            except json.JSONDecodeError:
                self._tags = json.dumps([])
        else:
            self._tags = json.dumps([])
    
    def to_dict(self):
        """转换为字典格式"""
        result = {
            'id': self.id,
            'filename': self.filename,
            'path': self.path,
            'category_id': self.category_id,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
            'tags': self.tags,
            'description': self.description
        }
        
        # 如果有关系，则包含分类名称
        if hasattr(self, 'category') and self.category:
            result['category_name'] = self.category.name
        
        return result
    
    def __repr__(self):
        return f'<Icon(id={self.id}, filename="{self.filename}", category_id={self.category_id})>'
