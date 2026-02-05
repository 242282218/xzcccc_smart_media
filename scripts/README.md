# 脚本工具说明

本目录包含项目使用的各种脚本工具。

## 目录结构

### 🚀 部署脚本 (deployment/)
- `backup.bat` - Windows 备份脚本
- `backup.sh` - Linux/Mac 备份脚本
- `start-all.bat` - 启动所有服务
- `stop-all.bat` - 停止所有服务

### 🔒 安全脚本 (security/)
- `encrypt_config.py` - 配置文件加密工具

### 🛠️ 工具脚本 (utils/)
- `cat_log.py` - 日志查看工具

## 测试脚本

- `run_tests.py` - 统一测试入口（读取 `ai/test_config.yaml`，输出到 `logs/test/`）

## 使用说明

请根据具体需求选择相应的脚本工具使用。
