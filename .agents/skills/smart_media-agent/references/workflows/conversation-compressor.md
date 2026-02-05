---
description: 压缩长对话历史为简洁摘要，保留关键上下文
---

# Conversation Compressor Workflow

来源 Skill: `.trae/skills/conversation-compressor/SKILL.md`

## 使用场景

- 对话超过 20 轮
- 用户请求 "压缩对话" / "总结上文"
- 上下文窗口接近限制

## 执行步骤

1. **分析对话结构**
   - 用户原始意图
   - AI 执行的操作
   - 关键决策点
   - 当前状态

2. **提取关键信息**
   保留:
   - 文件路径和行号
   - 代码变更
   - 命令输出和错误信息
   - 待办事项状态

   可精简:
   - 解释性文本
   - 重复尝试
   - 一般性讨论

3. **生成结构化摘要**
   ```markdown
   ## Conversation Summary
   **Original Request**: [一句话描述]
   **Current Status**: [completed / in-progress / blocked]
   **Actions Completed**: [已完成操作列表]
   **Key Technical Context**: [关键技术上下文]
   **Current Todo Status**: [待办状态]
   **Next Steps**: [下一步]
   ```

4. **用户确认**
   - 展示摘要
   - 等待确认 (Y/n)
   - 应用压缩

## 禁止事项

- ❌ 删除未解决的错误或阻塞点
- ❌ 丢失已修改文件的记录
- ❌ 删除待办任务
- ❌ 未经询问自动压缩
