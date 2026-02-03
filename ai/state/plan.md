# Smart Media 项目启动计划

## 📋 计划信息
- **版本**: v1.0
- **创建时间**: 2026-02-04
- **优先级**: P0（最高）
- **状态**: 待执行

---

## 🎯 计划目标

启动 Smart Media 项目的后端服务和前端应用，确保系统可正常运行。

---

## 📊 当前状态

### 项目结构
```
smart_media/
└── quark_strm/              # 核心项目
    ├── app/                 # 后端应用（FastAPI）
    ├── web/                 # 前端应用（Vue 3）
    ├── config.yaml          # 配置文件
    ├── requirements.txt     # Python 依赖
    └── scripts/             # 启动脚本
```

### 技术栈
- **后端**: Python 3.11+ / FastAPI / SQLAlchemy
- **前端**: Vue 3 / Vite / Element Plus
- **数据库**: SQLite
- **缓存**: Redis（可选）

---

## 🚀 启动步骤

### 阶段 1: 环境检查
**目标**: 验证运行环境是否满足要求

**检查项**:
- [ ] Python 3.11+ 已安装
- [ ] Node.js 18+ 已安装
- [ ] pip 可用
- [ ] npm 可用

**验证命令**:
```bash
python --version
node --version
pip --version
npm --version
```

**预期结果**:
- Python >= 3.11
- Node.js >= 18
- pip 可用
- npm 可用

---

### 阶段 2: 依赖安装
**目标**: 安装后端和前端依赖

#### 2.1 后端依赖
**操作**:
```bash
cd c:\Users\24228\Desktop\smart_media\quark_strm
pip install -r requirements.txt
```

**验证**:
```bash
pip list | grep fastapi
pip list | grep uvicorn
```

#### 2.2 前端依赖
**操作**:
```bash
cd c:\Users\24228\Desktop\smart_media\quark_strm\web
npm install
```

**验证**:
```bash
npm list vue
npm list vite
```

---

### 阶段 3: 配置检查
**目标**: 验证配置文件是否正确

**检查文件**:
- `quark_strm/config.yaml`
- `quark_strm/web/.env` (如果存在)

**必需配置**:
```yaml
# config.yaml
api_keys:
  tmdb_api_key: "your_api_key_here"  # TMDB API Key

# 可选配置
proxy:
  http_proxy: "http://127.0.0.1:7890"
  https_proxy: "http://127.0.0.1:7890"
```

**验证**:
- [ ] config.yaml 存在
- [ ] TMDB API Key 已配置（或使用默认）

---

### 阶段 4: 启动后端服务
**目标**: 启动 FastAPI 后端服务

**方式 1: 使用启动脚本（推荐）**
```bash
cd c:\Users\24228\Desktop\smart_media\quark_strm
scripts\start-all.bat
```

**方式 2: 手动启动**
```bash
cd c:\Users\24228\Desktop\smart_media\quark_strm
uvicorn app.main:app --reload --port 8000
```

**验证**:
- [ ] 服务启动成功
- [ ] 访问 http://localhost:8000/docs 可看到 API 文档
- [ ] 无报错信息

**预期日志**:
```
INFO:     Uvicorn running on http://127.0.0.1:8000 (Press CTRL+C to quit)
INFO:     Started reloader process
INFO:     Started server process
INFO:     Waiting for application startup.
INFO:     Application startup complete.
```

---

### 阶段 5: 启动前端应用
**目标**: 启动 Vue 3 前端开发服务器

**操作**:
```bash
cd c:\Users\24228\Desktop\smart_media\quark_strm\web
npm run dev
```

**验证**:
- [ ] 开发服务器启动成功
- [ ] 访问 http://localhost:5173 可看到界面
- [ ] 无报错信息

**预期日志**:
```
VITE v5.x.x  ready in xxx ms

➜  Local:   http://localhost:5173/
➜  Network: use --host to expose
```

---

### 阶段 6: 功能验证
**目标**: 验证核心功能可正常使用

**验证项**:
- [ ] 前端页面正常加载
- [ ] 后端 API 可正常调用
- [ ] 数据库连接正常
- [ ] 日志输出正常

**测试步骤**:
1. 打开浏览器访问 http://localhost:5173
2. 检查首页是否正常显示
3. 打开浏览器开发者工具，检查网络请求
4. 访问 http://localhost:8000/docs 测试 API

**成功标准**:
- ✅ 前端界面正常显示
- ✅ API 文档可访问
- ✅ 无控制台错误
- ✅ 网络请求正常

---

## 📝 常见问题

### 问题 1: 端口占用
**现象**: `Address already in use`

**解决**:
```bash
# Windows
netstat -ano | findstr :8000
taskkill /PID <PID> /F

# 或更换端口
uvicorn app.main:app --reload --port 8001
```

### 问题 2: 依赖安装失败
**现象**: `pip install` 或 `npm install` 失败

**解决**:
```bash
# Python 依赖
pip install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple

# Node 依赖
npm install --registry=https://registry.npmmirror.com
```

### 问题 3: 数据库文件缺失
**现象**: `no such table`

**解决**:
```bash
# 重新初始化数据库
python -c "from app.core.database import init_db; init_db()"
```

### 问题 4: TMDB API 调用失败
**现象**: `401 Unauthorized` 或 `Network Error`

**解决**:
1. 检查 `config.yaml` 中的 API Key
2. 检查网络连接
3. 配置代理（如需要）

---

## 🔄 停止服务

### 停止后端
```bash
# 使用脚本
scripts\stop-all.bat

# 或手动停止
# 在运行 uvicorn 的终端按 Ctrl+C
```

### 停止前端
```bash
# 在运行 npm run dev 的终端按 Ctrl+C
```

---

## 📊 执行检查清单

### 启动前
- [ ] 环境检查完成
- [ ] 依赖安装完成
- [ ] 配置文件检查完成

### 启动中
- [ ] 后端服务启动成功
- [ ] 前端服务启动成功
- [ ] 无报错信息

### 启动后
- [ ] 功能验证通过
- [ ] 日志输出正常
- [ ] 性能正常

---

## 🎯 成功标准

### 必须满足
- ✅ 后端服务运行在 http://localhost:8000
- ✅ 前端服务运行在 http://localhost:5173
- ✅ API 文档可访问
- ✅ 前端界面正常显示

### 可选满足
- ⭕ Redis 缓存服务运行
- ⭕ 监控服务运行
- ⭕ 日志收集正常

---

## 📈 下一步计划

启动成功后，可进行：
1. **功能测试**: 测试刮削、重命名等核心功能
2. **性能优化**: 根据监控数据优化性能
3. **功能开发**: 开发新功能
4. **Bug 修复**: 修复已知问题

---

## 📝 执行记录

### 执行日志
将在 `ai/logs/` 目录下生成执行日志：
- `startup_{timestamp}.log`

### 状态更新
执行过程中将更新本文件的状态字段。

---

**创建者**: Architect Agent  
**执行者**: DevOps Agent  
**状态**: 待执行  
**最后更新**: 2026-02-04
