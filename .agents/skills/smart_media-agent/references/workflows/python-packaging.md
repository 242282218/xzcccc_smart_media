---
description: 打包和发布 Python 项目
---

# Python Packaging Workflow

来源 Skill: `.trae/skills/python-packaging/SKILL.md`

## 使用场景

- 创建可安装的包
- 发布到 PyPI
- 设置开发环境
- 管理项目依赖
- 版本发布

## 执行步骤

1. **选择构建工具**
   - Poetry（推荐）
   - setuptools
   - flit

2. **配置项目**
   - 创建 pyproject.toml
   - 设置元数据
   - 定义依赖

3. **准备发布**
   - README.md 完整
   - LICENSE 文件存在
   - 版本号已更新
   - 测试通过
   - CHANGELOG 已更新

4. **构建和发布**
   - 执行构建
   - 发布到 PyPI
   - 验证安装

## 最佳实践

1. **语义化版本**: 遵循 SemVer 规范
2. **明确依赖**: 指定版本范围
3. **包含测试**: 发布前运行测试
4. **文档完整**: README 和文档齐全
