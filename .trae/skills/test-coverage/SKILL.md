---
name: test-coverage
description: 分析和提升代码测试覆盖率。
---

# Test Coverage

分析和提升代码测试覆盖率。

## When to Invoke

- 评估测试完整性
- 发现测试缺口
- CI/CD 门禁检查
- 发布前验证
- 持续改进

## Input Format

```yaml
project_path: "./src"
coverage_tool: "coverage.py"
target_coverage: 0.85
```

## Output Format

```yaml
coverage_report:
  overall:
    line_coverage: 0.82
    branch_coverage: 0.75
    function_coverage: 0.90
  by_module:
    - name: "auth"
      line_coverage: 0.95
      status: "good"
    - name: "utils"
      line_coverage: 0.45
      status: "needs_improvement"

uncovered_lines:
  - file: "utils.py"
    lines: [45, 46, 78-82]
    reason: "error handling paths"
  - file: "api.py"
    lines: [120-125]
    reason: "edge case conditions"

gap_analysis:
  critical_gaps:
    - location: "payment/process.py"
      risk: "high"
      reason: "核心业务逻辑未覆盖"
  low_priority:
    - location: "debug/logging.py"
      risk: "low"
      reason: "调试代码"

improvement_plan:
  - priority: "high"
    action: "添加 payment 模块测试"
    estimated_tests: 10
    expected_coverage: 0.90
```

## Examples

### Example 1: Python 项目覆盖率

**Input:** Django Web 应用

**Output:**
- 视图层覆盖率分析
- 模型层测试缺口
- 异常处理覆盖情况
- 测试优先级建议

### Example 2: C 项目覆盖率

**Input:** 嵌入式固件

**Output:**
- 函数覆盖情况
- 分支覆盖分析
- 死代码识别
- 关键路径覆盖建议

## Best Practices

1. **质量优于数量**: 100% 覆盖不等于无 bug
2. **关注边界**: 优先覆盖边界和异常
3. **持续监控**: 集成到 CI/CD
4. **增量检查**: 新代码必须覆盖