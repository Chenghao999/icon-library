# 图标管理器

一个简单易用的图标管理系统，可以帮助您分类管理图标、重命名图标，并提供URL复制功能，方便在导航页中使用。支持Docker和非Docker部署，兼容Windows、Mac和群晖NAS等平台。

## 功能特点

- **图标上传**：支持单个和批量上传图标文件
- **分类管理**：创建自定义分类，灵活管理图标
- **图标重命名**：方便地修改图标显示名称
- **URL复制**：一键复制图标URL，直接用于导航页
- **响应式设计**：适配不同屏幕尺寸
- **Docker支持**：容器化部署，简单便捷
- **跨平台兼容**：支持Windows、Mac和群晖NAS等设备
- **自动后备存储**：在数据库不可用时自动切换到文件系统存储

## 技术栈

- **后端**：Python Flask
- **数据库**：SQLite (可替换为其他数据库)
- **前端**：HTML, CSS, JavaScript
- **容器化**：Docker & Docker Compose

## 快速开始

### 方法一：使用Docker运行（推荐）

1. 确保您已安装Docker和Docker Compose

2. 在项目根目录下执行：

```bash
docker-compose up -d
```

3. 打开浏览器访问：http://localhost:5000

### 方法二：非Docker直接运行（Windows专用）

1. 确保已安装Python 3.6+
2. 双击运行 `run-local.bat` 脚本
3. 脚本会自动：
   - 创建必要的目录结构
   - 安装所需依赖
   - 设置环境变量
   - 启动应用程序
4. 打开浏览器访问 http://localhost:5000

### 方法三：非Docker手动运行（Mac/Linux/群晖NAS）

1. 确保已安装Python 3.6+
2. 打开终端，进入项目目录
3. 运行以下命令：
   ```bash
   python -m pip install -r requirements.txt --user
   python app.py
   ```
4. 打开浏览器访问 http://localhost:5000

## 手动配置（可选）

如果需要自定义配置，可以在项目根目录创建 `.env` 文件，内容如下：

```
# 应用密钥（建议修改为随机字符串）
SECRET_KEY=your_secret_key_here

# 图标存储路径
ICON_STORAGE_PATH=./static/icons

# 数据库连接字符串（如果使用数据库）
DATABASE_URL=sqlite:///./icon_store.db
```

## 使用说明

### 上传图标

1. 在上传区域选择单个或多个图标文件
2. 选择分类（可选）
3. 点击上传按钮

### 管理分类

1. 在分类管理区域输入新分类名称
2. 点击添加分类按钮
3. 点击分类标签可以筛选显示特定分类的图标

### 重命名图标

1. 找到需要重命名的图标
2. 点击重命名按钮
3. 输入新名称并保存

### 复制URL

1. 找到需要使用的图标
2. 点击复制URL按钮
3. URL会自动复制到剪贴板，可以直接粘贴到导航页中使用

### 修改图标分类

1. 在图标下方的下拉菜单中选择新分类
2. 系统会自动保存分类变更，文件会自动移动到相应分类文件夹

## 文件结构

```
icon_store/
├── static/
│   ├── css/           # 样式文件
│   └── icons/         # 图标存储根目录
│       ├── 未分类/     # 未分类图标文件夹
│       └── [分类名称]/ # 按分类创建的文件夹
├── templates/         # HTML模板
├── data/              # 数据库文件和文件系统存储数据
├── app.py             # 主应用程序
├── requirements.txt   # Python依赖
├── run-local.bat      # Windows非Docker启动脚本
├── Dockerfile         # Docker构建文件
└── docker-compose.yml # Docker Compose配置
```

## 系统要求

- **Python**: 3.6 或更高版本
- **磁盘空间**: 取决于您存储的图标数量
- **权限要求**: 对static/icons目录的读写权限
- **网络**: 能够访问本地网络(用于Web界面)

## 故障排除

### 常见问题

1. **Flask命令不可识别**
   - 问题: 在运行`flask run`时出现"flask未被识别"错误
   - 解决方案: 使用`python app.py`直接运行，或使用`run-local.bat`脚本

2. **端口占用**
   - 问题: 5000端口被占用导致无法启动
   - 解决方案: 在app.py文件中修改`port=5000`为其他端口号

3. **权限错误**
   - 问题: 出现权限相关错误
   - 解决方案: 确保有对static/icons和data目录的读写权限

4. **依赖安装失败**
   - 问题: 在Python 3.13+版本上安装依赖失败
   - 解决方案: 使用`--user`参数安装，或使用更新的依赖版本

5. **跨平台使用注意事项**
   - Windows: 使用`run-local.bat`简化操作
   - 群晖NAS: 通过SSH终端或Task Scheduler运行，需确保Python环境已安装
   - Mac: 在终端中执行安装和启动命令

### 日志和错误

应用程序会在控制台输出运行日志和错误信息，可用于排查问题。

## 安全说明

- 系统包含基本的文件路径验证，防止路径遍历攻击
- 建议在生产环境中配置适当的访问控制
- 定期备份图标数据以防止意外丢失

## 许可证

本项目采用MIT许可证。

## 支持的图标格式

- PNG (.png)
- JPG/JPEG (.jpg, .jpeg)
- GIF (.gif)
- SVG (.svg)
- ICO (.ico)
- WebP (.webp)

## 注意事项

- 使用Docker运行时，图标文件和数据库会保存在宿主机的卷中，确保数据持久化
- 请不要上传包含敏感信息的图标文件
- 定期备份您的图标和数据库文件
- 图标按分类存储在物理文件夹中，更改分类会触发文件移动

## License

MIT