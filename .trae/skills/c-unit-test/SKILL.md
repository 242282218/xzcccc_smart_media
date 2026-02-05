---
name: c-unit-test
description: 为 C 代码设计单元测试。
---

# C Unit Test

为 C 代码设计单元测试。

## When to Invoke

- 为 C 库编写测试
- 嵌入式代码测试
- 算法验证
- 回归测试
- 持续集成

## Input Format

```yaml
source_file: "./src/utils.c"
test_framework: "CMocka"
target_platform: "x86_64"
```

## Output Format

```yaml
test_cases:
  - name: "test_string_reverse"
    description: "测试字符串反转"
    setup: "char input[] = \"hello\""
    expected: "strcmp(result, \"olleh\") == 0"
  - name: "test_null_input"
    description: "测试空指针处理"
    setup: "char* input = NULL"
    expected: "returns NULL"

test_file: |
  #include <stdarg.h>
  #include <stddef.h>
  #include <setjmp.h>
  #include <cmocka.h>
  #include "utils.h"

  static void test_string_reverse(void **state) {
      char input[] = "hello";
      char *result = string_reverse(input);
      assert_string_equal(result, "olleh");
      free(result);
  }

  static void test_null_input(void **state) {
      assert_null(string_reverse(NULL));
  }

  int main(void) {
      const struct CMUnitTest tests[] = {
          cmocka_unit_test(test_string_reverse),
          cmocka_unit_test(test_null_input),
      };
      return cmocka_run_group_tests(tests, NULL, NULL);
  }

makefile: |
  test: test_utils.c utils.c
      gcc -o test_utils test_utils.c utils.c -lcmocka
      ./test_utils

coverage_config:
  tool: "gcov"
  flags: "-fprofile-arcs -ftest-coverage"
```

## Examples

### Example 1: 数据结构测试

**Input:** 链表实现

**Output:**
- 创建/销毁测试
- 插入/删除测试
- 边界条件测试
- 内存泄漏检查

### Example 2: 硬件抽象层测试

**Input:** GPIO 驱动

**Output:**
- Mock 寄存器访问
- 状态机测试
- 时序测试
- 错误注入测试

## Best Practices

1. **隔离测试**: 每个测试独立运行
2. **内存检查**: 使用 Valgrind 检测泄漏
3. **边界测试**: 特别关注边界条件
4. **Mock 外部**: 模拟硬件和外部依赖