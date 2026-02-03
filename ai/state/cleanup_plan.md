# 项目文件清理计划

## 📅 创建时间
2026-02-04 00:30:59

## 🎯 清理目标
对 smart_media 项目进行系统性文件清理与优化，删除不必要文件，保留核心功能，规范文件结构。

## 📊 当前项目状态分析

### 根目录结构 (c:\Users\24228\Desktop\smart_media)
```
smart_media/
├── .agent/              # Agent 配置目录
├── .git/                # Git 仓库
├── .gitignore           # Git 忽略配置
├── .lingma/             # Lingma 配置
├── .trae/               # Trae 配置
├── .vscode/             # VSCode 配置
├── ai/                  # AI 规则与状态
├── node_modules/        # Node 依赖（根目录）⚠️
├── package.json         # 根目录包配置 ⚠️
├── package-lock.json    # 根目录锁文件 ⚠️
├── quark_strm/          # 核心项目目录
├── reference_project/   # 参考项目 ⚠️
├── test/                # 测试目录（根级别）⚠️
├── test_*.js            # 测试脚本 ⚠️
├── test_config.json     # 测试配置 ⚠️
└── PANSOU_INTEGRATION.md # 文档
```

### quark_strm 项目结构
```
quark_strm/
├── .agent/              # Agent 配置
├── .git/                # Git 仓库（独立）
├── .gitignore           # Git 忽略
├── .pytest_cache/       # Pytest 缓存 ⚠️
├── .trae/               # Trae 配置
├── __pycache__/         # Python 缓存 ⚠️
├── app/                 # 核心应用代码 ✅
├── artifacts/           # 构建产物 ⚠️
├── build/               # 构建目录 ⚠️
├── config.yaml          # 配置文件 ✅
├── conftest.py          # Pytest 配置 ⚠️
├── data/                # 数据目录 ✅
├── docs/                # 文档目录 ✅
├── logs/                # 日志目录 ✅
├── quark_strm.db        # 数据库文件 ✅
├── requirements.txt     # Python 依赖 ✅
├── pyproject.toml       # 项目配置 ✅
├── scripts/             # 脚本目录 ✅
├── strm/                # STRM 文件目录 ✅
├── test_strm/           # 测试 STRM 目录 ⚠️
├── test_task.py         # 测试脚本 ⚠️
├── tests/               # 测试目录 ⚠️
├── tmp/                 # 临时目录 ⚠️
├── web/                 # 前端代码 ✅
├── Dockerfile           # Docker 配置 ✅
├── docker-compose.yml   # Docker Compose ✅
└── *.md                 # 文档文件 ✅
```

## 🗑️ 待清理文件分类

### 类别 1：Python 缓存文件（自动生成，可安全删除）
- 所有 `__pycache__/` 目录（21 个）
- 所有 `.pyc` 文件（23 个）
- `.pytest_cache/` 目录

**影响评估**：✅ 无影响，运行时自动重新生成

### 类别 2：测试相关文件（按需求删除）
#### 根目录测试文件
- `test/` 目录（19 个文件）
- `test_axios_params.js`
- `test_params_serialize.js`
- `test_config.json`

#### quark_strm 测试文件
- `tests/` 目录（完整测试套件）
  - `tests/unit/` - 单元测试
  - `tests/integration/` - 集成测试
  - `tests/e2e/` - 端到端测试
  - `tests/regression/` - 回归测试
  - `tests/mocks/` - Mock 文件
- `test_strm/` 目录（108 个测试文件）
- `test_task.py`
- `conftest.py`（pytest 配置）
- `TEST_SUMMARY.md`

**影响评估**：⚠️ 删除后无法运行测试，但不影响核心功能运行

### 类别 3：构建与临时文件
- `quark_strm/build/` 目录
- `quark_strm/artifacts/` 目录
- `quark_strm/tmp/` 目录
- `logs/test_write.txt`

