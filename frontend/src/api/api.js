// API 通信模块

// 后端API基础URL
const API_BASE_URL = '/api';
const ICON_BASE_URL = '/api/icons';

// 创建API对象
const api = {
    /**
     * 获取所有图标
     * @param {string} categoryId - 可选的分类ID
     * @returns {Promise}
     */
    async getIcons(categoryId = '') {
        let url = `${API_BASE_URL}/icons`;
        if (categoryId) {
            url += `?category_id=${categoryId}`;
        }
        return await this.request(url, 'GET');
    },
    
    /**
     * 获取单个图标信息
     * @param {string} iconId - 图标ID
     * @returns {Promise}
     */
    async getIcon(iconId) {
        return await this.request(`${API_BASE_URL}/icons/${iconId}`, 'GET');
    },
    
    /**
     * 上传图标
     * @param {FormData} formData - 包含图标文件和信息的FormData
     * @returns {Promise}
     */
    async uploadIcon(formData) {
        return await this.request(`${API_BASE_URL}/icons`, 'POST', formData, {
            'Content-Type': 'multipart/form-data'
        });
    },
    
    /**
     * 删除图标
     * @param {string} iconId - 图标ID
     * @returns {Promise}
     */
    async deleteIcon(iconId) {
        return await this.request(`${API_BASE_URL}/icons/${iconId}`, 'DELETE');
    },
    
    /**
     * 获取所有分类
     * @returns {Promise}
     */
    async getCategories() {
        return await this.request(`${API_BASE_URL}/categories`, 'GET');
    },
    
    /**
     * 创建新分类
     * @param {Object} category - 分类对象
     * @returns {Promise}
     */
    async createCategory(category) {
        return await this.request(`${API_BASE_URL}/categories`, 'POST', category);
    },
    
    /**
     * 删除分类
     * @param {string} categoryId - 分类ID
     * @returns {Promise}
     */
    async deleteCategory(categoryId) {
        return await this.request(`${API_BASE_URL}/categories/${categoryId}`, 'DELETE');
    },
    
    /**
     * 用户登录
     * @param {string} username - 用户名
     * @param {string} password - 密码
     * @returns {Promise}
     */
    async login(username, password) {
        return await this.request(`${API_BASE_URL}/auth/login`, 'POST', {
            username,
            password
        });
    },
    
    /**
     * 用户登出
     * @returns {Promise}
     */
    async logout() {
        return await this.request(`${API_BASE_URL}/auth/logout`, 'POST');
    },
    
    /**
     * 检查登录状态
     * @returns {Promise}
     */
    async checkLoginStatus() {
        return await this.request(`${API_BASE_URL}/auth/status`, 'GET');
    },
    
    /**
     * 获取图标文件URL
     * @param {string} filename - 图标文件名
     * @returns {string}
     */
    getIconUrl(filename) {
        return `${ICON_BASE_URL}/files/${filename}`;
    },
    
    /**
     * 通用请求方法
     * @param {string} url - 请求URL
     * @param {string} method - 请求方法
     * @param {Object|FormData} data - 请求数据
     * @param {Object} customHeaders - 自定义请求头
     * @returns {Promise}
     */
    async request(url, method = 'GET', data = null, customHeaders = {}) {
        try {
            const options = {
                method,
                headers: {
                    'Accept': 'application/json',
                    ...customHeaders
                },
                credentials: 'include' // 包含Cookie
            };
            
            // 如果不是FormData且有数据，设置Content-Type为JSON
            if (data && !(data instanceof FormData) && method !== 'GET') {
                options.headers['Content-Type'] = 'application/json';
                options.body = JSON.stringify(data);
            } else if (data instanceof FormData) {
                // FormData会自动设置正确的Content-Type
                options.body = data;
            }
            
            const response = await fetch(url, options);
            
            // 尝试解析JSON响应
            let responseData;
            try {
                responseData = await response.json();
            } catch (e) {
                responseData = {};
            }
            
            // 检查响应状态
            if (!response.ok) {
                throw new Error(responseData.message || `请求失败: ${response.status}`);
            }
            
            return {
                ok: true,
                status: response.status,
                data: responseData
            };
        } catch (error) {
            console.error('API请求错误:', error);
            return {
                ok: false,
                error: error.message
            };
        }
    }
};

// 导出API对象
window.api = api;