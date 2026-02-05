---
name: frontend-optimize
description: 优化前端性能和用户体验。
---

# Frontend Optimize

优化前端性能和用户体验。

## When to Invoke

- 页面加载缓慢
- 交互卡顿
- 包体积过大
- 首屏时间过长
- SEO 优化

## Input Format

```yaml
project_type: "react_spa"
performance_metrics:
  fcp: "2.5s"  # First Contentful Paint
  lcp: "4.0s"  # Largest Contentful Paint
  tti: "5.0s"  # Time to Interactive
  cls: "0.1"   # Cumulative Layout Shift
budget:
  js_size: "200kb"
  css_size: "50kb"
```

## Output Format

```yaml
performance_report:
  current:
    fcp: "2.5s"
    lcp: "4.0s"
    tti: "5.0s"
    bundle_size: "350kb"
  
  issues:
    - "JavaScript 包体积过大"
    - "未使用的代码"
    - "图片未优化"
    - "缺少资源预加载"

optimization_plan:
  - priority: "high"
    action: "代码分割"
    impact: "减少 40% 初始加载"
    effort: "medium"
    
  - priority: "high"
    action: "图片优化"
    impact: "减少 30% 页面大小"
    effort: "low"
    
  - priority: "medium"
    action: "启用 Gzip/Brotli"
    impact: "减少 60% 传输大小"
    effort: "low"

webpack_config: |
  module.exports = {
    optimization: {
      splitChunks: {
        chunks: 'all',
        cacheGroups: {
          vendor: {
            test: /[\\/]node_modules[\\/]/,
            name: 'vendors',
            chunks: 'all'
          }
        }
      }
    }
  };

lighthouse_score:
  before:
    performance: 45
    accessibility: 80
    best_practices: 75
    seo: 70
  
  after:
    performance: 90
    accessibility: 95
    best_practices: 95
    seo: 90
```

## Examples

### Example 1: React 应用优化

**Input:** 单页应用加载慢

**Output:**
- 代码分割配置
- 懒加载实现
- 缓存策略
- 预加载关键资源

### Example 2: 静态站点优化

**Input:** 营销页面性能差

**输出：**
- 图片优化方案
- 关键 CSS 内联
- 字体加载优化
- CDN 配置

## Best Practices

1. **测量优先**: 使用 Lighthouse 等工具测量
2. **渐进优化**: 小步快跑，持续改进
3. **用户体验**: 关注核心 Web 指标
4. **监控持续**: 建立性能监控体系