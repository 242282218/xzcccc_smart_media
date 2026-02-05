---
name: test-release
description: "# When To Use
版本发布、合并或上线前。"
---

# Description
测试放行评估模式，从测试视角判断发布风险。

# Instructions
基于测试结果与改动范围进行回归与放行评估。

## Evaluation Scope
- 已执行测试情况
- 关键回归点
- 已知风险

# Output Contract
- 当前测试状态
- 回归覆盖结论
- 放行建议（Yes / Conditional / No）

# Forbidden
- 不修改代码
- 不修改测试