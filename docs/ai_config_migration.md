# AI 配置迁移指南

## 新配置格式（OpenAI 兼容）

```yaml
ai:
  providers:
    - name: "deepseek"
      api_key: "sk-xxx"
      base_url: "https://api.deepseek.com/v1"
      model: "deepseek-chat"
      timeout: 20
      enabled: true
      priority: 100

    - name: "glm"
      api_key: "sk-yyy"
      base_url: "https://open.bigmodel.cn/api/paas/v4"
      model: "glm-4-flash"
      timeout: 15
      enabled: true
      priority: 90

    - name: "openai"
      api_key: "sk-zzz"
      base_url: "https://api.openai.com/v1"
      model: "gpt-4o-mini"
      timeout: 30
      enabled: true
      priority: 80

  max_retries: 3
  fallback_enabled: true
```

## 旧配置格式（已弃用）

```yaml
deepseek:
  api_key: "sk-xxx"
  base_url: "https://api.deepseek.com/v1"
  model: "deepseek-chat"
  timeout: 20

glm:
  api_key: "sk-yyy"
  base_url: "https://open.bigmodel.cn/api/paas/v4"
  model: "glm-4-flash"
  timeout: 15
```

## 迁移步骤

1. **备份现有配置**
   ```bash
   cp config.yaml config.yaml.backup
   ```

2. **转换为新格式**
   - 将每个旧配置转换为 `ai.providers` 列表项
   - 添加 `name` 和 `priority` 字段
   - 设置 `enabled: true`

3. **测试新配置**
   ```bash
   python -m app.services.unified_ai_service
   ```

4. **删除旧配置**（可选）
   - 确认新配置工作正常后，可删除 `deepseek`, `glm`, `kimi`, `zhipu` 配置

## 优势

✅ **统一接口**：所有 AI 模型使用相同配置格式
✅ **自动 Fallback**：按优先级自动切换
✅ **易于扩展**：添加新模型只需增加配置项
✅ **OpenAI 兼容**：支持任意 OpenAI 兼容 API

## 支持的模型

- OpenAI (GPT-4, GPT-3.5)
- DeepSeek
- GLM (智谱)
- Kimi
- Claude (通过 OpenAI 兼容接口)
- 其他 OpenAI 兼容服务
