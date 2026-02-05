## Pansou 项目集成可行性分析

### 一、Pansou 项目架构概览

**技术栈**: Go + Gin 框架
**核心功能**:
- 80+ 搜索插件（TG频道、网页爬虫等）
- 并发搜索 + 智能排序
- 二级缓存（内存+磁盘）
- 多网盘类型自动识别分类
- JWT 认证（可选）

**API 接口**:
```
POST/GET /api/search    # 搜索接口
GET /api/health         # 健康检查
POST /api/auth/login    # 登录（可选）
```

---

### 二、现有 smart_media 搜索架构

**技术栈**: Python + FastAPI
**当前搜索功能**:
- `quark_strm/app/api/search.py` - 搜索API路由
- `quark_strm/app/services/search_service.py` - 搜索服务
- 依赖 `quark_api_package` 的 search SDK

---

### 三、集成可行性评估

| 维度 | 可行性 | 说明 |
|------|--------|------|
| **技术兼容性** | ⚠️ 中等 | Go vs Python，需要 HTTP API 调用 |
| **功能覆盖** | ✅ 高 | Pansou 功能更完善，插件丰富 |
| **集成复杂度** | ⚠️ 中等 | 需要部署 pansou 服务作为独立进程 |
| **维护成本** | ✅ 低 | Pansou 维护活跃，插件生态丰富 |

---

### 四、推荐集成方案

#### 方案 A: HTTP API 代理模式（推荐）

```
┌─────────────────┐      HTTP API      ┌─────────────────┐
│  smart_media    │  ───────────────►  │   pansou        │
│  (Python/FastAPI)│  ◄───────────────  │   (Go/Gin)      │
│                 │    JSON Response   │   :8888         │
└─────────────────┘                    └─────────────────┘
```

**实施步骤**:
1. 部署 pansou 服务（Docker 或独立运行）
2. 修改 `search_service.py` 调用 pansou API
3. 删除原有的三个搜索页面，统一使用 pansou 的搜索结果
4. 前端页面调用 smart_media 的搜索 API，后端转发到 pansou

**优点**:
- 松耦合，pansou 独立升级不影响主项目
- 保留现有 smart_media 的 API 接口不变
- 可以利用 pansou 的 80+ 插件

**缺点**:
- 多一个服务进程
- 网络调用有轻微延迟

---

#### 方案 B: 代码级集成（不推荐）

将 pansou 的 Go 代码改写为 Python 并集成到项目中。

**缺点**:
- 工作量巨大（80+ 插件需要重写）
- 失去 pansou 的更新支持
- 维护困难

---

### 五、具体实施建议

建议采用 **方案 A**，具体步骤：

1. **部署 pansou 服务**
   ```bash
   docker run -d --name pansou -p 8888:8888 ghcr.io/fish2018/pansou:latest
   ```

2. **修改搜索服务** (`search_service.py`)
   - 将 SDK 调用改为 HTTP 调用 pansou API
   - 保持现有 API 接口不变，前端无需改动

3. **删除原有搜索页**
   - 删除 `quark_api_package/packages/search/` 下的搜索实现
   - 保留 API 路由层，只替换底层实现

4. **前端适配（可选）**
   - 可以利用 pansou 的 `merged_by_type` 返回格式，直接按网盘类型分组展示

---

### 六、结论

**可行！** 推荐将 pansou 作为独立的搜索服务集成到项目中：

- ✅ Pansou 功能完善，插件丰富（80+）
- ✅ 通过 HTTP API 调用，集成简单
- ✅ 可以删除原有的三个搜索页，统一使用 pansou
- ✅ 保留现有 API 接口，前端改动最小

是否继续制定详细的集成实施计划？