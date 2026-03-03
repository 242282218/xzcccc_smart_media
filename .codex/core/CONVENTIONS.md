# CONVENTIONS.md — 编码约定

> **核心原则**：前沿工具链 + 安全优先 + 长期可维护
> 本文件定义"**选什么**"和"**怎么写**"，执行约束见 `RULES.md`

---

## 1. 语言与运行时

### Python 3.12+

**核心工具链**
```bash
# 包管理（速度快 100x，支持 lockfile）
uv init && uv add <package>

# Lint + 格式化（单工具全搞定）
ruff check . && ruff format .

# 类型检查（严格模式）
pyright --strict

# 测试 + 覆盖率
pytest --cov=src tests/
```

**技术栈**
| 用途 | 工具 | 理由 |
|------|------|------|
| 包管理 | `uv` | 取代 pip/poetry，速度快 100x |
| Lint & 格式化 | `ruff` | 取代 flake8+black+isort |
| 类型检查 | `pyright` | 严格模式，速度快 |
| 运行时校验 | `pydantic` v2 | 数据边界验证 |
| 测试 | `pytest` + `pytest-cov` | 标准测试框架 |

**项目结构**
```
my-project/
├── src/
│   └── myapp/
│       ├── __init__.py
│       ├── core/          # 核心业务逻辑
│       ├── api/           # API 层
│       └── utils/         # 工具函数
├── tests/
│   ├── unit/
│   └── integration/
├── pyproject.toml         # 唯一配置入口
└── uv.lock                # 提交到 Git，保证可复现
```

### TypeScript / Node.js 22+

**核心工具链**
```bash
# 包管理（速度快，磁盘占用少）
pnpm install && pnpm add <package>

# Lint + 格式化
eslint . && prettier --write .

# 类型检查
tsc --noEmit

# 测试（比 Jest 快，原生 ESM/TS）
vitest run
```

**技术栈**
| 用途 | 工具 | 配置要点 |
|------|------|----------|
| 运行时 | Node.js 22+ | 原生 TS 支持，无需 ts-node |
| 类型系统 | TypeScript 5.x | `strict: true` |
| 模块系统 | ESM | `"type": "module"` + `node:` 前缀 |
| 包管理 | `pnpm` | 速度、磁盘占用优于 npm/yarn |
| Lint | `ESLint` v9 | flat config |
| 格式化 | `Prettier` | 统一代码风格 |
| 测试 | `Vitest` | 原生 ESM/TS 支持 |

### Shell / 脚本

| 平台 | 工具 | 最佳实践 |
|------|------|----------|
| Windows | PowerShell 7+ | 跨平台，避免 cmd |
| Linux/macOS | Bash | `set -euo pipefail` |
| 跨平台 | Python | 优先用 Python 替代 shell |

### Skill Frontmatter（Codex 标准）

`SKILL.md` 的 frontmatter 采用 Codex 标准：

| 字段 | 级别 | 说明 |
|------|------|------|
| `name` | MUST | 技能唯一标识名 |
| `description` | MUST | 触发描述，中文语境下必须使用中文 |
| `license` | SHOULD | 许可证说明（如有） |

说明：
- 不强制要求 `short-description` 字段。
- 迁移外部技能时，优先保证 `description` 可用于中文触发。

---

## 2. 架构模式

### 架构选型

| 场景 | 模式 | 理由 | 适用规模 |
|------|------|------|----------|
| 一般项目 | **模块化单体** | 易维护，好拆分 | < 10 万行 |
| API 服务 | **Clean Architecture** | 业务与框架解耦 | 任意规模 |
| 数据流 | **Stream/Pipeline** | 节省内存 | 大文件/日志 |
| AI 应用 | **Agent + Tool** | 单一职责，可测试 | 任意规模 |

### 设计原则（SOLID 精简版）

```python
# ✅ 单一职责：一个函数只做一件事
def validate_email(email: str) -> bool:
    return "@" in email and "." in email.split("@")[1]

def send_email(to: str, subject: str, body: str) -> None:
    # 只负责发送，不负责验证
    ...

# ✅ 依赖注入：依赖从外部传入
class UserService:
    def __init__(self, db: Database, cache: Cache):
        self.db = db
        self.cache = cache

# ✅ 接口优先：先定义类型，再写实现
from typing import Protocol

class Storage(Protocol):
    def save(self, key: str, value: str) -> None: ...
    def load(self, key: str) -> str: ...

# ✅ 纯函数优先：无副作用，可测试
def calculate_discount(price: float, rate: float) -> float:
    return price * (1 - rate)
```

### 异步编程

