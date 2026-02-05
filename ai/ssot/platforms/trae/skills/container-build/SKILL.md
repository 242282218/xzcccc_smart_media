---
name: container-build
description: "application_type: \"python_fastapi\""
---

# Container Build

构建优化的容器镜像。

## When to Invoke

- 应用容器化
- 优化现有镜像
- 设置多阶段构建
- 配置容器编排
- 安全加固

## Input Format

```yaml
application_type: "python_fastapi"
base_image: "python:3.11-slim"
optimization_goal: "最小镜像大小"
```

## Output Format

```yaml
dockerfile: |
  # 多阶段构建
  FROM python:3.11-slim as builder
  
  WORKDIR /app
  COPY requirements.txt .
  RUN pip install --user -r requirements.txt
  
  FROM python:3.11-slim
  
  # 创建非 root 用户
  RUN useradd -m -u 1000 appuser
  
  WORKDIR /app
  
  # 从 builder 复制依赖
  COPY --from=builder /root/.local /home/appuser/.local
  COPY --chown=appuser:appuser . .
  
  USER appuser
  
  ENV PATH=/home/appuser/.local/bin:$PATH
  
  EXPOSE 8000
  
  CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]

docker_compose: |
  version: '3.8'
  services:
    app:
      build: .
      ports:
        - "8000:8000"
      environment:
        - DATABASE_URL=postgresql://db:5432/app
      depends_on:
        - db
    
    db:
      image: postgres:15
      environment:
        POSTGRES_DB: app
        POSTGRES_USER: user
        POSTGRES_PASSWORD: password

optimization_tips:
  - "使用 .dockerignore 排除不需要的文件"
  - "合并 RUN 命令减少层数"
  - "使用特定版本标签而非 latest"
  - "清理缓存和临时文件"

security_checklist:
  - "使用非 root 用户运行"
  - "定期更新基础镜像"
  - "扫描镜像漏洞"
  - "不暴露不必要的端口"
```

## Examples

### Example 1: Python 应用

**Input:** FastAPI 应用

**Output:**
- 多阶段构建 Dockerfile
- 依赖缓存优化
- 非 root 用户配置
- Docker Compose 配置

### Example 2: C 应用

**Input:** C 服务

**Output:**
- 编译阶段
- 运行时阶段
- 静态链接优化
- 最小镜像

## Best Practices

1. **多阶段构建**: 分离编译和运行环境
2. **最小基础镜像**: 使用 alpine 或 slim 版本
3. **层缓存**: 合理利用 Docker 层缓存
4. **安全扫描**: 集成镜像安全扫描