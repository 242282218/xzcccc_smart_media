# quark_api_package 集成开发计划

## 目标
将 `C:\Users\24228\Desktop\smart_media\quark_api_package\packages` 下的所有包（quark_sdk、search、rename）集成到 quark_strm 项目中，开发新功能。

## 集成内容

### 1. quark_sdk 包集成
- **功能**: 夸克网盘SDK，提供文件管理、分享、转存等功能
- **集成方式**: 替换现有 `quark_api_client_v2.py` 实现
- **新增API**:
  - `POST /api/quark-sdk/share` - 创建分享
  - `POST /api/quark-sdk/transfer` - 转存文件

### 2. search 包集成
- **功能**: 资源搜索，支持Telegram、夸克API、网络搜索
- **集成方式**: 新增搜索服务模块
- **新增API**:
  - `GET /api/search` - 搜索资源

### 3. rename 包集成
- **功能**: 媒体文件智能重命名，支持TMDB匹配和AI辅助
- **集成方式**: 新增重命名服务模块
- **新增API**:
  - `POST /api/rename/preview` - 预览重命名
  - `POST /api/rename/execute` - 执行重命名

## 执行步骤

### Phase 1: 环境准备
1. 更新 `requirements.txt` 添加SDK依赖
2. 创建 `app/core/sdk_config.py` SDK配置模块
3. 更新 `config.yaml` 添加新配置项

### Phase 2: 后端开发
1. 创建 `app/services/quark_sdk_service.py` - SDK服务封装
2. 创建 `app/services/search_service.py` - 搜索服务
3. 创建 `app/services/rename_service.py` - 重命名服务
4. 创建 `app/api/quark_sdk.py` - SDK版夸克API路由
5. 创建 `app/api/search.py` - 搜索API路由
6. 创建 `app/api/rename.py` - 重命名API路由
7. 更新 `app/main.py` 注册新路由

### Phase 3: 前端开发
1. 创建 `web/src/api/quarkSdk.ts` - SDK版API封装
2. 创建 `web/src/api/search.ts` - 搜索API封装
3. 创建 `web/src/api/rename.ts` - 重命名API封装
4. 创建搜索页面组件
5. 创建重命名页面组件

### Phase 4: 测试
1. 后端API单元测试
2. 前端组件测试
3. 集成测试

## 需要确认的信息

1. **API密钥**: 是否需要配置TMDB API密钥和AI API密钥？
2. **Cookie格式**: 当前Cookie格式是否与SDK兼容？
3. **搜索源配置**: Telegram频道配置是否需要？
4. **测试账号**: 是否有测试用的夸克账号？

## 回滚方案
- 所有改动在独立分支进行
- 保留原有实现作为fallback
- 通过feature flag控制新功能启用

请确认后开始执行。