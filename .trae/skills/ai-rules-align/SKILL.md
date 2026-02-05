---
name: "ai-rules-align"
description: "Sync and align smart_media SSOT rules/agents/skills across Trae, Codex, Antigrity, and Lingma. Invoke after changing any rules or skills."
---

# AI Rules Align (smart_media)

Sync SSOT (`ai/ssot/`) to all platform output directories and verify alignment.

## When to Invoke

- You edited any file under `ai/ssot/**` or `ai/rules/**`
- Output files drifted (`.trae/`, `.lingma/`, `.agent/`, `.codex/`)
- CI check failed for SSOT sync

## Steps

1. **Sync**
   ```powershell
   python scripts/ai_rules_manager.py sync --global
   ```

2. **Check**
   ```powershell
   python scripts/ai_rules_manager.py check
   ```

3. **(Optional) Check global**
   ```powershell
   python scripts/ai_rules_manager.py check --global
   ```

