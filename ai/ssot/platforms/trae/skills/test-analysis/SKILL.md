---
name: test-analysis
description: "# When To Use
当需要整体了解当前测试体系、覆盖范围、测试缺口或环境差异时。"
---

# Description
测试分析模式，用于评估测试现状与风险。
不新增、不修改任何测试或代码。

# Instructions
从工程视角分析测试体系。

## Analysis Scope
- 测试类型分布（unit / integration / e2e）
- 覆盖范围与未覆盖逻辑
- 测试工具与框架
- 本地 / CI / 预发布环境差异

# Output Contract
- 测试现状概览
- 关键测试缺口
- 高风险区域
- 环境差异说明

# Forbidden
- 不修改代码
- 不修改测试
- 不执行命令