**Python**
```python
# ✅ 全面使用 async/await
async def fetch_data(url: str) -> dict:
    async with httpx.AsyncClient() as client:
        response = await client.get(url)
        return response.json()

# ✅ 并发请求
results = await asyncio.gather(
    fetch_data(url1),
    fetch_data(url2),
    fetch_data(url3)
)
```

**Node.js**
```typescript
// ✅ async/await + Promise.all()
const results = await Promise.all([
  fetchData(url1),
  fetchData(url2),
  fetchData(url3)
]);

// ❌ 绝不阻塞事件循环
// 避免：while (true) { ... }
// 避免：大量同步计算
```

**CPU 密集型任务**
- Python：`ProcessPoolExecutor`
- Node.js：`Worker Threads`

---

## 3. 安全规范（强制）

### 输入验证

```python
# ✅ 使用 allowlist 验证
from pydantic import BaseModel, Field, validator

class UserInput(BaseModel):
    username: str = Field(pattern=r'^[a-zA-Z0-9_]{3,20}$')
    age: int = Field(ge=0, le=150)

    @validator('username')
    def validate_username(cls, v):
        allowed_chars = set('abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789_')
        if not set(v).issubset(allowed_chars):
            raise ValueError('Invalid characters')
        return v

# ✅ 参数化查询（防 SQL 注入）
cursor.execute("SELECT * FROM users WHERE id = ?", (user_id,))

# ❌ 字符串拼接 SQL
cursor.execute(f"SELECT * FROM users WHERE id = {user_id}")  # 危险！
```

### 密钥管理

```bash
# ✅ 环境变量 + .env
echo "API_KEY=your_key_here" > .env
echo ".env" >> .gitignore

# Python
from dotenv import load_dotenv
import os
load_dotenv()
api_key = os.getenv("API_KEY")

# Node.js
import 'dotenv/config';
const apiKey = process.env.API_KEY;
```

**强制规则**
- ❌ 禁止硬编码任何密钥、Token、密码
- ✅ `.env` 必须加入 `.gitignore`
- ✅ 生产环境使用 Secret Manager（Vault、云 KMS）
- ✅ 定期轮换密钥，日志脱敏

### 依赖安全

```bash
# Python：锁定依赖 + 安全扫描
uv lock
pip-audit

# Node.js：锁定依赖 + 安全扫描
pnpm install --frozen-lockfile
pnpm audit

# CI 集成（GitHub Actions 示例）
- name: Security Audit
  run: |
    pip-audit
    pnpm audit
```

### 认证 / 授权

| 场景 | 推荐方案 | 禁止使用 |
|------|----------|----------|
| 密码存储 | `bcrypt` / `argon2` | MD5 / SHA1 |
| Token | JWT + RS256（非对称） | 对称密钥 |
| 权限 | 最小权限原则 | 过度授权 |

### 错误处理

```python
# ✅ 用户侧返回通用错误
try:
    result = process_payment(user_id, amount)
except Exception as e:
    logger.error(f"Payment failed: {e}", exc_info=True)  # 详细日志
    return {"error": "Payment processing failed"}  # 通用错误

# ❌ 暴露内部信息
except Exception as e:
    return {"error": str(e)}  # 可能泄露堆栈、路径
```

### OWASP Top 10 重点防御

| 编号 | 威胁 | 防御措施 |
|------|------|----------|
| A01 | 访问控制失效 | 最小权限 + 权限验证 |
| A03 | 供应链攻击 | 依赖锁定 + SCA 扫描 |
| A07 | 注入攻击 | 参数化查询 + 输入验证 |
| A10 | 异常处理不当 | 全局捕获 + 日志脱敏 |

---

## 4. 代码风格

### 通用原则

| 原则 | 标准 | 示例 |
|------|------|------|
| 可读性优先 | 代码是写给人看的 | 清晰 > 聪明 |
| 函数长度 | ≤ 40 行 | 超出考虑拆分 |
| 嵌套层数 | ≤ 3 层 | 用早返回减少嵌套 |
| 魔法数字 | 提取为常量 | `MAX_RETRIES = 3` |

**早返回示例（Guard Clause）**
```python
# ✅ 早返回，减少嵌套
def process_user(user: User) -> Result:
    if not user.is_active:
        return Result.error("User inactive")

    if not user.has_permission():
        return Result.error("No permission")

    return Result.success(user.data)

# ❌ 深层嵌套
def process_user(user: User) -> Result:
    if user.is_active:
        if user.has_permission():
            return Result.success(user.data)
        else:
            return Result.error("No permission")
    else:
        return Result.error("User inactive")
```

### 命名规范

