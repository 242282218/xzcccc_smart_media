---
description: 设计和实现高质量的 Vue 组件
---

# Vue Component Workflow

来源 Skill: `.trae/skills/vue-component/SKILL.md`

## 使用场景

- 开发新组件
- 重构现有组件
- 优化组件性能
- 设计组件库
- 代码审查

## 执行步骤

1. **设计组件接口**
   - 定义 Props（TypeScript 类型）
   - 定义 Emits 事件

2. **实现组件**
   - 使用 Composition API
   - 管理响应式状态
   - 处理事件

3. **添加样式**
   - 使用 scoped CSS
   - 响应式设计

4. **编写测试**
   - 使用 Vitest + Vue Test Utils
   - 渲染测试
   - 事件测试

## 最佳实践

1. **组合式 API**: 优先使用 Composition API
2. **TypeScript**: 使用类型安全的 Props/Emits
3. **样式作用域**: 使用 scoped CSS
4. **性能优化**: 使用 v-memo、computed
