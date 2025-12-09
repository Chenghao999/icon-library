# 分类模型文件
from datetime import datetime
from .. import db

class Category(db.Model):
    """分类数据库模型"""
    __tablename__ = 'categories'
    
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(100), nullable=False, unique=True, index=True)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # 关系定义
    icons = db.relationship('Icon', backref='category', lazy=True, cascade='all, delete-orphan')
    
    def to_dict(self):
        """转换为字典格式"""
        return {
            'id': self.id,
            'name': self.name,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
            'icon_count': len(self.icons)  # 返回该分类下的图标数量
        }
    
    def __repr__(self):
        return f'<Category(id={self.id}, name="{self.name}")>'
