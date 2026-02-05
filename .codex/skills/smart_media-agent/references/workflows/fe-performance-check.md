---
description: 前端性能分析，定位性能瓶颈
---

# Frontend Performance Check Workflow

来源 Skill: `.trae/skills/fe-performance-check/SKILL.md`

## 使用场景

- 页面性能差
- 渲染慢
- 包体积过大

## 执行步骤

1. **分析重渲染问题**
   - 检查 React/Vue 组件渲染次数
   - 识别不必要的重渲染

2. **分析包体积**
   - 检查 bundle 大小
   - 识别大包来源
   - 分析 tree-shaking 效果

3. **检查可疑副作用**
   - useEffect 依赖检查
   - 事件监听器清理
   - 内存泄漏检测

4. **输出分析报告**
   - 重渲染点列表
   - 大包来源说明
   - 可疑副作用列表

## 禁止事项

- 不直接改代码（仅分析）
