# 修复 SDK 配置导入警告

## 问题分析

**错误信息：**
```
SearchService导入失败: cannot import name 'SearchService' from 'packages.search.core.service'
SourceManager导入失败: cannot import name 'SourceManager' from 'packages.search.sources.manager'
```

**根本原因：**
- `packages.search.core.service` 和 `packages.search.sources.manager` 模块已被弃用
- 这些模块现在只包含注释说明，没有实际的类定义
- 功能已迁移到 pansou HTTP API 服务

## 修复方案

### 方案：移除对已弃用模块的导入

由于这些模块已被弃用且功能由 pansou 服务替代，应该：

1. **移除导入语句**：删除对 `SearchService` 和 `SourceManager` 的导入尝试
2. **更新 `create_search_service()` 方法**：直接返回 `None` 或调用新的 pansou 服务
3. **清理相关代码**：移除不再使用的搜索服务创建逻辑

## 修改文件

**文件**: `app/core/sdk_config.py`

### 修改内容

1. 移除以下导入尝试：
   ```python
   try:
       from packages.search.core.service import SearchService
   except ImportError as e:
       logger.warning(f"SearchService导入失败: {e}")
       SearchService = None
   
   try:
       from packages.search.sources.manager import SourceManager
   except ImportError as e:
       logger.warning(f"SourceManager导入失败: {e}")
       SourceManager = None
   ```

2. 更新 `create_search_service()` 方法：
   - 直接返回 `None`
   - 或记录日志说明搜索服务已迁移到 pansou

3. 移除 `ScoringEngine` 和 `CacheManager` 的导入（如果也被弃用）

## 验证步骤

1. 重启应用
2. 检查日志，确认不再有导入警告
3. 验证搜索功能通过 pansou 服务正常工作

## 回滚方案

```bash
git reset --hard <commit hash>
```