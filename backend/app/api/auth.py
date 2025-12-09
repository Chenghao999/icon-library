# 认证相关的API路由
from flask import request, jsonify, session
from functools import wraps
from .. import app_config, SQLALCHEMY_AVAILABLE
from . import api_bp

# 简单的用户验证（这里使用固定的用户名和密码，实际应用中应该从数据库读取）
USER_CREDENTIALS = {
    'admin': 'admin123'  # 简单演示用，实际应用应该使用加密存储的密码
}

# 登录装饰器
def login_required(f):
    """要求用户登录的装饰器"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            return jsonify({"error": "请先登录"}), 401
        return f(*args, **kwargs)
    return decorated_function

@api_bp.route('/login', methods=['POST'])
def login():
    """用户登录API"""
    data = request.get_json() or {}
    
    username = data.get('username')
    password = data.get('password')
    
    if not username or not password:
        return jsonify({"error": "用户名和密码不能为空"}), 400
    
    # 简单的验证逻辑
    if username in USER_CREDENTIALS and USER_CREDENTIALS[username] == password:
        session['user_id'] = username  # 在会话中存储用户名
        return jsonify({"message": "登录成功", "user": username}), 200
    else:
        return jsonify({"error": "用户名或密码错误"}), 401

@api_bp.route('/logout', methods=['POST'])
def logout():
    """用户登出API"""
    session.pop('user_id', None)  # 从会话中删除用户信息
    return jsonify({"message": "登出成功"}), 200

@api_bp.route('/check-login', methods=['GET'])
def check_login():
    """检查用户是否已登录"""
    if 'user_id' in session:
        return jsonify({"logged_in": True, "user": session['user_id']}), 200
    else:
        return jsonify({"logged_in": False}), 200
