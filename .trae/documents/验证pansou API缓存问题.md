## 问题分析

根据 PANSOU_API_DOC.md 文档，搜索API支持 `refresh` 参数强制刷新缓存。

当前问题：
- 搜索任何关键词都返回 5130 条结果
- 结果完全不相关
- 可能是缓存导致

## 验证方案

1. 修改请求添加 `refresh: true` 参数
2. 测试搜索"流浪地球"看是否返回正确结果
3. 如果正常，说明是缓存问题

## 修改文件

`quark_strm/app/services/search_service.py`:
- 在搜索参数中添加 `"refresh": True`

请确认是否执行？