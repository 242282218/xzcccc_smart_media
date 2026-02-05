---
name: ai-rules-sync
description: Sync smart_media SSOT rules/skills to platform directories (.trae/.lingma/.agent/.codex) and publish Codex skills to global ~/.codex/skills. Use after adding or editing any rules/agents/skills.
---

# AI Rules Sync (smart_media)

This skill keeps all AI rules/agents/skills consistent across environments by syncing from the repo SSOT (`ai/ssot/`) to platform directories and (optionally) global Codex skills.

## Quick Use

Run these from the repo root:

```powershell
python scripts/ai_rules_manager.py sync --global
python scripts/ai_rules_manager.py check
```

If you also want to verify the global install:

```powershell
python scripts/ai_rules_manager.py check --global
```

## Where to Edit (SSOT)

Only edit these locations:

- Common engineering rules: `ai/rules/`
- Trae rules/skills: `ai/ssot/platforms/trae/`
- 反重力 rules/workflows: `ai/ssot/platforms/anti/`
- Codex agent/skills: `ai/ssot/platforms/codex/`

Do **not** hand-edit generated outputs:

- `.trae/`, `.lingma/`, `.agent/`, `.codex/`, `AGENTS.md`

