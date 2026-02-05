---
description: 生成前端组件结构认知图，理清组件组成
---

# Frontend Component Map Workflow

来源 Skill: `.trae/skills/fe-component-map/SKILL.md`

## 使用场景

- 需要搞清楚某个页面或功能由哪些组件组成时

## 执行步骤

1. **识别页面入口组件**
   - 找到页面路由入口
   - 确定主组件

2. **分析子组件拆分**
   - 列出所有子组件
   - 确定组件层级关系

3. **明确组件职责边界**
   - 每个组件的功能说明
   - Props 和 Events 接口

4. **输出组件树**
   ```
   页面 → 组件树
   ├── HeaderComponent (负责导航)
   ├── MainContent (负责内容展示)
   │   ├── Sidebar
   │   └── ContentArea
   └── FooterComponent
   ```

## 禁止事项

- 不修改组件代码
- 不调整组件结构
