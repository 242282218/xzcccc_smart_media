---
description: 配置持续集成和持续部署流水线
---

# CI/CD Config Workflow

来源 Skill: `.trae/skills/ci-cd-config/SKILL.md`

## 使用场景

- 新项目搭建 CI/CD
- 迁移 CI 平台
- 优化构建时间
- 设置自动化测试
- 配置部署策略

## 执行步骤

1. **确定 CI 平台**
   - GitHub Actions
   - GitLab CI
   - Jenkins

2. **设计流水线阶段**
   - build
   - test
   - security_scan
   - deploy_staging
   - deploy_production

3. **配置触发条件**
   - push 触发
   - PR 触发
   - 定时触发

4. **配置环境变量与密钥**
   - 使用 secrets 管理敏感信息
   - 配置环境变量

5. **验证流水线**
   - 触发测试运行
   - 检查各阶段日志
   - 确认部署结果

## 最佳实践

1. **快速反馈**: 快速阶段优先执行
2. **并行执行**: 独立的任务并行运行
3. **缓存优化**: 缓存依赖和构建产物
4. **安全凭证**: 使用 secrets 管理敏感信息
