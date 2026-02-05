---
name: "ai-rules-sync"
description: "Sync smart_media SSOT rules/skills to platform directories (.trae/.lingma/.agent/.codex) and publish Codex skills to global ~/.codex/skills. Invoke after changing or adding any agent/skill/rule."
---

# AI Rules Sync (smart_media)

This skill syncs the repo SSOT (`ai/ssot/`) into platform directories, so rules/skills stay consistent across Trae / 反重力 / Codex.

## When to Invoke

- You edited any rule/agent/skill under `ai/ssot/**` or `ai/rules/**`
- You added a new agent/skill/workflow file and want all platforms updated
- CI fails because SSOT outputs are out of sync

## Steps

1. Run sync (recommended to include global install):

   ```powershell
   python scripts/ai_rules_manager.py sync --global
   ```

2. Verify repo outputs are synced:

   ```powershell
   python scripts/ai_rules_manager.py check
   ```

3. (Optional) Verify global `~/.codex/skills` is synced too:

   ```powershell
   python scripts/ai_rules_manager.py check --global
   ```

