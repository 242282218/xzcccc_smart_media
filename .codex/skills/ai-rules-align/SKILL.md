---
name: ai-rules-align
description: Sync and align smart_media SSOT rules/agents/skills across Codex, Trae, Antigrity, and Lingma. Use after adding or editing any rules, agents, skills, or workflows.
---

# AI Rules Align (smart_media)

Keep all rule/agent/skill files consistent by syncing from SSOT to platform outputs and verifying alignment.

## When to Invoke

- You added/edited anything under `ai/ssot/**` or `ai/rules/**`
- A platform output file was changed (e.g., `.trae/`, `.lingma/`, `.agent/`, `.codex/`)
- CI reports SSOT outputs are out of sync

## Steps (Low Freedom)

1. **Edit only SSOT**
   - Source of truth: `ai/ssot/**` and `ai/rules/**`
   - Do **not** hand-edit generated outputs

2. **Sync to all platforms**
   ```powershell
   python scripts/ai_rules_manager.py sync --global
   ```

3. **Verify alignment**
   ```powershell
   python scripts/ai_rules_manager.py check
   ```

4. **(Optional) Verify global install**
   ```powershell
   python scripts/ai_rules_manager.py check --global
   ```

## Expected Output

- `sync` prints `Synced...` or `Already in sync.`
- `check` prints `OK: SSOT outputs are in sync.`

