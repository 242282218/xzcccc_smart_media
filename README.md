# Smart Media - 夸克网盘 STRM 媒体管理系统

<div align="center">

[![Python](https://img.shields.io/badge/Python-3.10+-blue.svg)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.100+-green.svg)](https://fastapi.tiangolo.com/)
[![Vue](https://img.shields.io/badge/Vue-3.5+-brightgreen.svg)](https://vuejs.org/)
[![Docker](https://img.shields.io/badge/Docker-Ready-blue.svg)](https://www.docker.com/)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

**让云盘视频像本地文件一样在 Emby/Jellyfin 中流畅播放**

[功能特性](#-功能特性) • [快速开始](#-快速开始) • [架构设计](#-架构设计) • [API 文档](#-api-文档) • [开发指南](#-开发指南)

</div>

---

## 📖 项目简介

**Smart Media** (又名 `quark_strm`) 是一个基于 **夸克网盘** 的智能媒体管理系统，核心目标是通过生成 **.strm 文件** 实现 Emby/Jellyfin 媒体服务器对云盘视频的直接播放，同时提供智能重命名、文件管理、通知推送等增强功能。

### 核心价值

- 🎬 **云盘直连**: 将夸克网盘视频生成 STRM 文件，Emby/Jellyfin 可直接播放
- 🤖 **智能重命名**: AI 驱动的文件名解析，自动匹配 TMDB 元数据
- 🔄 **自动同步**: 云盘文件变更自动触发 Emby 媒体库刷新
- 📬 **通知推送**: 支持 Telegram、微信等多种通知渠道
- 🛡️ **安全可靠**: API Key 认证、敏感数据加密、日志脱敏
- 🚀 **高性能**: 多级缓存 (L1/L2/L3)、异步并发、连接池优化

### 技术栈

**后端**:
- Python 3.10+ / FastAPI 0.100+ / SQLAlchemy 2.0+
- SQLite / Redis (可选) / APScheduler
- aiohttp / httpx / Pydantic 2.0+

**前端**:
- Vue 3.5+ / TypeScript 5.9+ / Vite 7.3+
- Element Plus 2.13+ / Pinia 3.0+ / Vue Router 4.6+
- ECharts 6.0+ / Axios 1.13+

**部署**:
- Docker / Docker Compose
- GitHub Actions CI/CD

---

## ✨ 功能特性

### 核心功能

| 功能模块 | 描述 | 状态 |
|---------|------|------|
| **夸克网盘接入** | 文件浏览、直链获取、Cookie 自动维护 | ✅ 完成 |
| **STRM 文件生成** | 递归扫描、增量更新、有效性校验 | ✅ 完成 |
| **播放网关** | 302 重定向、Range 请求代理、直链缓存 | ✅ 完成 |
| **智能重命名** | AI 解析、TMDB 匹配、Emby 规范命名 | ✅ 完成 |
| **Emby 集成** | 媒体库刷新、事件监听、定时任务 | ✅ 完成 |
| **文件管理** | 本地/云盘双存储、文件操作 | ✅ 完成 |
| **通知推送** | Telegram、微信、事件订阅 | ✅ 完成 |
| **系统管理** | 配置管理、任务调度、监控指标 | ✅ 完成 |

### 技术亮点

- 🎯 **多 AI 提供商故障转移**: GLM (智谱) / DeepSeek / Kimi 自动切换
- 💾 **分级缓存系统**: L1(内存) → L2(磁盘) → L3(Redis)
- 🔥 **配置热加载**: 文件监控 + 原子性保存 + 回滚机制
- 🧠 **智能重命名算法**: 本地算法 + AI 增强混合模式
- 🎭 **Emby 深度集成**: 自动刷新、Webhook、播放统计
- 🌐 **WebDAV 兜底**: 直链失效时自动切换 WebDAV 播放
- 🔐 **全链路安全**: API Key 认证、加密存储、日志脱敏、路径安全

---

## 🚀 快速开始

### 方式一：Docker 部署 (推荐)

#### 1. 准备配置文件

```bash
# 复制配置模板
cp config.example.yaml config.yaml

# 编辑配置文件，填入必要参数
# - 夸克网盘 Cookie
# - TMDB API Key
# - Emby URL 和 API Key (可选)
# - Telegram/微信通知配置 (可选)
```

#### 2. 启动服务

```bash
docker compose pull && docker compose up -d
```

#### 3. 验证安装

```bash
# 检查健康状态
curl http://localhost:8000/health

# 查看日志
docker compose logs -f
```

如已配置 Emby 代理基址（`emby.proxy_base_url`），可额外验证专用代理入口：

```bash
# 访问 Emby 专用代理入口（默认 18097）
curl -I http://localhost:18097
```

#### 4. 访问前端

浏览器打开：`http://localhost:3000`

如需让 Emby 走 Smart Media 专用代理入口，使用：`http://localhost:18097`

默认登录凭据 (开发环境):
- 用户名：`admin`
- 密码：`admin`

### 方式二：本地开发部署

#### 前置要求

- Python 3.10+
- Node.js 20+
- Git

#### 1. 克隆项目

```bash
git clone <repository-url>
cd smart_media
```

#### 2. 安装后端依赖

```bash
cd quark_strm
pip install -r requirements.txt
```

#### 3. 安装前端依赖

```bash
cd web
npm install
```

#### 4. 准备配置文件

```bash
# 复制并编辑配置
cp config.example.yaml config.yaml

# 复制环境变量示例
cp ../config/.env.example ../config/.env
```

#### 5. 启动后端服务

```bash
cd quark_strm
python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8001
```

#### 6. 启动前端开发服务器

```bash
cd quark_strm/web
# 如果本机 3000 端口已被占用（如博客项目），建议固定使用 18099
npm run dev -- --port 18099
```

#### 7. 访问应用

- 前端开发服务器：`http://localhost:18099`
- 后端 API: `http://localhost:8001`
- API 文档：`http://localhost:8001/docs`
- Emby 专用代理入口：`http://localhost:18097`（用于 PlaybackInfo Hook 与播放链路代理）

#### 8. 端口规划

| 端口 | 用途 |
|------|------|
| `3000` | 前端开发服务器默认端口（可选） |
| `18099` | 前端开发服务器推荐端口（本地 3000 冲突场景） |
| `8001` | Smart Media API / Web 管理入口（本地开发） |
| `18097` | Emby 专用代理入口（建议配置给 Emby 的 `proxy_base_url`） |

#### 9. Emby 专用代理入口（18097）使用说明

1. 在 `config.yaml` 中配置：
   - `emby.url`: 上游 Emby 地址（例如 `http://192.168.100.66:18096`）
   - `emby.proxy_base_url`: Smart Media 代理入口（例如 `http://127.0.0.1:18097`）
2. 访问 `http://127.0.0.1:18097` 应直接显示 Emby 页面（登录、浏览、播放走同一入口）。
3. 播放链路策略：
   - 优先 302 重定向到可播放直链
   - 302 不可用时自动回退到服务端转发代理（stream）
4. 透明代理约束（已修复）：
   - 18097 不再注入会影响 Emby Web 的 CSRF/CSP 头
   - 保留上游多值 `Set-Cookie`，避免登录态丢失
   - 过滤冲突响应头，避免 `Content-Length/Encoding` 导致的回包异常

#### 10. 18097 登录报错排查

若出现“登录出错 / 处理请求时出错”，按顺序检查：
1. 确认当前版本包含 `v2026.03.14-emby-proxy-hotfix1`（见更新日志）。
2. 使用无痕窗口或清理站点缓存后重试（包含 Service Worker）。
3. 对照日志：
   - `quark_strm/logs/runtime/proxy_18097.out.log`
   - `quark_strm/logs/runtime/proxy_18097.err.log`
4. 重点看登录请求：`POST /emby/Users/authenticatebyname`
   - `200`/`401` 属于上游认证结果
   - 若出现 `RuntimeError`/`Traceback` 再按日志继续修复

---

## 🏗️ 架构设计

### 系统架构图

```
┌─────────────────────────────────────────────────────┐
│                  Smart Media 系统                    │
├─────────────────────────────────────────────────────┤
│  ┌──────────────┐  ┌──────────────┐  ┌───────────┐ │
│  │  夸克接入层  │  │  STRM 生成层  │  │ 播放网关层│ │
│  │  - 文件浏览  │  │  - 目录扫描  │  │  - 代理  │ │
│  │  - 直链获取  │  │  - STRM 生成  │  │  - 302   │ │
│  │  - 重命名    │  │  - 增量更新  │  │  - Range │ │
│  └──────────────┘  └──────────────┘  └───────────┘ │
│  ┌──────────────┐  ┌──────────────┐  ┌───────────┐ │
│  │  智能重命名  │  │  通知推送    │  │  系统管理 │ │
│  │  - TMDB 匹配  │  │  - Telegram │  │  - 配置  │ │
│  │  - 预览      │  │  - 微信      │  │  - 监控  │ │
│  │  - 批量执行  │  │  - 事件订阅  │  │  - 日志  │ │
│  └──────────────┘  └──────────────┘  └───────────┘ │
└─────────────────────────────────────────────────────┘
```

### 技术架构层次

```
┌─────────────────┐
│   API Layer     │  # FastAPI 路由 (20+ 个路由模块)
├─────────────────┤
│  Service Layer  │  # 业务逻辑 (40+ 个服务类)
├─────────────────┤
│   Data Layer    │  # SQLAlchemy + Pydantic
├─────────────────┤
│  Core Layer     │  # 配置、日志、异常、安全
└─────────────────┘
```

### 核心服务

| 服务 | 文件 | 描述 |
|------|------|------|
| **QuarkService** | [`quark_service.py`](quark_strm/app/services/quark_service.py) | 夸克网盘操作封装 |
| **StrmService** | [`strm_service.py`](quark_strm/app/services/strm_service.py) | STRM 文件生成和管理 |
| **EmbyService** | [`emby_service.py`](quark_strm/app/services/emby_service.py) | Emby 媒体服务器集成 |
| **SmartRenameService** | [`smart_rename_service.py`](quark_strm/app/services/smart_rename_service.py) | 智能重命名核心服务 |
| **AIParserService** | [`ai_parser_service.py`](quark_strm/app/services/ai_parser_service.py) | AI 文件解析服务 |
| **NotificationService** | [`notification_service.py`](quark_strm/app/services/notification_service.py) | 统一通知服务 |
| **CronService** | [`cron_service.py`](quark_strm/app/services/cron_service.py) | 定时任务调度 |
| **TieredCache** | [`tiered_cache.py`](quark_strm/app/services/tiered_cache.py) | 分级缓存系统 |

### 数据模型

**SQLite 数据库** (`quark_strm.db`):

- `strm`: STRM 文件记录
- `records`: 扫描记录
- `emby_libraries`: Emby 媒体库
- `emby_media_items`: Emby 媒体项
- `scrape_records`: 刮削记录
- `rename_history`: 重命名历史
- `notification_history`: 通知历史
- `cloud_drives`: 云盘配置
- `tasks`: 任务记录

---

## 📡 API 文档

### 核心 API 端点

#### 夸克网盘

```http
GET  /api/quark/browse              # 浏览目录
POST /api/quark/smart-rename-cloud  # 智能重命名预览
POST /api/quark/execute-cloud-rename # 执行重命名
```

#### STRM 生成

```http
POST /api/strm/generate    # 生成 STRM
POST /api/strm/check       # 校验 STRM
GET  /api/strm/records     # 扫描记录
```

#### 智能重命名

```http
POST /api/smart-rename/scan      # 扫描媒体文件
POST /api/smart-rename/preview   # 预览重命名
POST /api/smart-rename/execute   # 执行重命名
POST /api/smart-rename/rollback  # 回滚操作
```

#### Emby 集成

```http
POST /api/emby/refresh            # 刷新媒体库
GET  /api/emby/libraries          # 获取媒体库列表
GET  /api/emby/event-logs         # 事件日志
```

#### 文件管理

```http
GET  /api/file-manager/browse     # 浏览文件
POST /api/file-manager/upload     # 上传文件
DELETE /api/file-manager/delete   # 删除文件
```

#### 系统管理

```http
GET  /api/config                  # 获取配置
PUT  /api/config                  # 更新配置
GET  /api/metrics                 # 监控指标
GET  /api/dashboard/stats         # 仪表盘统计
```

### API 认证

所有敏感接口需要 API Key 认证:

**方式 1: Header**
```http
X-API-Key: your_api_key
```

**方式 2: Bearer Token**
```http
Authorization: Bearer your_token
```

**配置 API Key**:
```yaml
# config.yaml
security:
  api_key: "your_secret_api_key"
  require_api_key: true
```

### 在线 API 文档

启动服务后访问:
- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

---

## 📚 项目结构

```
smart_media/
├── quark_strm/                 # 主应用目录
│   ├── app/                    # 后端应用核心
│   │   ├── api/               # API 路由层 (20+ 个路由文件)
│   │   ├── config/            # 配置管理
│   │   ├── core/              # 核心基础设施
│   │   ├── models/            # 数据库模型
│   │   ├── schemas/           # Pydantic 数据验证
│   │   ├── services/          # 业务逻辑层 (40+ 个服务)
│   │   ├── utils/             # 工具函数
│   │   └── main.py            # FastAPI 应用入口
│   ├── web/                   # Vue 3 前端应用
│   │   ├── src/
│   │   │   ├── api/          # API 客户端 (17 个模块)
│   │   │   ├── components/   # 可复用组件
│   │   │   ├── views/        # 页面视图 (15 个页面)
│   │   │   ├── stores/       # Pinia 状态管理
│   │   │   ├── router/       # 路由配置
│   │   │   └── main.ts       # 入口文件
│   │   └── package.json
│   ├── docs/                  # 项目文档
│   ├── config.yaml            # 主配置文件
│   ├── requirements.txt       # Python 依赖
│   ├── Dockerfile             # Docker 镜像
│   └── docker-compose.yml     # 容器编排
├── scripts/                   # 运维脚本
├── config/                    # 配置目录
├── .github/workflows/         # CI/CD 配置
└── README.md                  # 本文件
```

完整文件索引详见：[`FILE_INDEX.md`](quark_strm/docs/FILE_INDEX.md)

---

## 🔧 配置说明

### 核心配置项

```yaml
# config.yaml 示例

# 夸克网盘配置
quark:
  cookie: "your_quark_cookie"
  root_id: "0"  # 根目录 ID

# TMDB 配置
tmdb:
  api_key: "your_tmdb_api_key"
  language: "zh-CN"

# Emby 配置
emby:
  enabled: true
  url: "http://localhost:8096"
  proxy_base_url: "http://localhost:18097"  # Emby 侧建议填写该入口
  api_key: "your_emby_api_key"
  refresh:
    on_strm_generate: true  # 生成 STRM 后自动刷新
    on_rename: true         # 重命名后自动刷新

# 通知配置
telegram:
  bot_token: "your_bot_token"
  chat_id: "your_chat_id"

wechat:
  corp_id: "your_corp_id"
  agent_id: "1000001"
  secret: "your_secret"

# 安全配置
security:
  api_key: "your_api_key"
  require_api_key: true

# CORS 配置
cors:
  allow_origins:
    - "http://localhost:3000"
    - "http://localhost:5173"
  allow_credentials: true
```

### 环境变量覆盖

支持通过环境变量覆盖配置文件中的值:

```bash
# .env 文件
SMART_MEDIA_QUARK_COOKIE=xxx
SMART_MEDIA_TMDB_API_KEY=xxx
SMART_MEDIA_EMBY_URL=http://localhost:8096
SMART_MEDIA_EMBY_PROXY_BASE_URL=http://localhost:18097
SMART_MEDIA_EMBY_API_KEY=xxx
SMART_MEDIA_API_KEY=xxx
# 302 失败后是否在服务端内部直接切到 stream 代理（默认 true）
SMART_MEDIA_PROXY_INTERNAL_REDIRECT=true
# 直链可播性探测缓存 TTL（秒，默认 20）
SMART_MEDIA_PLAYABLE_PROBE_CACHE_TTL=20
```

### 敏感数据加密

配置文件中支持加密存储敏感字段:

```yaml
quark:
  cookie: "encrypted:AQAA...base64_encoded_encrypted_value"
```

使用加密工具生成加密值:
```bash
python scripts/encrypt_config.py "your_secret_value"
```

---

## 🧪 测试

### 运行测试

```bash
cd quark_strm
pip install -r requirements.txt
pytest
```

### 运行特定测试套件

```bash
# 快速测试
python scripts/run_tests.py --suite fast

# 完整测试
python scripts/run_tests.py --suite full

# 生成覆盖率报告
pytest --cov=app --cov-report=html
```

### 自动化测试流水线

```bash
python scripts/auto_test_pipeline.py
```

---

## 📊 监控与日志

### 监控指标

访问监控端点获取系统指标:

```bash
# 系统健康状态
curl http://localhost:8000/api/monitor/system/status

# 所有指标
curl http://localhost:8000/api/monitor/metrics

# 特定指标历史
curl http://localhost:8000/api/monitor/metrics/system.cpu.percent

# 活跃告警
curl http://localhost:8000/api/monitor/alerts
```

### 日志查看

```bash
# Docker 日志
docker compose logs -f

# 本地日志
tail -f quark_strm/logs/app.log
```

### 告警阈值

默认告警配置:
- CPU > 80% 持续 60 秒
- 内存 > 85% 持续 120 秒
- 磁盘 > 90% 持续 300 秒
- 抓取任务失败率 > 30% 持续 120 秒

---

## 🛡️ 安全最佳实践

### 1. API Key 管理

- ✅ 生产环境必须设置强 API Key
- ✅ 定期轮换 API Key
- ✅ 不要将 API Key 提交到版本控制

### 2. 敏感数据加密

- ✅ 使用 `encrypted:` 前缀加密敏感配置
- ✅ 加密密钥存储在环境变量
- ✅ 定期备份加密配置

### 3. CORS 配置

- ✅ 生产环境明确指定允许的来源
- ✅ 禁止使用通配符 `*`
- ✅ 启用凭证时限制来源

### 4. 日志脱敏

系统自动脱敏以下敏感信息:
- 邮箱地址
- 手机号
- API 密钥
- JWT Token
- Cookie
- IP 地址

### 5. 路径安全

- ✅ 使用 `path_security.py` 验证文件路径
- ✅ 禁止路径遍历攻击 (`..` 序列)
- ✅ 符号链接检查

---

## 🤝 贡献指南

### 开发环境设置

1. Fork 项目
2. 创建开发分支 (`git checkout -b feature/AmazingFeature`)
3. 安装依赖 (`pip install -r requirements.txt`, `npm install`)
4. 运行测试确保功能正常
5. 提交更改 (`git commit -m 'Add some AmazingFeature'`)
6. 推送到分支 (`git push origin feature/AmazingFeature`)
7. 创建 Pull Request

### 代码规范

**后端**:
- 遵循 PEP 8
- 使用类型提示 (Type Hints)
- 添加文档字符串

**前端**:
- 遵循 Vue 风格指南
- 使用 TypeScript
- ESLint 检查通过

### 提交信息规范

```
feat: 新功能
fix: 修复 bug
docs: 文档更新
style: 代码格式调整
refactor: 重构
test: 测试相关
chore: 构建/工具链相关
```

---

## 📝 更新日志

### v2026.03.14-emby-proxy-hotfix1 (2026-03-14)

**代理修复**:
- ✅ 修复 18097 登录链路中响应头冲突导致的异常回包问题
- ✅ 专用代理请求跳过 CSRF/CSP 注入，恢复 Emby Web 登录兼容性
- ✅ 保留上游多值 `Set-Cookie`，避免登录态丢失

**Emby 对接**:
- ✅ 18097 统一作为 Emby 对接入口（页面 + API + PlaybackInfo Hook）
- ✅ 播放链路保持“302 优先，失败自动回退 stream 转发”

### v0.1.0 (2026-03-03)

**新增**:
- ✅ 夸克网盘文件浏览和 STRM 生成
- ✅ 智能重命名系统 (AI 增强)
- ✅ Emby 媒体服务器集成
- ✅ 多通道通知系统
- ✅ 分级缓存系统
- ✅ 系统监控和告警
- ✅ Web 管理界面

**优化**:
- ✅ 配置热加载支持
- ✅ 多级缓存性能优化
- ✅ 日志脱敏处理
- ✅ 安全加固

**修复**:
- ✅ 已知问题修复

详细更新日志见：[`CHANGELOG.md`](CHANGELOG.md)

---

## 📄 开源协议

本项目采用 [MIT](LICENSE) 协议开源。

---

## 🙏 致谢

感谢以下开源项目:

- [FastAPI](https://fastapi.tiangolo.com/) - 现代高性能 Web 框架
- [Vue 3](https://vuejs.org/) - 渐进式 JavaScript 框架
- [Element Plus](https://element-plus.org/) - Vue 3 组件库
- [SQLAlchemy](https://www.sqlalchemy.org/) - Python SQL 工具包
- [ECharts](https://echarts.apache.org/) - 数据可视化库
- [TMDB](https://www.themoviedb.org/) - 电影元数据 API
- [夸克网盘](https://pan.quark.cn/) - 云存储服务

---

## 📞 联系方式

- **项目 Issues**: [GitHub Issues](https://github.com/yourusername/smart_media/issues)
- **讨论区**: [GitHub Discussions](https://github.com/yourusername/smart_media/discussions)

---

## 📎 附录

### 相关文档

- [架构设计文档](quark_strm/docs/architecture/)
- [API 文档](quark_strm/docs/api/)
- [开发指南](quark_strm/docs/development/)
- [使用指南](quark_strm/docs/guides/)
- [运维文档](quark_strm/docs/operations/)
- [测试报告](quark_strm/docs/testing/)
- [验收报告](quark_strm/docs/qa/)

### 常见问题 (FAQ)

**Q: STRM 文件如何播放？**
A: 推荐将 Emby 的代理入口配置为 `http://<smart-media-host>:18097`。播放时 Smart Media 会自动处理 PlaybackInfo，优先走 302 直链，失败时自动回退到流代理转发。

**Q: 如何配置 AI 重命名？**
A: 在配置文件中设置 AI 服务提供商 (GLM/DeepSeek/Kimi) 的 API Key，然后在智能重命名界面选择 `ai_enhanced` 或 `ai_only` 算法。

**Q: 直链失效怎么办？**
A: 系统会自动检测直链有效性并刷新缓存。如果频繁失效，可以调整缓存 TTL 或启用 WebDAV 兜底播放。

**Q: 如何添加更多云盘支持？**
A: 参考 `app/services/storage/` 目录下的存储提供者抽象，实现新的云盘适配器即可。

---

<div align="center">

**Made with ❤️ by Smart Media Team**

⭐ 如果这个项目对你有帮助，请给一个 Star 支持！

</div>
