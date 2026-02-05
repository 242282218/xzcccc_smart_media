---
name: fe-read-only
description: "# When To Use
当需要理解前端项目整体结构、技术栈、页面与组件关系，
且不希望 AI 对代码产生任何修改时。"
---

# Description
前端只读分析模式。
仅用于理解与确认，不进行任何改动。

# Instructions
只允许分析现有代码与配置。

## Analysis Scope
- 技术栈（React / Vue / Next / Vite 等）
- 页面与路由结构
- 组件组织方式
- 构建与启动方式

# Output Contract
- 技术栈概览
- 页面 / 路由结构
- 主要组件职责

# Forbidden
- 不修改代码
- 不提出重构或优化建议
- 不执行命令