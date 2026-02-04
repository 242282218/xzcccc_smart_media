# AI Runner 执行器配置 v2.0

## 📋 文档信息
- **版本**: v2.0
- **更新时间**: 2026-02-04
- **用途**: 定义 AI Agent 执行流程与环境配置

---

## 🎯 执行器概述

AI Runner 是 smart_media 项目的 AI Agent 执行引擎，负责：
- 任务调度与分发
- 执行环境管理
- 日志记录与监控
- 错误处理与回滚

---

## 🔧 环境配置

### 项目路径
```yaml
project_root: c:\Users\24228\Desktop\smart_media
core_project: c:\Users\24228\Desktop\smart_media\quark_strm
ai_root: c:\Users\24228\Desktop\smart_media\ai
```

### 关键目录
```yaml
directories:
  rules: ai/rules/              # 规则文件（必读）
  state: ai/state/              # 状态文件（必读）
  logs: ai/logs/                # 执行日志
  workflows: .agent/workflows/  # Workflow 定义
  testing: quark_strm/docs/testing/  # 测试文档
```

### 必需文件
```yaml
required_files:
  - ai/rules/agent.md           # Agent 规范（必读）
  - ai/rules/debug_guide.md     # 调试指南（必读）
  - ai/runner.md                # Runner 配置（本文件）
  - ai/state/plan.md            # 当前计划
```

---

## 🚀 执行流程

### 阶段1: 初始化检查

**必须完成的检查项**:
```
□ 1. 读取 ai/rules/agent.md
□ 2. 读取 ai/runner.md
□ 3. 读取 ai/state/plan.md（如果不存在则创建）
□ 4. 声明当前 Agent 角色
□ 5. 确认任务理解正确
```

**检查失败处理**:
- 文件不存在 → 报告"前置条件不足"并停止
- 角色不明确 → 询问用户明确角色

### 阶段2: 任务分析

**代码修改任务必须**:
```
□ 1. 定位相关文件（grep_search / find_by_name）
□ 2. 查看现有代码（view_file）
□ 3. 理解代码上下文
□ 4. 说明修改计划
□ 5. 获得用户确认（如果是重大修改）
```

**问题排查任务必须**:
```
□ 1. 复现问题
□ 2. 收集错误信息
□ 3. 分析根因
□ 4. 验证假设
□ 5. 修复并验证
```

### 阶段3: 执行与验证

**执行规则**:
- 📝 每步输出真实日志
- ⏱️ 超时时间: 30秒
- ❌ 失败立即停止，标记FAIL
- 🔄 禁止自动重试

**验证方式优先级**:
1. Python 代码调用
2. API 请求测试
3. 终端命令（最后选择）

### 阶段4: 完成报告

**报告格式**:
```markdown
## 执行结果
- **任务**: [描述]
- **状态**: ✅/❌
- **修改**: [文件列表]
- **验证**: [方法和结果]
```

---

## 📊 日志规范

### 日志格式
```
[时间] [级别] [Agent] 消息
```

### 日志级别
- DEBUG: 调试信息（仅开发时使用）
- INFO: 常规操作记录
- WARNING: 需要注意的情况
- ERROR: 执行失败
- CRITICAL: 严重错误，需人工介入

### 日志存储
```yaml
log_storage:
  path: ai/logs/
  format: "{date}_{task}.md"
  retention: 30  # 保留天数
```

---

## 🔄 任务调度

### 优先级定义
```
P0: 阻塞性问题（必须立即处理）
P1: 核心功能开发
P2: 优化改进
P3: 文档/清理任务
```

### 并发控制
```yaml
concurrency:
  max_agents: 1        # 同时运行的 Agent 数量
  max_retries: 0       # 禁止自动重试
  timeout: 300         # 超时时间（秒）
```

---

## 🛡️ 错误处理

### 错误分类与处理
```yaml
SYNTAX_ERROR:
  action: FAIL
  description: 代码语法错误
  next: 报告行号和错误信息

IMPORT_ERROR:
  action: FAIL
  description: 模块导入失败
  next: 检查路径和依赖

RUNTIME_ERROR:
  action: FAIL
  description: 运行时错误
  next: 报告堆栈和上下文

TIMEOUT_ERROR:
  action: FAIL
  description: 执行超时
  next: 终止并报告

VALIDATION_ERROR:
  action: FAIL  
  description: 验证不通过
  next: 报告验证结果
```

### 失败后操作
```
1. 立即停止执行
2. 保存当前状态
3. 生成错误报告
4. 标记 FAIL
5. 等待人工决策
```

---

## 🔐 安全配置

### 权限控制
```yaml
permissions:
  read: 
    - "ai/"
    - "quark_strm/"
    - ".agent/"
  write:
    - "ai/logs/"
    - "ai/state/"
    - "quark_strm/docs/"
  execute:
    - "scripts/"
  forbidden:
    - ".git/"
    - "node_modules/"
    - "__pycache__/"
```

### 敏感信息处理
```yaml
sensitive:
  api_keys: masked
  passwords: masked
  tokens: masked
  cookies: masked
```

---

## 📁 状态文件说明

### ai/state/plan.md
当前任务计划，包含：
- 当前正在执行的任务
- 任务进度和状态
- 待完成的子任务

### ai/state/dev_summary.md
开发进度摘要，包含：
- 已完成的功能
- 进行中的工作
- 已知问题

### ai/logs/*.md
执行日志，每次任务生成一个文件

---

## 🚦 状态管理

### 执行状态
```python
STATES = {
    "INIT": "初始化，检查前置条件",
    "ANALYZING": "分析任务，定位代码",
    "EXECUTING": "执行修改",
    "VALIDATING": "验证结果",
    "SUCCESS": "成功完成",
    "FAIL": "执行失败",
    "WAITING": "等待人工决策"
}
```

### 状态转换
```
INIT → ANALYZING → EXECUTING → VALIDATING → SUCCESS
             ↓            ↓             ↓
           FAIL ←────────←────────────←
             ↓
          WAITING
```

---

## ⚡ 性能基准

### 操作超时
```yaml
timeouts:
  api_test: 5s        # API 测试
  command: 30s        # 终端命令
  file_read: 2s       # 文件读取
  total_task: 300s    # 单个任务总时间
```

### 质量指标
```yaml
quality:
  code_coverage: 80%      # 测试覆盖率目标
  max_complexity: 10      # 最大圈复杂度
  documentation: required # 文档必须
  comments: required      # 注释必须
```

---

## 📌 快速参考

### 开始任务前
```
1. 读取 agent.md
2. 读取 runner.md
3. 读取 plan.md
4. 声明角色
```

### 修改代码前
```
1. grep_search 定位
2. view_file 理解
3. 说明计划
4. 执行修改
5. 验证结果
```

### 遇到错误时
```
1. 标记 FAIL
2. 报告原因
3. 保存状态
4. 等待决策
```

### 完成任务后
```
1. 简洁报告
2. 验证结果
3. 更新状态
```

---

**维护者**: AI Engineering Team  
**版本**: v2.0  
**最后更新**: 2026-02-04
