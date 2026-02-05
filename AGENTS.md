# AGENTS

## 范围与目标
本文件定义本项目中 Agent 的协作边界、阶段规则与当前技能状态，作为统一执行规范。

## 协作与执行规则（优化版）
1. 多角色协作仅作为阶段划分原则存在；单次执行仅允许一个 Agent 工作，角色切换必须通过独立阶段完成。
2. 输出必须严格遵循统一模板结构；如缺失关键字段，需立即重写并通过校验后方可进入下一阶段。
3. 对话语言必须保持为中文。
4. 生成代码时必须添加函数级注释，注释需明确：用途、输入、输出与副作用。
5. 限制 Agent 自动重试：失败一次即标记 FAIL，并等待人工决策后续处理。
6. 所有 Agent 行为必须满足公司/组织规范及合规要求。
7. 测试阶段尽量减少终端命令：优先使用 Python 代码验证；终端命令如超时，必须立即退出并标记失败。

## 当前技能状态
### Codex 项目内技能（.codex/skills）
- cloudflare-deploy
- figma
- gh-fix-ci
- guidelines
- openai-docs
- playwright
- principles
- rules
- vercel-deploy

### Trae 项目内技能（.trae/skills）
- c-build-system
- ci-cd-config
- container-build
- conversation-compressor
- c-unit-test
- fe-accessibility-check
- fe-api-contract
- fe-component-map
- fe-minimal-diff
- fe-performance-check
- fe-read-only
- fe-safe-refactor
- fe-state-trace
- fe-style-guard
- fe-test-focus
- frontend-optimize
- fuzz-test-gen
- pytest-design
- python-packaging
- react-component
- test-analysis
- test-coverage
- test-design
- test-failure
- test-implement
- test-release
- vue-component

### .agents/skills
- 当前为空

## 备注
- 规则包仅作为约束与参考，不启用 agent / planner / orchestrator。
- 如需同步或变更技能，请先更新 SSOT，再执行同步流程。
