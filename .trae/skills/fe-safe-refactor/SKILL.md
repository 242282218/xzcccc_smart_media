---
name: fe-safe-refactor
description: "# When To Use
需要优化前端代码结构，但必须保证 UI 与行为完全一致时。"
---

# Description
前端安全重构模式，不改变任何渲染结果与交互行为。

# Instructions
在保证行为一致的前提下进行结构优化。

## Allowed
- 拆分组件
- 抽取 hooks
- 重命名（语义等价）

# Output Contract
- 修改文件列表
- 行为不变说明

# Forbidden
- 不改变 UI
- 不改变交互
- 不引入新设计