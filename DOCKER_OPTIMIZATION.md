# Docker镜像优化指南

## 已实施的优化措施

### 1. 多阶段构建（Multi-stage Build）
- **构建阶段**：使用`python:3.9-slim`作为构建环境，包含编译工具
- **运行阶段**：使用`python:3.9-alpine`作为最终运行环境，体积更小
- **优势**：将编译依赖与运行时依赖分离，减小最终镜像体积

### 2. 基础镜像优化
- 从完整的Python镜像切换到Alpine基础镜像（体积减少约80%）
- Alpine是一个非常轻量级的Linux发行版，基础镜像仅约5MB

### 3. 依赖优化
- 使用虚拟环境（venv）隔离Python依赖
- 仅复制必要的虚拟环境文件到最终镜像
- 使用轻量级的`waitress`替代`gunicorn`作为WSGI服务器

### 4. 文件系统优化
- 仅复制必要的应用文件，排除测试、文档和临时文件
- 使用`.dockerignore`和`.gitignore`排除不必要的文件
- 合并RUN指令，减少镜像层数量

### 5. 资源配置优化
- 在`docker-compose.yml`中添加资源限制（CPU、内存）
- 优化日志配置，限制日志文件大小和数量

## 预期收益

- **镜像体积减少**：预计从几百MB减少到约100MB以内
- **构建速度提升**：通过缓存和多阶段构建加速构建过程
- **运行时性能**：使用Alpine基础镜像，启动更快，内存占用更少
- **安全性提升**：减少攻击面，移除不必要的组件

## 使用说明

### 构建优化镜像
```bash
# 使用BuildKit加速构建
DOCKER_BUILDKIT=1 docker-compose build
```

### 运行优化后的应用
```bash
docker-compose up -d
```

## 进一步优化建议

1. **使用更小的基础镜像**：考虑使用`python:3.9-alpine`直接作为构建和运行环境
2. **精简Python依赖**：审查`requirements.txt`，移除不必要的依赖包
3. **使用distroless镜像**：对于生产环境，可以考虑使用Google的distroless镜像
4. **镜像层优化**：按照`COPY`不变文件、`RUN`安装依赖、`COPY`经常变化文件的顺序排列指令
5. **定期清理**：使用`docker system prune`定期清理未使用的镜像和容器

## 常见问题

### Alpine镜像兼容性问题
- Alpine使用musl libc而非glibc，部分Python包可能需要重新编译
- 解决方案：在构建阶段使用glibc兼容层或预编译二进制包

### 权限问题
- 确保挂载卷的权限设置正确，使用与容器内相同的用户ID
- 使用`docker exec -it icon-manager bash`检查容器内文件权限

### 性能监控
- 使用`docker stats`监控容器资源使用情况
- 使用`docker images`对比优化前后的镜像大小