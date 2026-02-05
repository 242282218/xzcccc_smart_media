---
description: 设计高质量的 pytest 测试用例
---

# Pytest Design Workflow

来源 Skill: `.trae/skills/pytest-design/SKILL.md`

## 使用场景

- 为新功能编写测试
- 补充缺失的测试
- 重构测试代码
- 提高测试覆盖率
- 设计集成测试

## 执行步骤

1. **分析目标代码**
   - 理解功能逻辑
   - 识别边界条件

2. **设计测试用例**
   - 正向测试
   - 边界条件测试
   - 异常处理测试

3. **设计 Fixture**
   - 确定 scope（function/class/session）
   - 设计 mock 策略

4. **编写测试代码**
   - 遵循 AAA 模式
   - 一个概念一个测试

5. **验证覆盖率**
   - 运行测试
   - 检查覆盖率报告

## 最佳实践

1. **AAA 模式**: Arrange-Act-Assert
2. **一个概念一个测试**: 每个测试验证一个概念
3. **可读性优先**: 测试代码应该像文档
4. **快速反馈**: 测试应该在毫秒内完成
