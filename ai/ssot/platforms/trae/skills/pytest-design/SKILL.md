---
name: pytest-design
description: 设计高质量的 pytest 测试用例。
---

# Pytest Design

设计高质量的 pytest 测试用例。

## When to Invoke

- 为新功能编写测试
- 补充缺失的测试
- 重构测试代码
- 提高测试覆盖率
- 设计集成测试

## Input Format

```yaml
code_path: "./src/calculator.py"
test_focus: "边界条件和异常处理"
coverage_target: 0.9
```

## Output Format

```yaml
test_cases:
  - name: "test_add_positive_numbers"
    description: "测试正数相加"
    input: "add(2, 3)"
    expected: "5"
    type: "unit"
  - name: "test_add_negative_numbers"
    description: "测试负数相加"
    input: "add(-2, -3)"
    expected: "-5"
    type: "unit"
  - name: "test_add_overflow"
    description: "测试溢出异常"
    input: "add(MAX_INT, 1)"
    expected: "OverflowError"
    type: "exception"

fixture_design:
  - name: "calculator"
    scope: "function"
    description: "每个测试创建新的 calculator 实例"
  - name: "mock_db"
    scope: "session"
    description: "共享的 mock 数据库"

mock_strategy:
  - target: "external_api.call"
    method: "patch"
    return_value: "{\"status\": \"ok\"}"

test_file: |
  import pytest
  from calculator import add

  def test_add_positive_numbers():
      assert add(2, 3) == 5

  def test_add_negative_numbers():
      assert add(-2, -3) == -5

  def test_add_overflow():
      with pytest.raises(OverflowError):
          add(MAX_INT, 1)
```

## Examples

### Example 1: API 测试

**Input:** REST API 端点

**Output:**
- 正常请求测试
- 参数验证测试
- 认证授权测试
- 错误处理测试

### Example 2: 数据库操作测试

**Input:** ORM 模型操作

**Output:**
- CRUD 测试
- 事务回滚测试
- 并发测试
- Fixture 设计

## Best Practices

1. **AAA 模式**: Arrange-Act-Assert
2. **一个概念一个测试**: 每个测试验证一个概念
3. **可读性优先**: 测试代码应该像文档
4. **快速反馈**: 测试应该在毫秒内完成