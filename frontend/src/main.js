// 前端主脚本文件

// 全局状态
const appState = {
    isLoggedIn: false,
    currentView: 'all', // 'all', 'categories', 'upload', 'login'
    categories: [],
    selectedCategory: ''
};

// DOM 加载完成后执行
window.addEventListener('DOMContentLoaded', () => {
    // 初始化应用
    initApp();
    
    // 绑定导航事件
    document.getElementById('nav-all').addEventListener('click', () => showView('all'));
    document.getElementById('nav-categories').addEventListener('click', () => showView('categories'));
    document.getElementById('nav-upload').addEventListener('click', () => showView('upload'));
    document.getElementById('nav-login').addEventListener('click', () => {
        if (appState.isLoggedIn) {
            logout();
        } else {
            showView('login');
        }
    });
    
    // 绑定刷新按钮事件
    document.getElementById('refresh-btn').addEventListener('click', loadIcons);
    
    // 绑定分类选择事件
    document.getElementById('category-select').addEventListener('change', (e) => {
        appState.selectedCategory = e.target.value;
        loadIcons();
    });
    
    // 绑定上传表单提交事件
    document.getElementById('upload-form').addEventListener('submit', handleIconUpload);
    
    // 绑定分类管理相关事件
    document.getElementById('add-category-btn').addEventListener('click', addCategory);
    
    // 绑定登录表单提交事件
    document.getElementById('login-form-element').addEventListener('submit', handleLogin);
});

// 初始化应用
async function initApp() {
    // 检查登录状态
    await checkLoginStatus();
    
    // 加载分类
    await loadCategories();
    
    // 加载图标
    loadIcons();
}

// 检查登录状态
async function checkLoginStatus() {
    try {
        const response = await api.checkLoginStatus();
        if (response.ok && response.data.logged_in) {
            appState.isLoggedIn = true;
            updateLoginUI();
        }
    } catch (error) {
        console.error('检查登录状态失败:', error);
    }
}

// 更新登录相关UI
function updateLoginUI() {
    const loginBtn = document.getElementById('nav-login');
    if (appState.isLoggedIn) {
        loginBtn.textContent = '登出';
        loginBtn.classList.remove('nav-login-btn');
        loginBtn.classList.add('nav-logout-btn');
        
        // 显示管理功能和编辑按钮
        document.getElementById('nav-categories').style.display = 'block';
        document.getElementById('nav-upload').style.display = 'block';
        
        // 显示所有编辑相关按钮
        const editButtons = document.querySelectorAll('.icon-actions .btn-delete, .btn-delete-category, #add-category-btn');
        editButtons.forEach(btn => btn.style.display = 'inline-block');
    } else {
        loginBtn.textContent = '登录';
        loginBtn.classList.add('nav-login-btn');
        loginBtn.classList.remove('nav-logout-btn');
        
        // 隐藏所有编辑和上传功能
        document.getElementById('nav-categories').style.display = 'none';
        document.getElementById('nav-upload').style.display = 'none';
        
        // 如果当前视图是编辑相关视图，切换到默认视图
        if (appState.currentView === 'upload' || appState.currentView === 'categories') {
            showView('all');
        }
    }
}

// 显示不同视图
function showView(viewName) {
    // 隐藏所有视图
    document.getElementById('icons-grid').parentElement.style.display = 'none';
    document.getElementById('category-filter').style.display = 'none';
    document.getElementById('category-management').style.display = 'none';
    document.getElementById('upload-form-container').style.display = 'none';
    document.getElementById('login-form').style.display = 'none';
    
    // 显示选中的视图
    appState.currentView = viewName;
    
    switch(viewName) {
        case 'all':
            document.getElementById('icons-grid').parentElement.style.display = 'block';
            document.getElementById('category-filter').style.display = 'block';
            break;
        case 'categories':
            document.getElementById('category-management').style.display = 'block';
            renderCategories();
            break;
        case 'upload':
            document.getElementById('upload-form-container').style.display = 'block';
            break;
        case 'login':
            document.getElementById('login-form').style.display = 'block';
            break;
    }
}

// 加载分类
async function loadCategories() {
    try {
        const response = await api.getCategories();
        if (response.ok) {
            appState.categories = response.data;
            updateCategoryDropdowns();
        }
    } catch (error) {
        console.error('加载分类失败:', error);
        alert('加载分类失败，请稍后再试');
    }
}

