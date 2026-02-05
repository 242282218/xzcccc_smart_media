# 更新配置并详细测试后端API

## 执行步骤

### 1. 更新 config.yaml
在文件末尾添加API密钥配置：
```yaml
# API密钥配置
api_keys:
  ai_api_key: "62aac2d7a5fe40e7b24e0d51a119c75c.UA3mC0lj6EB3ZUrb"
  tmdb_api_key: "7b260e96dd9e320fa427eab26fbbf528"
```

### 2. 更新 sdk_config.py
修改SDKConfig类，从config.yaml读取API密钥：
- 添加配置管理器导入
- 从配置文件读取api_keys
- 优先使用配置文件中的密钥，其次环境变量

### 3. 详细测试后端API
运行以下测试：
- GET /api/quark-sdk/status - SDK状态
- GET /api/quark-sdk/files/0 - 文件列表
- GET /api/search/status - 搜索服务状态
- GET /api/rename/status - 重命名服务状态
- 验证API密钥是否正确加载

### 4. 验证集成
- 确保所有新端点正常工作
- 验证现有API不受影响
- 检查日志输出

请确认后开始执行。