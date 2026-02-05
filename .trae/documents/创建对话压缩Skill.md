## 目标
创建一个用于压缩对话历史的Skill，减少token消耗并保留关键上下文

## Skill设计

### 基本信息
- **名称**: conversation-compressor
- **描述**: Compresses long conversation history into concise summary. Invoke when conversation exceeds 20 turns, user asks to summarize/squash context, or context window is running low.

### 功能特性
1. **自动触发**: 对话超过20轮时自动提示压缩
2. **手动触发**: 用户说"压缩对话"/"总结上文"时立即执行
3. **智能提取**: 保留关键代码、文件路径、错误信息、待办事项
4. **结构输出**: 统一的摘要格式，包含：
   - 原始请求
   - 已执行的行动
   - 当前状态
   - 关键上下文（修改的文件、运行的进程）
   - 下一步计划

### 文件创建
```
.trae/skills/conversation-compressor/SKILL.md
```

### 内容结构
- Frontmatter: name + description
- 使用时机说明
- 压缩流程（分析→提取→生成→保留）
- 输出格式模板
- 使用指南

### 验证方式
1. 创建后检查文件结构
2. 测试触发条件识别
3. 验证压缩输出格式

### 回滚路径
- 删除 .trae/skills/conversation-compressor/ 目录