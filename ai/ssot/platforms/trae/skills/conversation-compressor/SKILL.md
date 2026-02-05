---
name: "conversation-compressor"
description: "Compresses long conversation history into concise summary. Invoke when conversation exceeds 20 turns, user asks to summarize/squash context, or context window is running low."
---

# Conversation Compressor

This skill compresses conversation history while preserving essential context for continued work.

## When to Invoke

- **Automatic**: Conversation exceeds 20 message exchanges
- **Manual**: User explicitly says:
  - "压缩对话" / "压缩上下文"
  - "总结上文" / "summarize conversation"
  - "squash context" / "compress history"
  - "对话太长了" / "context too long"
- **Emergency**: Context window approaching limit (warning signs: slower responses, truncated outputs)

## Compression Process

### Step 1: Analyze Conversation Structure
Identify and categorize:
- **User's Original Intent**: What did the user initially want to achieve?
- **AI Actions**: What steps were taken? (files read, modified, commands executed)
- **Key Decisions**: Important choices made during the conversation
- **Current State**: Where are we now? (completed/pending/blocked)
- **Technical Context**: File paths, code snippets, error messages, configurations

### Step 2: Extract Critical Information

**Must Preserve**:
- File paths and line numbers referenced
- Code changes (functions, classes, key logic)
- Command outputs and error messages (if unresolved)
- Configuration changes
- Test results and verification status
- Todo list items and their status

**Can Summarize**:
- Explanatory text and educational content
- Repeated attempts or iterations
- Successful verifications (keep result only)
- General discussion

### Step 3: Generate Structured Summary

Use this exact format:

```markdown
## Conversation Summary

**Original Request**: [One-line description of user's goal]

**Current Status**: [completed / in-progress / blocked / needs-verification]

**Actions Completed**:
1. [Action]: [Brief result] → [File/Location affected]
2. [Action]: [Brief result] → [File/Location affected]
...

**Key Technical Context**:
- **Modified Files**: [list with brief description of changes]
- **Running Processes**: [if any]
- **Environment**: [relevant config, ports, versions]
- **Unresolved Issues**: [errors or blockers needing attention]

**Current Todo Status**:
- [x] Completed: [task]
- [ ] Pending: [task]
- [ ] Blocked: [task] (reason: ...)

**Next Steps**: [What should happen next]

**Important Notes**:
- [Any critical info not covered above]
```

### Step 4: User Confirmation

Before applying compression:
1. Present the generated summary
2. Ask: "是否确认压缩对话？这将保留上述关键信息，删除详细历史。"
3. Wait for user confirmation (Y/n)
4. If confirmed, replace conversation context with summary

## Guidelines

### Do's
- ✅ Keep all file paths exact and complete
- ✅ Preserve error messages if issue not resolved
- ✅ Maintain todo list with accurate status
- ✅ Include verification results (pass/fail)
- ✅ Note any external dependencies or requirements

### Don'ts
- ❌ Remove unresolved errors or blockers
- ❌ Lose track of modified files
- ❌ Delete pending tasks without noting them
- ❌ Compress if user explicitly wants full history
- ❌ Auto-compress without asking (unless emergency)

## Example

**Before Compression** (25 messages):
- User: Help me fix this bug
- AI: Let me check the file
- [10 messages of investigation]
- AI: Found the issue on line 45
- [5 messages of explaining the fix]
- AI: Fixed, please test
- User: Works great!
- [5 messages of discussion]

**After Compression**:
```markdown
## Conversation Summary

**Original Request**: Fix bug in authentication module

**Current Status**: completed

**Actions Completed**:
1. Investigated auth.py → Found null pointer on line 45
2. Applied fix: Added null check → auth.py#L45-48
3. Verified fix works → User confirmed

**Key Technical Context**:
- **Modified Files**: auth.py (added null check at line 45)
- **Environment**: Python 3.9, FastAPI
- **Unresolved Issues**: None

**Current Todo Status**:
- [x] Completed: Fix auth bug

**Next Steps**: None - task complete
```

## Emergency Compression

If context window is critically low:
1. Skip user confirmation
2. Auto-generate summary
3. Notify user: "[系统自动压缩对话以节省上下文空间]"
4. Include compressed summary in next response
