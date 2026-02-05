---
name: c-build-system
description: 配置 C/C++ 项目的构建系统。
---

# C Build System

配置 C/C++ 项目的构建系统。

## When to Invoke

- 新项目搭建构建系统
- 迁移构建工具
- 设置交叉编译
- 优化构建速度
- 集成到 CI

## Input Format

```yaml
project_type: "executable"
target_platform: "linux_x86_64"
dependencies:
  - "libssl"
  - "libcurl"
```

## Output Format

```yaml
build_config: |
  cmake_minimum_required(VERSION 3.15)
  project(MyProject VERSION 1.0.0 LANGUAGES C)
  
  # 设置 C 标准
  set(CMAKE_C_STANDARD 11)
  set(CMAKE_C_STANDARD_REQUIRED ON)
  
  # 查找依赖
  find_package(OpenSSL REQUIRED)
  find_package(CURL REQUIRED)
  
  # 添加可执行文件
  add_executable(myapp
      src/main.c
      src/utils.c
      src/network.c
  )
  
  # 链接库
  target_link_libraries(myapp
      OpenSSL::SSL
      CURL::libcurl
  )
  
  # 包含目录
  target_include_directories(myapp PRIVATE
      ${CMAKE_SOURCE_DIR}/include
  )
  
  # 编译选项
  target_compile_options(myapp PRIVATE
      -Wall -Wextra -O2
  )
  
  # 安装规则
  install(TARGETS myapp DESTINATION bin)

build_script: |
  #!/bin/bash
  mkdir -p build && cd build
  cmake ..
  cmake --build . --parallel
  ctest --output-on-failure

optimization:
  - "使用 ccache 加速编译"
  - "启用并行编译 (-j)"
  - "使用 Ninja 替代 Make"
  - "预编译头文件"

ci_integration: |
  # GitHub Actions 示例
  - name: Build
    run: |
      mkdir build && cd build
      cmake ..
      cmake --build . --config Release
```

## Examples

### Example 1: 可执行程序

**Input:** CLI 工具

**Output:**
- CMakeLists.txt
- 依赖查找
- 编译选项
- 安装规则

### Example 2: 库项目

**Input:** 共享库

**Output:**
- 静态/动态库构建
- 头文件安装
- pkg-config 配置
- 版本符号

## Best Practices

1. **现代 CMake**: 使用目标导向的 CMake
2. **依赖管理**: 使用 find_package 或 FetchContent
3. **编译选项**: 区分 Debug/Release
4. **可移植性**: 避免平台特定代码