**影响评估**：✅ 可安全删除，构建时重新生成

### 类别 4：参考项目与冗余依赖
- `reference_project/` 目录（343 个文件）⚠️ 需确认
- 根目录 `node_modules/` ⚠️ 需确认是否必要
- 根目录 `package.json` 和 `package-lock.json` ⚠️ 需确认

**影响评估**：⚠️ 需要人工确认是否为开发参考资料

### 类别 5：脚本工具（保留核心，删除测试相关）
保留：
- `scripts/backup.bat` / `backup.sh` - 备份脚本
- `scripts/start-all.bat` / `stop-all.bat` - 启动/停止脚本
- `scripts/encrypt_config.py` - 配置加密

可删除：
- `scripts/e2e_test.py` - E2E 测试脚本
- `scripts/quality_check.py` - 质量检查（测试相关）
- `scripts/verify_improvements.py` - 验证脚本（测试相关）
- `scripts/simple_verify.py` - 简单验证（测试相关）
- `scripts/auto_fix_agent.py` - 自动修复（开发工具）

**影响评估**：✅ 删除测试脚本不影响核心功能

### 类别 6：文档整理（保留核心，删除冗余）
保留核心文档：
- `README.md`
- `SECURITY_CONFIG.md`
- `docs/QUICK_START.md`
- `docs/PROJECT_STRUCTURE.md`
- `docs/Redis缓存使用指南.md`
- `docs/监控系统使用指南.md`

可删除/合并：
- `OPTIMIZATION_COMPLETE_REPORT.md` - 优化报告（已过时）
- `TEST_SUMMARY.md` - 测试摘要
- `docs/优化变更记录.md` - 优化记录（可归档）
- `docs/优化工作总结报告.md` - 优化总结（可归档）
- `docs/优化总结报告.md` - 优化总结（重复）
- `docs/项目清理总结报告.md` - 清理报告（旧）
- `docs/测试报告.md` - 测试报告
- `docs/reports/Test_Report_*.md` - 测试报告

**影响评估**：✅ 删除历史文档不影响功能

## 📋 清理执行计划

### 阶段 1：安全清理（无风险）
1. 删除所有 `__pycache__/` 目录
2. 删除所有 `.pyc` 文件
3. 删除 `.pytest_cache/` 目录
4. 清空 `tmp/` 目录
5. 删除 `build/` 和 `artifacts/` 目录

**预计减少**：约 5-10 MB

### 阶段 2：测试文件清理（按需求）
1. 删除根目录测试文件（`test/`, `test_*.js`, `test_config.json`）
2. 删除 `quark_strm/tests/` 完整目录
3. 删除 `quark_strm/test_strm/` 目录
4. 删除 `quark_strm/test_task.py`
5. 删除 `quark_strm/conftest.py`
6. 删除测试相关脚本

**预计减少**：约 20-50 MB

### 阶段 3：文档整理
1. 删除过时的优化报告
2. 删除测试报告
3. 整理 `docs/` 目录结构
4. 归档历史文档到 `docs/archive/`

**预计减少**：约 1-2 MB

### 阶段 4：参考项目处理（需确认）
1. 评估 `reference_project/` 是否仍需要
2. 如不需要，完整删除
3. 评估根目录 `node_modules/` 必要性

**预计减少**：约 50-200 MB（如删除）

### 阶段 5：验证与报告
1. 验证核心功能可正常启动
2. 检查依赖完整性
3. 生成清理报告
4. 更新 `.gitignore`

## 🔒 保留的核心文件清单

### 应用核心
- `app/` - 完整应用代码
- `web/` - 前端代码
- `config.yaml` - 配置文件
- `quark_strm.db` - 数据库
- `requirements.txt` - Python 依赖
- `pyproject.toml` - 项目配置

### 数据与日志
- `data/` - 数据目录
- `logs/` - 日志目录（保留结构）
- `strm/` - STRM 文件

