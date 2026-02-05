---
description: 前端状态追踪，分析状态来源与更新路径
---

# Frontend State Trace Workflow

来源 Skill: `.trae/skills/fe-state-trace/SKILL.md`

## 使用场景

- 涉及 useState / Redux / Pinia / Zustand / Context 等状态问题时

## 执行步骤

1. **定位状态定义位置**
   - 找到状态声明
   - 确定状态类型

2. **追踪状态更新触发点**
   - 哪些操作会更新状态
   - 更新的时机和条件

3. **分析状态使用组件**
   - 哪些组件消费该状态
   - 状态在组件间的传递方式

4. **输出分析报告**
   - 状态来源
   - 更新路径
   - 使用位置

## 禁止事项

- 不修改状态代码
- 不重构状态结构