// 更新分类下拉选择框
function updateCategoryDropdowns() {
    const categorySelects = [
        document.getElementById('category-select'),
        document.getElementById('icon-category')
    ];
    
    categorySelects.forEach((select, index) => {
        if (!select) return;
        
        // 清空除了第一个选项外的所有选项
        while (select.options.length > (index === 0 ? 1 : 0)) {
            select.remove(1);
        }
        
        // 添加分类选项
        appState.categories.forEach(category => {
            const option = document.createElement('option');
            option.value = category.id;
            option.textContent = category.name;
            select.appendChild(option);
        });
    });
}

// 加载图标
async function loadIcons() {
    const iconsGrid = document.getElementById('icons-grid');
    iconsGrid.innerHTML = '<div class="loading">加载中...</div>';
    
    try {
        const response = await api.getIcons(appState.selectedCategory);
        if (response.ok) {
            renderIcons(response.data);
        }
    } catch (error) {
        console.error('加载图标失败:', error);
        iconsGrid.innerHTML = '<div class="error-message">加载图标失败，请稍后再试</div>';
    }
}

// 渲染图标网格
function renderIcons(icons) {
    const iconsGrid = document.getElementById('icons-grid');
    
    if (icons.length === 0) {
        iconsGrid.innerHTML = '<div class="empty-state">暂无图标</div>';
        return;
    }
    
    // 清空网格
    iconsGrid.innerHTML = '';
    
    // 创建图标项
    icons.forEach(icon => {
        const iconItem = document.createElement('div');
        iconItem.className = 'icon-item';
        iconItem.dataset.iconId = icon.id;
        
        // 创建图标预览
        const iconPreview = document.createElement('div');
        iconPreview.className = 'icon-preview';
        const iconUrl = api.getIconUrl(icon.id);

        // #region agent log
        fetch('http://127.0.0.1:7242/ingest/2bd302be-89d3-4f8c-b4a7-d31a5cb8ba79',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({sessionId:'debug-session',runId:'pre-fix',hypothesisId:'H1',location:'frontend/src/main.js:renderIcons',message:'render icon url',data:{iconId:icon.id,filename:icon.filename,computedUrl:iconUrl,origin:window.location.origin},timestamp:Date.now()})}).catch(()=>{});
        // #endregion

        iconPreview.innerHTML = `<img src="${iconUrl}" alt="${icon.filename}">`;
        
        // 创建图标信息
        const iconInfo = document.createElement('div');
        iconInfo.className = 'icon-info';
        iconInfo.innerHTML = `
            <h3>${icon.filename}</h3>
            <p>分类: ${getCategoryName(icon.category_id)}</p>
            ${icon.tags && icon.tags.length > 0 ? `<p>标签: ${icon.tags.join(', ')}</p>` : ''}
        `;
        
        // 创建操作按钮容器
        const iconActions = document.createElement('div');
        iconActions.className = 'icon-actions';
        
        // 下载按钮
        const downloadBtn = document.createElement('a');
        downloadBtn.className = 'btn btn-download';
        downloadBtn.href = iconUrl;
        downloadBtn.download = icon.filename;
        downloadBtn.textContent = '下载';
        downloadBtn.addEventListener('click', () => {
            // #region agent log
            fetch('http://127.0.0.1:7242/ingest/2bd302be-89d3-4f8c-b4a7-d31a5cb8ba79',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({sessionId:'debug-session',runId:'pre-fix',hypothesisId:'H3',location:'frontend/src/main.js:downloadClick',message:'download clicked',data:{iconId:icon.id,href:iconUrl,origin:window.location.origin},timestamp:Date.now()})}).catch(()=>{});
            // #endregion
        });
        
        // 仅登录用户显示管理按钮
        if (appState.isLoggedIn) {
            // 分类转移下拉菜单
            const transferGroup = document.createElement('div');
            transferGroup.className = 'transfer-group';
            transferGroup.innerHTML = '<span>转移到:</span>';
            
            const categorySelect = document.createElement('select');
            categorySelect.className = 'category-select';
            categorySelect.dataset.iconId = icon.id;
            categorySelect.dataset.currentCategory = icon.category_id || null;
            
            // 添加默认选项
            const defaultOption = document.createElement('option');
            defaultOption.value = '';
            defaultOption.textContent = '选择分类';
            categorySelect.appendChild(defaultOption);
            
            // 添加所有分类选项
            appState.categories.forEach(category => {
                // 跳过当前分类
                if (category.id === icon.category_id) return;
                
                const option = document.createElement('option');
                option.value = category.id;
                option.textContent = category.name;
                categorySelect.appendChild(option);
            });
            
            // 添加事件监听器
            categorySelect.addEventListener('change', (e) => {
                const newCategoryId = e.target.value;
                if (newCategoryId) {
                    transferIconCategory(icon.id, newCategoryId);
                    // 重置选择框
                    e.target.value = '';
                }
            });
            
            transferGroup.appendChild(categorySelect);
            iconActions.appendChild(transferGroup);
            
            // 删除按钮
            const deleteBtn = document.createElement('button');
            deleteBtn.className = 'btn btn-delete';
            deleteBtn.textContent = '删除';
            deleteBtn.addEventListener('click', () => deleteIcon(icon.id));
            iconActions.appendChild(deleteBtn);
        }
        
        iconActions.appendChild(downloadBtn);
        iconItem.appendChild(iconPreview);
        iconItem.appendChild(iconInfo);
        iconItem.appendChild(iconActions);
        
        iconsGrid.appendChild(iconItem);
    });
}

