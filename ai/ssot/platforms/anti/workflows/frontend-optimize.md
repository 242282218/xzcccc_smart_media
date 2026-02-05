---
description: 优化前端性能和用户体验
---

# Frontend Optimize Workflow

来源 Skill: `.trae/skills/frontend-optimize/SKILL.md`

## 使用场景

- 页面加载缓慢
- 交互卡顿
- 包体积过大
- 首屏时间过长
- SEO 优化

## 执行步骤

1. **性能测量**
   - 使用 Lighthouse 等工具测量
   - 记录核心 Web 指标（FCP, LCP, TTI, CLS）

2. **问题分析**
   - JavaScript 包体积
   - 未使用的代码
   - 图片未优化
   - 缺少资源预加载

3. **制定优化计划**
   - 代码分割
   - 图片优化
   - 启用 Gzip/Brotli
   - 配置缓存策略

4. **实施优化**
   - 配置 webpack/vite
   - 实现懒加载
   - 优化关键渲染路径

5. **验证效果**
   - 重新测量
   - 对比优化前后

## 最佳实践

1. **测量优先**: 使用 Lighthouse 等工具测量
2. **渐进优化**: 小步快跑，持续改进
3. **用户体验**: 关注核心 Web 指标
4. **监控持续**: 建立性能监控体系
