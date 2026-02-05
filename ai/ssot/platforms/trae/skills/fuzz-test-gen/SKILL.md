---
name: fuzz-test-gen
description: 生成模糊测试用例，发现边界漏洞。
---

# Fuzz Test Generator

生成模糊测试用例，发现边界漏洞。

## When to Invoke

- 安全敏感代码测试
- 解析器/解码器测试
- 网络协议实现
- 文件格式处理
- 发现内存安全问题

## Input Format

```yaml
target_function: "parse_json"
fuzzer: "LibFuzzer"
duration: "1h"
```

## Output Format

```yaml
fuzz_harness: |
  #include <stdint.h>
  #include <stddef.h>
  #include "json_parser.h"

  extern "C" int LLVMFuzzerTestOneInput(const uint8_t *data, size_t size) {
      char *input = (char*)malloc(size + 1);
      memcpy(input, data, size);
      input[size] = '\0';
      
      parse_json(input);  // 目标函数
      
      free(input);
      return 0;
  }

corpus:
  - "{}"
  - '{"key": "value"}'
  - "[]"
  - "null"
  - "123"

crash_report:
  - crash_id: "CRASH-001"
    input: '{"\\\\\\\\": 1}'
    type: "heap-buffer-overflow"
    stacktrace: |
      #0 parse_string
      #1 parse_object
      #2 parse_json
    severity: "high"

fix_recommendation:
  - issue: "缺少长度检查"
    location: "parser.c:45"
    fix: "添加边界检查"
```

## Examples

### Example 1: JSON 解析器模糊测试

**Input:** JSON 解析库

**Output:**
- 畸形 JSON 测试
- 嵌套深度测试
- Unicode 边界测试
- 内存泄漏检测

### Example 2: 图像解码器模糊测试

**Input:** PNG 解码库

**Output:**
- 畸形图像测试
- 压缩炸弹防护
- 缓冲区溢出检测
- 资源耗尽测试

## Best Practices

1. **语料库质量**: 提供多样化的初始输入
2. **持续运行**: 模糊测试应该持续运行
3. **崩溃分析**: 每个崩溃都要分析修复
4. **回归测试**: 崩溃样本加入回归测试