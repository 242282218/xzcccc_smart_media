# AI 规则与 Skills（SSOT）

本目录是 smart_media 项目的 **Single Source of Truth**（唯一事实源）。

目标：在 **反重力 / VS Code Codex / Trae / Codex CLI** 多环境开发时，只维护一份规则与技能，然后一键同步到各平台要求的目录。

## 目录约定

- `ai/ssot/platforms/trae/`：Trae 使用的规则与 skills（同步到 `.trae/`）
- `ai/ssot/platforms/anti/`：反重力使用的规则与 workflows（同步到 `.lingma/` 和 `.agent/`）
- `ai/ssot/platforms/codex/`：Codex 使用的入口 Agent 与 skills（同步到 `AGENTS.md` 与 `.codex/`，并可发布到全局 `~/.codex/skills`）

## 一键同步/校验

```powershell
python scripts/ai_rules_manager.py sync --global
python scripts/ai_rules_manager.py check
```

说明：
- `sync`：从 `ai/ssot/` 发布到各平台目录
- `check`：校验当前工作区是否已同步（CI 会跑）
- `--global`：额外发布到全局 `~/.codex/skills`

## 修改规则

只允许修改 `ai/ssot/**` 与 `ai/rules/**`（公共规则）。
各平台目录（如 `.trae/`、`.lingma/`、`.agent/`、`.codex/`）视为 **发布产物**，禁止手改。

