#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
数据库初始化脚本
"""

import os
import sys
from app import create_app, db
from app.models.category import Category
from app.services.category_service import CategoryService

# 添加当前目录到系统路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def init_database():
    """初始化数据库"""
    print("开始初始化数据库...")
    
    # 创建应用实例
    app = create_app()
    
    with app.app_context():
        # 创建数据库表
        print("创建数据库表...")
        db.create_all()
        
        # 初始化默认分类
        print("初始化默认分类...")
        category_service = CategoryService()
        
        # 检查是否已有分类数据
        if Category.query.count() == 0:
            # 创建默认分类
            default_categories = [
                {"name": "未分类"},
                {"name": "用户界面"},
                {"name": "社交媒体"},
                {"name": "工具"},
                {"name": "编辑"},
                {"name": "导航"}
            ]
            
            for cat_data in default_categories:
                category = category_service.create_category(cat_data)
                print(f"创建分类: {category.name}")
            
            print(f"成功创建 {len(default_categories)} 个默认分类")
        else:
            print("分类数据已存在，跳过初始化")
        
        print("数据库初始化完成!")

if __name__ == "__main__":
    try:
        init_database()
    except Exception as e:
        print(f"数据库初始化失败: {str(e)}")
        sys.exit(1)