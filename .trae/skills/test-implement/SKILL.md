---
name: test-implement
description: "# When To Use
需要补充测试以覆盖关键路径或降低回归风险时。"
---

# Description
测试实现模式，以最小代价补充关键测试。

# Instructions
只新增与风险直接相关的测试。

## Implementation Rules
- 测试数量最小化
- 覆盖关键逻辑
- 不重构生产代码

# Output Contract
- 新增测试说明
- 覆盖点说明

# Forbidden
- 不重构业务代码
- 不大规模重写测试