| 类型 | Python | TypeScript | 示例 |
|------|--------|------------|------|
| 变量/函数 | `snake_case` | `camelCase` | `user_name` / `userName` |
| 类 | `PascalCase` | `PascalCase` | `UserService` |
| 常量 | `UPPER_SNAKE` | `UPPER_SNAKE` | `MAX_RETRIES` |
| 文件 | `snake_case.py` | `kebab-case.ts` | `user_service.py` / `user-service.ts` |
| 私有成员 | `_private` | `#private` | `_internal_method` / `#privateField` |

### 注释规范

```python
# ✅ 解释"为什么"
def retry_on_failure(func, max_retries=3):
    # 使用指数退避避免瞬时故障导致雪崩
    for i in range(max_retries):
        try:
            return func()
        except Exception:
            time.sleep(2 ** i)

# ❌ 解释"做什么"（代码已经说明）
def add(a, b):
    # 将 a 和 b 相加
    return a + b

# ✅ TODO 格式
# TODO(张三): 优化查询性能 — 关联 issue #123
```

**注释原则**
- 复杂算法 / 非直觉行为必须注释
- TODO 必须包含：作者、描述、关联 issue
- 不留无主 TODO

---

## 5. 测试规范

### 测试目标

| 指标 | 目标 | 说明 |
|------|------|------|
| 核心业务逻辑 | ≥ 80% | 关键路径必须覆盖 |
| 工具函数 | ≥ 90% | 纯函数易测试 |
| UI/集成 | ≥ 60% | 关键流程覆盖 |

### 测试分类

```python
# Unit：纯逻辑，毫秒级，无 IO
def test_calculate_discount_when_rate_valid_then_returns_discounted_price():
    result = calculate_discount(100.0, 0.2)
    assert result == 80.0

# Integration：跨模块，含外部依赖（用 mock）
@pytest.mark.asyncio
async def test_user_service_when_create_user_then_saves_to_db(mock_db):
    service = UserService(mock_db)
    user = await service.create_user("test@example.com")
    assert mock_db.save.called

# E2E：只覆盖关键路径
def test_checkout_flow_when_valid_cart_then_completes_order():
    # 完整的购物车 -> 支付 -> 订单流程
    ...
```

### 测试命名

**格式**：`test_<行为>_when_<条件>_then_<预期>`

```python
# ✅ 清晰的测试名
def test_login_when_invalid_password_then_returns_error():
    ...

def test_send_email_when_recipient_not_found_then_raises_exception():
    ...

# ❌ 模糊的测试名
def test_login():
    ...

def test_email_error():
    ...
```

### 测试最佳实践

```python
# ✅ 使用 fixture 复用设置
@pytest.fixture
def user():
    return User(id=1, name="Test User")

def test_user_service(user):
    assert user.name == "Test User"

# ✅ 使用事件等待，不用 sleep
async def test_async_task():
    task = start_background_task()
    await task  # ✅ 等待完成
    # time.sleep(1)  # ❌ 禁止

# ✅ 参数化测试
@pytest.mark.parametrize("input,expected", [
    (100, 80),
    (50, 40),
    (0, 0),
])
def test_discount(input, expected):
    assert calculate_discount(input, 0.2) == expected
```

---

## 6. Git 规范

### Commit 消息（Conventional Commits）

**格式**
```
<type>(<scope>): <描述>

[可选的详细说明]

[可选的 footer]
```

**类型（type）**
| 类型 | 说明 | 示例 |
|------|------|------|
| `feat` | 新功能 | `feat(auth): 添加 JWT 刷新机制` |
| `fix` | Bug 修复 | `fix(api): 修复空指针导致的 500 错误` |
| `refactor` | 重构 | `refactor(db): 优化查询性能` |
| `docs` | 文档 | `docs(readme): 更新安装说明` |
| `test` | 测试 | `test(user): 添加登录测试用例` |
| `chore` | 构建/依赖 | `chore(deps): 升级 pydantic 到 v2.7` |
| `perf` | 性能优化 | `perf(cache): 使用 Redis 缓存` |
| `ci` | CI/CD | `ci(github): 添加自动部署` |

**示例**
```bash
# 功能开发
git commit -m "feat(auth): 添加 OAuth2 登录支持"

# Bug 修复
git commit -m "fix(api): 修复并发请求导致的数据竞争"

# 重构
git commit -m "refactor(core): 将业务逻辑从 API 层分离"

# 依赖更新
git commit -m "chore(deps): 升级 TypeScript 到 5.4"
```

### 分支策略

```bash
# 主分支（稳定）
main

# 功能开发
feat/user-authentication
feat/payment-integration

# Bug 修复
fix/login-error
fix/memory-leak

# 工作流
git checkout -b feat/new-feature
# ... 开发 ...
git commit -m "feat(module): 添加新功能"
git push origin feat/new-feature
# 创建 PR，squash merge 到 main
```

