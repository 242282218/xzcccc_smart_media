---
description: 同步 smart_media 的统一规则源（SSOT）到各平台目录，并发布到全局 ~/.agents/skills
---

# AI Rules Sync Workflow

来源：`ai/ssot/`（Single Source of Truth）

## 使用场景

- 新增/修改了 Agent、规则或 Skill
- `.trae/` / `.lingma/` / `.agent/` / `.agents/` 出现漂移（不同步）
- CI 提示 SSOT 未同步

## 执行步骤

1. **只改 SSOT**
   - 规则/skills 的源目录：`ai/ssot/`
   - 公共工程规范：`ai/rules/`
   - 禁止手改发布产物：`.trae/`、`.lingma/`、`.agent/`、`.agents/`、`AGENTS.md`

2. **一键同步（含全局）**
   ```powershell
   python scripts/ai_rules_manager.py sync --global
   ```

3. **校验（仓库）**
   ```powershell
   python scripts/ai_rules_manager.py check
   ```

4. **（可选）校验全局安装**
   ```powershell
   python scripts/ai_rules_manager.py check --global
   ```

5. **提交**
   - 提交变更（SSOT + 发布产物）
   - 确保 CI 通过