// 根据分类ID获取分类名称
function getCategoryName(categoryId) {
    const category = appState.categories.find(c => c.id === categoryId);
    return category ? category.name : '未分类';
}

// 删除图标
async function deleteIcon(iconId) {
    if (!appState.isLoggedIn) {
        alert('请先登录');
        return;
    }
    
    if (!confirm('确定要删除这个图标吗？此操作不可恢复。')) {
        return;
    }
    
    try {
        // #region agent log
        fetch('http://127.0.0.1:7242/ingest/2bd302be-89d3-4f8c-b4a7-d31a5cb8ba79',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({sessionId:'debug-session',runId:'pre-fix',hypothesisId:'H4',location:'frontend/src/main.js:deleteIcon',message:'delete start',data:{iconId},timestamp:Date.now()})}).catch(()=>{});
        // #endregion

        const response = await api.deleteIcon(iconId);
        if (response.ok) {
            // 删除成功，重新加载图标列表
            loadIcons();
            // #region agent log
            fetch('http://127.0.0.1:7242/ingest/2bd302be-89d3-4f8c-b4a7-d31a5cb8ba79',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({sessionId:'debug-session',runId:'pre-fix',hypothesisId:'H4',location:'frontend/src/main.js:deleteIcon',message:'delete ok',data:{iconId},timestamp:Date.now()})}).catch(()=>{});
            // #endregion
        } else {
            alert('删除图标失败: ' + (response.error || '未知错误'));
        }
    } catch (error) {
        console.error('删除图标出错:', error);
        alert('删除图标失败: ' + (error.message || '未知错误'));
        // #region agent log
        fetch('http://127.0.0.1:7242/ingest/2bd302be-89d3-4f8c-b4a7-d31a5cb8ba79',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({sessionId:'debug-session',runId:'pre-fix',hypothesisId:'H4',location:'frontend/src/main.js:deleteIcon',message:'delete error',data:{iconId,error:error?.message},timestamp:Date.now()})}).catch(()=>{});
        // #endregion
    }
}

// 转移图标到其他分类
async function transferIconCategory(iconId, newCategoryId) {
    if (!appState.isLoggedIn) {
        alert('请先登录');
        return;
    }
    
    try {
        // #region agent log
        fetch('http://127.0.0.1:7242/ingest/2bd302be-89d3-4f8c-b4a7-d31a5cb8ba79',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({sessionId:'debug-session',runId:'pre-fix',hypothesisId:'H2',location:'frontend/src/main.js:transferIconCategory',message:'transfer start',data:{iconId,newCategoryId},timestamp:Date.now()})}).catch(()=>{});
        // #endregion

        const response = await api.updateIcon(iconId, {
            category_id: newCategoryId
        });
        
        if (response.ok) {
            // 转移成功，重新加载图标列表
            loadIcons();
            // #region agent log
            fetch('http://127.0.0.1:7242/ingest/2bd302be-89d3-4f8c-b4a7-d31a5cb8ba79',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({sessionId:'debug-session',runId:'pre-fix',hypothesisId:'H2',location:'frontend/src/main.js:transferIconCategory',message:'transfer ok',data:{iconId,newCategoryId},timestamp:Date.now()})}).catch(()=>{});
            // #endregion
        } else {
            alert('转移分类失败: ' + (response.error || '未知错误'));
        }
    } catch (error) {
        console.error('转移分类出错:', error);
        alert('转移分类失败: ' + (error.message || '未知错误'));
        // #region agent log
        fetch('http://127.0.0.1:7242/ingest/2bd302be-89d3-4f8c-b4a7-d31a5cb8ba79',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({sessionId:'debug-session',runId:'pre-fix',hypothesisId:'H2',location:'frontend/src/main.js:transferIconCategory',message:'transfer error',data:{iconId,newCategoryId,error:error?.message},timestamp:Date.now()})}).catch(()=>{});
        // #endregion
    }
}

