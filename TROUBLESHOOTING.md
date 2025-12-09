# Docker容器诊断与问题排查

本文档提供了关于图标管理器Docker部署中常见问题的诊断和解决方案，特别是解释为什么`docker stats`命令可能看不到运行中的容器。

## 问题：双击start-docker.bat后，使用docker stats看不到容器

### 可能的原因和解决方案

#### 1. Docker Desktop未运行或权限问题

**症状**：执行Docker命令时出现连接错误，或者容器创建后立即退出。

**解决方案**：
- 确保Docker Desktop已启动并正在运行
- 尝试以管理员身份运行`start-docker.bat`脚本
- 重启Docker Desktop，等待完全启动后再尝试

#### 2. 容器名称冲突

**症状**：`docker ps`显示容器已停止或不存在，但尝试创建时报名称冲突。

**解决方案**：
- 使用`docker ps -a`查看所有容器（包括已停止的）
- 手动删除旧容器：`docker rm icon-manager`
- 重新运行`start-docker.bat`脚本（已更新版本会自动处理这种情况）

#### 3. 容器启动后立即退出

**症状**：容器短暂出现后消失，`docker ps`不显示，但`docker ps -a`显示已停止。

**解决方案**：
- 查看容器日志获取错误信息：`docker logs icon-manager`
- 常见原因：
  - 端口5000已被占用（检查并释放端口）
  - 依赖安装失败（检查requirements.txt）
  - 应用启动时发生错误

#### 4. Docker版本兼容性问题

**症状**：Docker命令执行异常或容器行为不符合预期。

**解决方案**：
- 更新Docker Desktop到最新版本
- 确保Windows版本与Docker兼容
- 检查是否启用了WSL2集成（推荐）

#### 5. 文件权限问题

**症状**：容器能够创建但无法正常访问挂载的卷。

**解决方案**：
- 确保`static/icons`目录有适当的读写权限
- 检查Windows Defender或其他安全软件是否阻止了Docker访问文件
- 临时禁用安全软件，测试是否解决问题

## 诊断步骤

1. **检查Docker服务状态**：
   ```bash
   docker info
   ```
   如果无法连接，请确保Docker Desktop正在运行。

2. **列出所有容器**：
   ```bash
   docker ps -a
   ```
   查看icon-manager容器是否存在，处于什么状态。

3. **查看容器日志**：
   ```bash
   docker logs icon-manager
   ```
   查找错误信息和异常。

4. **检查端口占用**：
   ```bash
   netstat -ano | findstr "5000"
   ```
   确认端口5000未被其他程序占用。

5. **尝试交互式运行容器**：
   ```bash
   docker run -it --rm --name icon-test -p 5001:5000 icon-manager bash
   ```
   进入容器内部进行调试。

## 修改后的start-docker.bat功能说明

更新后的脚本增加了以下诊断功能：

1. **自动清理旧容器**：停止并删除可能存在的同名容器，避免冲突
2. **Docker服务状态检查**：验证是否能正常连接到Docker守护进程
3. **容器状态验证**：确认容器是否真的在运行
4. **详细的状态输出**：显示容器的创建和运行状态
5. **故障提示**：根据检测结果提供针对性的故障排除建议

## 手动验证Docker环境

如果脚本仍然无法正常工作，可以按照以下步骤手动验证Docker环境：

1. **基本连接测试**：
   ```bash
   docker --version
   docker run hello-world
   ```
   如果hello-world容器能正常运行，说明Docker基本功能正常。

2. **创建简单测试容器**：
   ```bash
   docker run -d --name test-nginx -p 8080:80 nginx
   docker stats test-nginx
   ```
   如果这个简单容器也看不到，可以确定是Docker环境问题。

3. **查看Docker Desktop设置**：
   - 确保资源分配足够（CPU、内存）
   - 检查网络设置
   - 验证WSL2集成状态

## 高级诊断方法

### 使用Docker Compose进行测试

如果直接使用`docker run`有问题，可以尝试使用Docker Compose：

1. 执行：`docker-compose up -d`
2. 查看状态：`docker-compose ps`
3. 查看日志：`docker-compose logs`

### 检查Windows事件查看器

在Windows事件查看器中检查应用程序日志，查找与Docker相关的错误信息。

---

## 常见错误代码及含义

| 错误代码 | 含义 | 可能的解决方案 |
|---------|------|--------------|
| 125 | Docker守护进程错误 | 重启Docker Desktop |
| 137 | 容器被强制终止（OOM） | 增加Docker可用内存，或优化应用 |
| 143 | 容器正常退出 | 检查应用是否有正确的启动机制 |
| Cannot connect to Docker daemon | Docker未运行或权限不足 | 启动Docker Desktop，以管理员身份运行 |
| port is already allocated | 端口冲突 | 更改映射端口或关闭占用端口的程序 |

---

如果上述解决方案都无法解决问题，建议完全重置Docker Desktop或重新安装Docker环境。