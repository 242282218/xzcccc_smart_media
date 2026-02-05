---
description: 配置 C/C++ 项目的构建系统
---

# C Build System Workflow

来源 Skill: `.trae/skills/c-build-system/SKILL.md`

## 使用场景

- 新项目搭建构建系统
- 迁移构建工具
- 设置交叉编译
- 优化构建速度
- 集成到 CI

## 执行步骤

1. **分析项目结构**
   - 确定项目类型（executable / library）
   - 识别目标平台
   - 列出外部依赖

2. **生成 CMake 配置**
   - 创建 CMakeLists.txt
   - 配置编译选项
   - 设置依赖查找

3. **配置构建脚本**
   - 创建 build.sh / build.bat
   - 设置并行编译
   - 配置缓存优化

4. **验证构建**
   - 执行完整构建
   - 运行测试
   - 检查输出产物

## 最佳实践

1. **现代 CMake**: 使用目标导向的 CMake
2. **依赖管理**: 使用 find_package 或 FetchContent
3. **编译选项**: 区分 Debug/Release
4. **可移植性**: 避免平台特定代码