// 处理图标上传
async function handleIconUpload(e) {
    e.preventDefault();
    
    const fileInput = document.getElementById('icon-file');
    const categorySelect = document.getElementById('icon-category');
    const tagsInput = document.getElementById('icon-tags');
    const descriptionInput = document.getElementById('icon-description');
    
    // 创建FormData对象
    const formData = new FormData();
    formData.append('icon', fileInput.files[0]);
    formData.append('category_id', categorySelect.value);
    
    // 处理标签
    if (tagsInput.value.trim()) {
        const tags = tagsInput.value.split(',').map(tag => tag.trim());
        formData.append('tags', JSON.stringify(tags));
    }
    
    // 处理描述
    if (descriptionInput.value.trim()) {
        formData.append('description', descriptionInput.value.trim());
    }
    
    try {
        const response = await api.uploadIcon(formData);
        if (response.ok) {
            alert('图标上传成功！');
            // 重置表单
            document.getElementById('upload-form').reset();
            // 刷新图标列表
            loadIcons();
        }
    } catch (error) {
        console.error('上传图标失败:', error);
        alert('上传图标失败: ' + (error.message || '未知错误'));
    }
}

// 渲染分类管理视图
function renderCategories() {
    const categoryList = document.getElementById('category-list');
    categoryList.innerHTML = '';
    
    if (appState.isLoggedIn) {
        // 登录状态下显示完整的分类管理
        appState.categories.forEach(category => {
            const categoryItem = document.createElement('div');
            categoryItem.className = 'category-item';
            categoryItem.innerHTML = `
                <span>${category.name}</span>
                <button class="btn-delete-category" data-id="${category.id}">删除</button>
            `;
            categoryList.appendChild(categoryItem);
        });
        
        // 绑定删除分类事件
        document.querySelectorAll('.btn-delete-category').forEach(btn => {
            btn.addEventListener('click', (e) => deleteCategory(e.target.dataset.id));
        });
    } else {
        // 未登录状态下显示提示信息
        const loginPrompt = document.createElement('div');
        loginPrompt.className = 'login-prompt';
        loginPrompt.textContent = '请先登录以管理分类';
        categoryList.appendChild(loginPrompt);
    }
}

// 添加分类
async function addCategory() {
    const categoryNameInput = document.getElementById('new-category-name');
    const categoryName = categoryNameInput.value.trim();
    
    if (!categoryName) {
        alert('请输入分类名称');
        return;
    }
    
    try {
        const response = await api.createCategory({ name: categoryName });
        if (response.ok) {
            alert('分类添加成功！');
            categoryNameInput.value = '';
            // 重新加载分类
            await loadCategories();
            renderCategories();
        }
    } catch (error) {
        console.error('添加分类失败:', error);
        alert('添加分类失败: ' + (error.message || '未知错误'));
    }
}

// 删除分类
async function deleteCategory(categoryId) {
    if (!appState.isLoggedIn) {
        alert('请先登录');
        return;
    }
    
    if (!confirm('确定要删除这个分类吗？该分类下的图标将被移至未分类。')) {
        return;
    }
    
    try {
        const response = await api.deleteCategory(categoryId);
        if (response.ok) {
            alert('分类删除成功！');
            // 重新加载分类
            await loadCategories();
            renderCategories();
            // 如果当前选中的是被删除的分类，重置选择
            if (appState.selectedCategory === categoryId) {
                appState.selectedCategory = '';
                document.getElementById('category-select').value = '';
                loadIcons();
            }
        }
    } catch (error) {
        console.error('删除分类失败:', error);
        alert('删除分类失败: ' + (error.message || '未知错误'));
    }
}

// 删除图标函数已在上方定义

// 处理登录
async function handleLogin(e) {
    e.preventDefault();
    
    const username = document.getElementById('username').value;
    const password = document.getElementById('password').value;
    const errorElement = document.getElementById('login-error');
    
    try {
        const response = await api.login(username, password);
        if (response.ok) {
            appState.isLoggedIn = true;
            updateLoginUI();
            showView('all');
            // 重置表单
            document.getElementById('login-form-element').reset();
            errorElement.textContent = '';
        } else {
            errorElement.textContent = '用户名或密码错误';
        }
    } catch (error) {
        console.error('登录失败:', error);
        errorElement.textContent = '登录失败，请稍后再试';
    }
}

// 登出
async function logout() {
    try {
        const response = await api.logout();
        if (response.ok) {
            appState.isLoggedIn = false;
            updateLoginUI();
        }
    } catch (error) {
        console.error('登出失败:', error);
    }
}