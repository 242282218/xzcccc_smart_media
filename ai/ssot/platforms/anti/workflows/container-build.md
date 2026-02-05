---
description: 构建优化的容器镜像
---

# Container Build Workflow

来源 Skill: `.trae/skills/container-build/SKILL.md`

## 使用场景

- 应用容器化
- 优化现有镜像
- 设置多阶段构建
- 配置容器编排
- 安全加固

## 执行步骤

1. **创建 Dockerfile**
   - 选择基础镜像（slim/alpine）
   - 设置多阶段构建
   - 配置非 root 用户

2. **创建 .dockerignore**
   - 排除不需要的文件
   - 减少构建上下文

3. **配置 Docker Compose**
   - 定义服务
   - 配置网络
   - 设置卷挂载

4. **安全检查**
   - 使用非 root 用户运行
   - 扫描镜像漏洞
   - 更新基础镜像

5. **构建并验证**
   - 构建镜像
   - 运行容器
   - 验证功能

## 最佳实践

1. **多阶段构建**: 分离编译和运行环境
2. **最小基础镜像**: 使用 alpine 或 slim 版本
3. **层缓存**: 合理利用 Docker 层缓存
4. **安全扫描**: 集成镜像安全扫描
