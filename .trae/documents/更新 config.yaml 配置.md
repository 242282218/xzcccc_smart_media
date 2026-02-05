## 任务目标
将历史指令.md 中的配置信息写入 config.yaml

## 已阅读文件
- ai/rules/agent.md
- ai/runner.md
- ai/state/plan.md
- quark_strm/config.yaml

## 配置映射
根据历史指令.md L52-64 提取的配置：

| 源配置项 | 目标配置路径 | 值 |
|---------|-------------|-----|
| tgbot_token | telegram.bot_token | 5807378696:AAHDfl1nCtTkhk9bvtvog3cjwByYjgv0grE |
| user_id | telegram.chat_id | 5675490499 |
| tmdb_key | tmdb.api_key | 7b260e96dd9e320fa427eab26fbbf528 |
| emby_url | emby.url | http://192.168.100.66:18096/ |
| emb_key | emby.api_key | 0be957f3e00f4133b550efa05df5b3bc |
| 智谱ai_key | zhipu.api_key | 62aac2d7a5fe40e7b24e0d51a119c75c.UA3mC0lj6EB3ZUrb |
| 夸克cookie | quark.cookie | (完整cookie字符串) |

## 执行步骤
1. 更新 telegram.enabled 为 true
2. 更新 telegram.bot_token 和 telegram.chat_id
3. 添加 tmdb 配置节
4. 添加 emby 配置节
5. 添加 zhipu 配置节
6. 添加 quark 配置节

## 约束范围
- 仅修改: quark_strm/config.yaml
- 禁止修改: 其他所有文件

## 回滚方案
```bash
git checkout quark_strm/config.yaml
```