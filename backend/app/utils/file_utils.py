# 文件操作工具类
import os
import shutil
import re
import json
from werkzeug.utils import secure_filename

class FileUtils:
    """文件操作工具类"""
    
    @staticmethod
    def ensure_directory_exists(directory_path):
        """确保目录存在，如果不存在则创建"""
        if not os.path.exists(directory_path):
            os.makedirs(directory_path)
    
    @staticmethod
    def sanitize_filename(filename):
        """生成安全的文件名
        
        Args:
            filename: 原始文件名
            
        Returns:
            安全处理后的文件名
        """
        filename = secure_filename(filename)
        # 移除特殊字符
        filename = re.sub(r'[^a-zA-Z0-9._-]', '_', filename)
        # 确保文件名长度合理
        name, ext = os.path.splitext(filename)
        if len(name) > 50:
            name = name[:50] + '_'
        return name + ext
    
    @staticmethod
    def is_allowed_file(filename, allowed_extensions):
        """检查文件扩展名是否允许
        
        Args:
            filename: 文件名
            allowed_extensions: 允许的扩展名集合，例如 {'png', 'jpg', 'jpeg'}
            
        Returns:
            布尔值，表示文件类型是否被允许
        """
        return '.' in filename and filename.rsplit('.', 1)[1].lower() in allowed_extensions
    
    @staticmethod
    def load_json_file(file_path, default=None):
        """加载JSON文件
        
        Args:
            file_path: JSON文件路径
            default: 文件不存在时的默认返回值
            
        Returns:
            JSON数据或默认值
        """
        if default is None:
            default = {}
            
        try:
            if os.path.exists(file_path):
                with open(file_path, 'r', encoding='utf-8') as f:
                    return json.load(f)
            return default
        except (json.JSONDecodeError, IOError):
            return default
    
    @staticmethod
    def save_json_file(file_path, data, ensure_directories=True):
        """保存数据到JSON文件
        
        Args:
            file_path: JSON文件路径
            data: 要保存的数据
            ensure_directories: 是否确保目录存在
            
        Returns:
            布尔值，表示操作是否成功
        """
        try:
            if ensure_directories:
                directory = os.path.dirname(file_path)
                FileUtils.ensure_directory_exists(directory)
                
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            return True
        except IOError:
            return False
    
    @staticmethod
    def move_file(source_path, destination_path):
        """移动文件
        
        Args:
            source_path: 源文件路径
            destination_path: 目标文件路径
            
        Returns:
            布尔值，表示操作是否成功
        """
        try:
            # 确保目标目录存在
            destination_dir = os.path.dirname(destination_path)
            FileUtils.ensure_directory_exists(destination_dir)
            
            # 移动文件
            shutil.move(source_path, destination_path)
            return True
        except (IOError, OSError):
            return False
    
    @staticmethod
    def copy_file(source_path, destination_path):
        """复制文件
        
        Args:
            source_path: 源文件路径
            destination_path: 目标文件路径
            
        Returns:
            布尔值，表示操作是否成功
        """
        try:
            # 确保目标目录存在
            destination_dir = os.path.dirname(destination_path)
            FileUtils.ensure_directory_exists(destination_dir)
            
            # 复制文件
            shutil.copy2(source_path, destination_path)
            return True
        except (IOError, OSError):
            return False
    
    @staticmethod
    def delete_file(file_path):
        """删除文件
        
        Args:
            file_path: 要删除的文件路径
            
        Returns:
            布尔值，表示操作是否成功
        """
        try:
            if os.path.exists(file_path):
                os.remove(file_path)
                return True
            return False
        except (IOError, OSError):
            return False
