---
name: python-packaging
description: 打包和发布 Python 项目。
---

# Python Packaging

打包和发布 Python 项目。

## When to Invoke

- 创建可安装的包
- 发布到 PyPI
- 设置开发环境
- 管理项目依赖
- 版本发布

## Input Format

```yaml
project_path: "./myproject"
package_name: "my-awesome-package"
build_tool: "poetry"
```

## Output Format

```yaml
setup_config: |
  [build-system]
  requires = ["poetry-core>=1.0.0"]
  build-backend = "poetry.core.masonry.api"
  
  [tool.poetry]
  name = "my-awesome-package"
  version = "0.1.0"
  description = "A awesome package"
  authors = ["Your Name <you@example.com>"]
  readme = "README.md"
  license = "MIT"
  
  [tool.poetry.dependencies]
  python = "^3.9"
  requests = "^2.28.0"
  
  [tool.poetry.group.dev.dependencies]
  pytest = "^7.0"
  black = "^22.0"
  
  [tool.poetry.scripts]
  my-cli = "my_package.cli:main"

build_script: |
  #!/bin/bash
  # 构建和发布
  poetry build
  poetry publish

publish_guide:
  - "注册 PyPI 账号"
  - "配置 API Token"
  - "运行 poetry publish"
  - "验证包安装"

check_list:
  - "README.md 完整"
  - "LICENSE 文件存在"
  - "版本号已更新"
  - "测试通过"
  - "CHANGELOG 已更新"
```

## Examples

### Example 1: 库包

**Input:** 工具库

**Output:**
- pyproject.toml 配置
- 入口点定义
- 依赖管理
- 发布流程

### Example 2: 应用包

**Input:** CLI 工具

**Output:**
- 控制台脚本配置
- 数据文件包含
- 平台特定配置
- 安装指南

## Best Practices

1. **语义化版本**: 遵循 SemVer 规范
2. **明确依赖**: 指定版本范围
3. **包含测试**: 发布前运行测试
4. **文档完整**: README 和文档齐全