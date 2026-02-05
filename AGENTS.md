# smart_media 统一入口 Agent（Codex / VS Code）

## 单一事实源（SSOT）

- 规则与 skills 的唯一事实源在：`ai/ssot/`
- 公共工程执行规范在：`ai/rules/`
- 平台目录（`.trae/`、`.lingma/`、`.agent/`、`.codex/`）为发布产物，禁止手改；请改 SSOT 后运行同步脚本。

## 开始任何工程任务前（必读）

请先阅读并遵循以下文件（若缺失请提示“前置条件不足”并停止）：

- `ai/rules/agent.md`
- `ai/runner.md`
- `ai/state/plan.md`

## 同步与校验（强制）

当你新增/修改了任何规则、Agent 或 Skill 后，必须执行：

```powershell
python scripts/ai_rules_manager.py sync --global
python scripts/ai_rules_manager.py check
```

CI 会运行 `check`，未同步将导致失败。

