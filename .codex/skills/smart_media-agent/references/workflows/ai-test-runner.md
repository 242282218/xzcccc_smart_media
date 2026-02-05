---
description: 统一使用 scripts/run_tests.py 执行测试，输出 logs/test，并禁用交互式 shell。
---

# AI Test Runner Workflow

## 使用场景

- 需要运行测试或分析失败用例
- 需要统一日志与动态超时
- 需要强制容器/CI 执行

## 执行步骤

1. 确认配置存在：
   - `ai/test_config.yaml`
2. 运行测试入口：
   ```powershell
   python scripts/run_tests.py --suite fast
   ```
3. 查看日志：
   - `logs/test/summary.json`
   - `logs/test/stdout.log`
   - `logs/test/stderr.log`
   - `logs/test/junit.xml`

## 禁止事项

- 禁止直接运行 pytest/npm test
- 禁止进入交互式 shell
