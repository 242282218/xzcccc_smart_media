---
description: 对齐并同步 smart_media 的统一规则源（SSOT），确保各平台输出一致
---

# AI Rules Align Workflow

来源：`ai/ssot/`（Single Source of Truth）

## 使用场景

- 新增/修改了 Agent、规则或 Skill
- 各平台输出目录出现漂移（不同步）
- CI 提示 SSOT 未同步

## 执行步骤

1. **只改 SSOT**
   - 规则/skills 源目录：`ai/ssot/`
   - 公共工程规范：`ai/rules/`
   - 禁止手改发布产物：`.trae/`、`.lingma/`、`.agent/`、`.codex/`、`AGENTS.md`

2. **一键同步**
   ```powershell
   python scripts/ai_rules_manager.py sync --global
   ```

3. **校验**
   ```powershell
   python scripts/ai_rules_manager.py check
   ```

4. **（可选）校验全局**
   ```powershell
   python scripts/ai_rules_manager.py check --global
   ```

