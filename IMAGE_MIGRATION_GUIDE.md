# 图标管理器镜像迁移指南

本指南详细说明了如何将图标管理器应用打包为Docker镜像，以及如何将该镜像保存、传输到其他设备并在那里加载使用。

## 1. 前提条件

确保您的开发设备上已安装：
- Docker Engine 19.03或更高版本
- Docker Compose

## 2. 构建Docker镜像

### 2.1 检查项目结构

在构建镜像前，确保项目目录包含所有必要文件：

```
icon_store/
├── app.py              # 主应用程序文件
├── requirements.txt    # Python依赖项列表
├── templates/          # HTML模板文件夹
├── static/             # 静态资源文件夹
├── data/               # 数据存储目录
├── Dockerfile          # Docker构建文件
└── docker-compose.yml  # Docker Compose配置
```

### 2.2 使用Docker Compose构建镜像

1. 打开终端，导航到项目根目录
2. 执行以下命令构建镜像：

```bash
docker-compose build
```

这将根据docker-compose.yml中的配置构建名为`icon-manager`的镜像。

### 2.3 手动构建Docker镜像

您也可以直接使用Docker命令构建镜像：

```bash
docker build -t icon-manager:latest .
```

这里`icon-manager`是镜像名称，`:latest`是标签，可以根据需要修改。

## 3. 保存Docker镜像

构建完成后，可以将镜像保存为tar文件以便传输：

```bash
docker save -o icon-manager-image.tar icon-manager:latest
```

这将在当前目录创建一个名为`icon-manager-image.tar`的文件，其中包含完整的Docker镜像。

## 4. 传输镜像到其他设备

有多种方式可以将镜像文件传输到其他设备：

1. 使用USB驱动器或其他外部存储设备复制tar文件
2. 通过网络共享、FTP或云存储服务传输文件
3. 如果目标设备可以访问互联网，也可以考虑使用Docker Hub等容器注册表

## 5. 在目标设备上加载和运行镜像

### 5.1 加载Docker镜像

在目标设备上，打开终端并执行以下命令加载镜像：

```bash
docker load -i icon-manager-image.tar
```

### 5.2 使用Docker Compose运行

如果您也复制了docker-compose.yml文件，可以直接使用Docker Compose启动应用：

```bash
docker-compose up -d
```

### 5.3 手动运行Docker容器

或者，您可以直接使用docker run命令启动容器：

```bash
docker run -d --name icon-manager \
  -p 5000:5000 \
  -v $(pwd)/static/icons:/app/static/icons \
  -e SECRET_KEY=your_secure_secret_key_here \
  -e ICON_STORAGE_PATH=/app/static/icons \
  -e FLASK_ENV=production \
  icon-manager:latest
```

### 5.4 访问应用

应用启动后，可以通过浏览器访问：`http://localhost:5000`

## 6. 数据持久化

注意，为了保存图标数据，需要确保在目标设备上也设置了卷映射：

- 在启动容器时使用`-v`参数映射静态图标目录
- 或者确保docker-compose.yml文件中的volumes配置正确

## 7. 常见问题排查

### 端口占用
如果5000端口已被占用，可以通过修改端口映射来解决：
```bash
docker run -p 8080:5000 ...  # 使用8080端口代替5000
```

### 权限问题
确保挂载的目录具有正确的读写权限：
```bash
chmod -R 755 ./static/icons
```

### 无法访问应用
- 检查容器是否正在运行：`docker ps`
- 查看容器日志：`docker logs icon-manager`
- 确认防火墙设置允许访问相关端口
