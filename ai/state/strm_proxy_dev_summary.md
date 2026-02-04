# STRM 与 Proxy 开发总结

## 📅 最后更新: 2026-02-04 15:32

---

## ✅ 已完成工作

### 阶段 1: STRM 生成器优化
- **文件**: `app/services/strm_generator.py`
- **变更**:
  - 添加 `StrmUrlMode` 类型（`redirect`/`stream`/`direct`）
  - 默认使用 `redirect` 模式（推荐）
  - STRM 内容格式: `http://host:8000/api/proxy/redirect/{file_id}?path={encoded_path}`
  - 附加 `path` 参数支持 WebDAV 兜底

### 阶段 2: 302 直链获取验证
- **API**: `GET /api/proxy/redirect/{file_id}`
- **状态**: ✅ 验证通过
- **测试文件**: `test_302_redirect.py`, `verify_strm_flow.py`, `verify_strm_url.py`

### 阶段 3: 统一直链解析器
- **新建文件**: `app/services/link_resolver.py`
- **功能**:
  - 支持 Quark API 直接获取（优先）
  - 支持 AList API 获取（备选）
  - 自动故障转移

### 阶段 4: WebDAV 兜底机制
- **新建文件**: `app/services/webdav_fallback.py`
- **功能**:
  - 302 失败时自动切换到 WebDAV
  - 基于 URL 中的 `path` 参数构造 WebDAV URL
  - 支持嵌入认证信息

### 阶段 5: Token 监控
- **新建文件**: `app/services/token_monitor.py`
- **功能**:
  - 定期检查 Cookie 有效性
  - 失效时记录日志（可扩展通知）

### 配置更新
- **文件**: `config.yaml`, `app/config/settings.py`, `app/core/config_manager.py`
- **新增配置项**:
  ```yaml
  alist:
    enabled: false
    url: "http://localhost:5244"
    token: ""
    mount_path: "/"

  webdav:
    enabled: false
    fallback_enabled: true
    url: "http://localhost:5244/dav"
    username: ""
    password: ""
    mount_path: "/"
  ```

### API 更新
- **文件**: `app/api/proxy.py`
- **变更**: 
  - `redirect_302` 现在接受 `path` 参数
  - 集成 `LinkResolver` 和 `WebDAVFallback`

---

## 🏗️ 系统架构

```
┌──────────────────────────────────────────────────────────────┐
│                         Emby/Plex                            │
│                    读取 .strm 文件                            │
└──────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌──────────────────────────────────────────────────────────────┐
│  STRM 文件内容:                                               │
│  http://host:8000/api/proxy/redirect/{fid}?path={path}       │
└──────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌──────────────────────────────────────────────────────────────┐
│              /api/proxy/redirect/{file_id}                   │
│                     (proxy.py)                               │
└──────────────────────────────────────────────────────────────┘
                              │
              ┌───────────────┼───────────────┐
              ▼               ▼               ▼
       ┌───────────┐   ┌───────────┐   ┌─────────────┐
       │  Quark    │   │  AList    │   │   WebDAV    │
       │   API     │   │   API     │   │  Fallback   │
       │ (优先)    │   │ (备选)    │   │  (兜底)     │
       └───────────┘   └───────────┘   └─────────────┘
              │               │               │
              └───────────────┴───────────────┘
                              │
                              ▼
                    302 重定向到直链
```

---

## 📋 待开发任务 (下一阶段)

### P1 - 高优先级

#### 1. AList 服务集成
- **描述**: 配置并测试 AList API 集成
- **前置**: 需要用户部署 AList 并挂载夸克网盘
- **验证**: 测试 `/api/fs/get` 直链获取

#### 2. WebDAV 兜底实测
- **描述**: 配置 WebDAV 并验证兜底播放
- **前置**: 需要 AList WebDAV 服务
- **验证**: 模拟 Quark API 失败，确认切换到 WebDAV

#### 3. Token 刷新增强
- **描述**: 研究夸克 Token 刷新机制
- **可能方案**:
  - 如果 Cookie 包含 refresh_token，实现自动刷新
  - 如果不支持，增加通知机制（Telegram/WeChat）
- **相关文件**: `token_monitor.py`

#### 4. 批量 STRM 生成 API
- **描述**: 完善 `/api/strm/scan` API
- **新增参数**: 
  - `base_url`: 代理服务器地址（内外网可能不同）
  - `strm_url_mode`: URL 模式选择
- **相关文件**: `app/api/strm.py`, `app/services/strm_service.py`

### P2 - 中优先级

#### 5. 前端 STRM 管理页面
- **描述**: 添加前端 UI 管理 STRM 生成任务
- **功能**:
  - 选择夸克目录
  - 配置输出路径
  - 查看生成进度
  - 查看生成历史

#### 6. Emby 集成测试
- **描述**: 完整 Emby 播放测试
- **验证点**:
  - STRM 文件识别
  - 302 重定向播放
  - 内外网访问

#### 7. 直链缓存优化
- **描述**: 优化 LinkCache 策略
- **现状**: `app/services/link_cache.py` 已存在
- **可优化**: 
  - 缓存命中率监控
  - 预热机制

### P3 - 低优先级

#### 8. 代理模式 (stream)
- **描述**: 测试并完善流代理模式
- **场景**: 部分播放器/网络环境不支持 302

#### 9. 转码链接支持
- **描述**: 完善 `/api/proxy/transcoding/{file_id}`
- **场景**: 原片格式不兼容时使用转码流

---

## 📁 关键文件清单

| 文件 | 功能 | 状态 |
|------|------|------|
| `app/services/strm_generator.py` | STRM 生成核心 | ✅ 已更新 |
| `app/services/link_resolver.py` | 直链解析器 | ✅ 新建 |
| `app/services/webdav_fallback.py` | WebDAV 兜底 | ✅ 新建 |
| `app/services/token_monitor.py` | Token 监控 | ✅ 新建 |
| `app/api/proxy.py` | 代理 API | ✅ 已更新 |
| `app/config/settings.py` | 配置模型 | ✅ 已更新 |
| `config.yaml` | 配置文件 | ✅ 已更新 |

---

## 🧪 测试脚本

| 脚本 | 用途 |
|------|------|
| `test_302_redirect.py` | 测试 302 重定向 API |
| `verify_strm_flow.py` | 测试 STRM 生成流程 |
| `verify_strm_url.py` | 验证 STRM URL 有效性 |

---

## 📝 Git 提交建议

```bash
git add -A
git commit -m "feat: STRM生成与多源直链解析

- 新增 LinkResolver 支持 Quark/AList 双引擎
- 新增 WebDAVFallback 兜底机制
- 新增 TokenMonitor 保活监控
- STRM URL 附加 path 参数支持兜底
- 更新 config.yaml 支持 alist/webdav 配置"
```

---

## 🚀 下次会话启动指令

新开会话后，可以直接说：

> 继续开发 STRM 和 Proxy 功能，请先阅读 `ai/state/strm_proxy_dev_summary.md` 了解进度，然后继续完成 P1 任务列表。

---

**作者**: Developer Agent  
**项目**: smart_media / quark_strm
