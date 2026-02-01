# Pansou 搜索服务集成说明

## 概述

已成功将 pansou 项目集成到 smart_media 中，替代原有的三个搜索源（telegram、net_search、quark_api）。

## 架构变更

### 集成前
```
smart_media
├── quark_api_package/packages/search/
│   ├── sources/telegram.py      # TG搜索
│   ├── sources/net_search.py    # 网络搜索
│   ├── sources/quark_api.py     # 夸克API搜索
│   └── ...
```

### 集成后
```
smart_media
├── pansou-reference/            # pansou参考代码（Go）
├── quark_strm/app/services/
│   └── search_service.py        # 调用pansou HTTP API
└── quark_api_package/packages/search/  # 已弃用，保留兼容性
```

## 使用方式

### 1. 启动 pansou 服务

**方式一：Docker（推荐）**
```bash
docker run -d --name pansou -p 8888:8888 ghcr.io/fish2018/pansou:latest
```

**方式二：源码运行**
```bash
cd pansou-reference
go mod tidy
go run main.go
```

### 2. 配置环境变量

在运行 smart_media 前设置：
```bash
# Windows PowerShell
$env:PANSOU_API_URL="http://localhost:8888"

# Windows CMD
set PANSOU_API_URL=http://localhost:8888

# Linux/Mac
export PANSOU_API_URL=http://localhost:8888
```

### 3. API 接口

搜索接口保持不变：
```
GET /api/search?keyword=电影名&cloud_types=quark,baidu
GET /api/search/filtered?keyword=电影名&min_score=0.8
GET /api/search/status
```

## Pansou 优势

| 功能 | 原搜索 | Pansou |
|------|--------|--------|
| 搜索源数量 | 3个 | 80+个插件 |
| 网盘支持 | 夸克 | 百度、阿里、夸克、天翼、UC、115等 |
| 并发搜索 | 支持 | 支持（工作池设计） |
| 智能排序 | 基础评分 | 多维度综合排序 |
| 缓存机制 | 简单缓存 | 二级缓存（内存+磁盘） |
| 异步插件 | 不支持 | 支持 |

## 文件变更清单

### 修改的文件
1. `quark_strm/app/services/search_service.py` - 改为调用pansou HTTP API
2. `quark_api_package/packages/search/__init__.py` - 添加迁移说明
3. `quark_api_package/packages/search/sources/base.py` - 标记弃用
4. `quark_api_package/packages/search/sources/manager.py` - 标记弃用
5. `quark_api_package/packages/search/core/service.py` - 标记弃用

### 删除的文件
1. `quark_api_package/packages/search/sources/telegram.py`
2. `quark_api_package/packages/search/sources/net_search.py`
3. `quark_api_package/packages/search/sources/quark_api.py`

### 新增的文件
1. `pansou-reference/` - pansou参考代码
2. `PANSOU_INTEGRATION.md` - 本文档

## 注意事项

1. **依赖项**：需要安装 `httpx` 库（已用于其他功能）
2. **服务依赖**：pansou服务必须独立运行
3. **网络要求**：确保能访问 pansou 服务地址
4. **兼容性**：原有API接口完全兼容，前端无需改动

## 故障排查

### 问题：搜索返回 "pansou服务未启动"
**解决**：检查 pansou 服务是否运行，以及 PANSOU_API_URL 配置是否正确

### 问题：搜索结果为空
**解决**：pansou默认只启用部分插件，可通过环境变量配置启用更多插件

### 问题：网络超时
**解决**：调整超时时间或检查网络连接

## 参考链接

- Pansou GitHub: https://github.com/242282218/pansou
- API文档: 见 pansou-reference/docs/
