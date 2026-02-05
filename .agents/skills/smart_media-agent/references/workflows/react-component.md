---
description: 设计和实现高质量的 React 组件
---

# React Component Workflow

来源 Skill: `.trae/skills/react-component/SKILL.md`

## 使用场景

- 开发新组件
- 重构现有组件
- 优化组件性能
- 设计组件库
- 代码审查

## 执行步骤

1. **设计组件接口**
   - 定义 Props 类型
   - 确定组件职责

2. **实现组件**
   - 编写组件代码
   - 管理状态
   - 处理事件

3. **添加样式**
   - CSS Modules 或 Styled Components
   - 响应式设计

4. **编写测试**
   - 渲染测试
   - 交互测试
   - 快照测试

5. **创建 Storybook 故事**（可选）
   - 展示不同状态
   - 文档化 Props

## 最佳实践

1. **单一职责**: 每个组件只做一件事
2. **Props 明确**: 清晰的 Props 类型定义
3. **状态提升**: 合理的状态管理
4. **性能优化**: 使用 memo、useMemo、useCallback
