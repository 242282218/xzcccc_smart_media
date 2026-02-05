---
name: fe-state-trace
description: "# When To Use
涉及 useState / Redux / Pinia / Zustand / Context 等状态问题时。"
---

# Description
用于追踪前端状态的来源、更新路径与消费位置。

# Instructions
分析状态生命周期，不改动状态逻辑。

## Analysis Scope
- 状态定义位置
- 状态更新触发点
- 状态使用组件

# Output Contract
- 状态来源
- 更新路径
- 使用位置

# Forbidden
- 不修改状态代码
- 不重构状态结构