## 修复计划

### 问题描述
[SearchView.vue](file:///c:/Users/24228/Desktop/smart_media/quark_strm/web/src/views/SearchView.vue) 中使用的 `searchApi` 对象和 `SearchResultItem` 类型在 [api/search.ts](file:///c:/Users/24228/Desktop/smart_media/quark_strm/web/src/api/search.ts) 中未导出，导致模块加载失败，页面无法打开。

### 修复步骤

**步骤1：修改 `quark_strm/web/src/api/search.ts`**
- 导出 `searchApi` 对象，包含 `search`、`searchFiltered`、`getStatus` 方法
- 导出 `SearchResultItem` 类型别名（指向 `SearchResult`）
- 保持现有导出函数的向后兼容

**步骤2：验证修复**
- 检查 TypeScript 类型检查
- 确认模块可以正确导入

### 修改文件清单
- `quark_strm/web/src/api/search.ts` - 添加 `searchApi` 对象和 `SearchResultItem` 类型导出

### Git锚点
修复前将记录当前commit hash，提供回滚方案