**分支规则**
- `main`：稳定分支，只接受 PR/merge
- `feat/<功能名>`：功能开发
- `fix/<问题描述>`：bug 修复
- 完成后 squash merge，保持 main 历史干净

### .gitignore 必备

```gitignore
# 密钥和配置
.env
.env.local
*.key
*.pem

# 构建产物
dist/
build/
__pycache__/
*.pyc
*.pyo
node_modules/

# IDE 配置（除非团队共享）
.idea/
.vscode/
*.swp
*.swo

# 操作系统
.DS_Store
Thumbs.db

# 日志
*.log
logs/
```

---

## 7. 工具链速查

### 常用命令

**Python**
```bash
# 项目初始化
uv init
uv add <package>

# 开发工具
ruff check .                    # Lint 检查
ruff format .                   # 代码格式化
pyright --strict                # 类型检查
pytest --cov=src tests/         # 测试 + 覆盖率
pip-audit                       # 安全扫描

# 依赖管理
uv lock                         # 锁定依赖
uv sync                         # 同步依赖
uv add --dev pytest             # 添加开发依赖
```

**TypeScript / Node.js**
```bash
# 项目初始化
pnpm init
pnpm add <package>

# 开发工具
eslint .                        # Lint 检查
prettier --write .              # 代码格式化
tsc --noEmit                    # 类型检查
vitest run                      # 测试
pnpm audit                      # 安全扫描

# 依赖管理
pnpm install --frozen-lockfile  # 锁定安装
pnpm add -D vitest              # 添加开发依赖
pnpm update                     # 更新依赖
```

### 工具对照表

| 用途 | Python | TypeScript |
|------|--------|------------|
| 依赖管理 | `uv` | `pnpm` |
| Lint | `ruff` | `ESLint` v9 |
| 格式化 | `ruff format` | `Prettier` |
| 类型检查 | `pyright` | `tsc --noEmit` |
| 测试 | `pytest` | `Vitest` |
| 安全扫描 | `pip-audit` | `pnpm audit` |
| Pre-commit | `pre-commit` | `husky` + `lint-staged` |

### CI/CD 集成示例

```yaml
# .github/workflows/ci.yml
name: CI

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      # Python
      - name: Setup Python
        uses: actions/setup-python@v5
        with:
          python-version: '3.12'

      - name: Install uv
        run: pip install uv

      - name: Install dependencies
        run: uv sync

      - name: Lint & Format
        run: |
          ruff check .
          ruff format --check .

      - name: Type check
        run: pyright --strict

      - name: Test
        run: pytest --cov=src tests/

      - name: Security audit
        run: pip-audit

      # TypeScript
      - name: Setup Node.js
        uses: actions/setup-node@v4
        with:
          node-version: '22'

      - name: Install pnpm
        run: npm install -g pnpm

      - name: Install dependencies
        run: pnpm install --frozen-lockfile

      - name: Lint & Format
        run: |
          eslint .
          prettier --check .

      - name: Type check
        run: tsc --noEmit

      - name: Test
        run: vitest run

      - name: Security audit
        run: pnpm audit
```

---

## 8. 快速参考

### 项目初始化清单

**Python 项目**
```bash
# 1. 创建项目结构
mkdir -p src/myapp tests
touch pyproject.toml README.md .gitignore

# 2. 初始化 uv
uv init

# 3. 添加核心依赖
uv add pydantic httpx

# 4. 添加开发依赖
uv add --dev pytest pytest-cov ruff pyright

# 5. 配置 pyproject.toml
# [tool.ruff]
# [tool.pyright]
# [tool.pytest]

# 6. 初始化 Git
git init
git add .
git commit -m "chore: 初始化项目"
```

**TypeScript 项目**
```bash
# 1. 创建项目结构
mkdir -p src tests
touch package.json tsconfig.json .gitignore

# 2. 初始化 pnpm
pnpm init

# 3. 添加 TypeScript
pnpm add -D typescript @types/node

# 4. 添加开发工具
pnpm add -D eslint prettier vitest

# 5. 配置文件
# tsconfig.json: {"compilerOptions": {"strict": true}}
# eslint.config.js
# .prettierrc

# 6. 初始化 Git
git init
git add .
git commit -m "chore: 初始化项目"
```

### 代码审查清单

- [ ] 代码符合命名规范
- [ ] 函数长度 ≤ 40 行
- [ ] 嵌套层数 ≤ 3 层
- [ ] 无硬编码密钥
- [ ] 输入已验证
- [ ] 错误处理完善
- [ ] 有单元测试
- [ ] 类型检查通过
- [ ] Lint 检查通过
- [ ] 安全扫描通过

---

> **最后更新**：2026-03
> **下次复查**：每 6 个月检查工具链版本更新
> **维护者**：定期审查并更新本文档，确保与最新最佳实践保持一致