### 部署与脚本
- `Dockerfile` / `docker-compose.yml`
- `scripts/backup.*` - 备份脚本
- `scripts/start-all.bat` / `stop-all.bat`
- `scripts/encrypt_config.py`

### 文档
- `README.md`
- `SECURITY_CONFIG.md`
- `docs/QUICK_START.md`
- `docs/PROJECT_STRUCTURE.md`
- `docs/Redis缓存使用指南.md`
- `docs/监控系统使用指南.md`

### 配置
- `.gitignore`
- `.env.example`
- `ai/` - AI 规则与状态
- `.agent/` / `.trae/` - Agent 配置

## ⚠️ 风险评估

### 高风险操作（需人工确认）
1. ❌ 删除 `reference_project/` - 可能包含重要参考代码
2. ❌ 删除根目录 `node_modules/` - 需确认是否有根级别依赖
3. ❌ 删除所有测试文件 - 无法进行回归测试

### 中风险操作
1. ⚠️ 删除测试脚本 - 可能影响 CI/CD 流程
2. ⚠️ 删除历史文档 - 可能丢失重要上下文

### 低风险操作
1. ✅ 删除缓存文件 - 可自动重新生成
2. ✅ 删除临时文件 - 不影响功能
3. ✅ 删除构建产物 - 可重新构建

## 📝 回滚方案

### Git 锚点
当前 Git commit: `8a8adf2723a78346199384040edff9e8c8561bc9`

### 回滚命令
```bash
# 完全回滚
git reset --hard 8a8adf2723a78346199384040edff9e8c8561bc9

# 部分回滚（恢复特定文件）
git checkout 8a8adf2723a78346199384040edff9e8c8561bc9 -- <file_path>
```

### 备份建议
在执行清理前，建议：
1. 创建完整项目备份
2. 确保 Git 仓库状态干净
3. 记录当前磁盘使用情况

## 🎯 成功标准

### 功能验证
- ✅ 后端服务可正常启动
- ✅ 前端页面可正常访问
- ✅ 核心 API 接口可正常调用
- ✅ 数据库连接正常
- ✅ Redis 缓存正常工作

### 结构验证
- ✅ 目录结构清晰
- ✅ 文件命名规范
- ✅ 无冗余文件
- ✅ 文档完整且最新

### 性能指标
- ✅ 项目体积减少 30% 以上
- ✅ Git 仓库大小优化
- ✅ IDE 加载速度提升

## 📊 预期清理结果

### 文件数量
- 删除文件：约 200-400 个
- 保留文件：约 150-250 个
- 减少比例：约 50-70%

### 磁盘空间
- 当前大小：约 300-500 MB（估算）
- 清理后：约 100-200 MB
- 减少空间：约 150-300 MB

## ❓ 待人工确认的问题

1. **是否删除 `reference_project/` 目录？**
   - 包含 343 个文件
   - 可能是开发参考资料
   - 建议：先归档再删除

2. **是否删除根目录 `node_modules/`？**
   - 需确认根目录是否有 Node.js 项目
   - `package.json` 内容需检查
   - 建议：检查后决定

3. **是否完全删除所有测试文件？**
   - 包括单元测试、集成测试、E2E 测试
   - 删除后无法进行自动化测试
   - 建议：保留核心测试框架，删除具体测试用例

4. **是否删除历史优化文档？**
   - 可能包含重要的决策记录
   - 建议：归档到 `docs/archive/` 而非删除

## 🚀 下一步行动

等待人工确认以下内容：
1. ✅ 同意执行阶段 1（安全清理）
2. ❓ 是否执行阶段 2（测试文件清理）
3. ❓ 是否执行阶段 3（文档整理）
4. ❓ 是否执行阶段 4（参考项目处理）
5. ❓ 对上述 4 个待确认问题的决策

---

**创建者**: Architect Agent  
**状态**: 等待人工确认  
**优先级**: P0（系统性清理）
