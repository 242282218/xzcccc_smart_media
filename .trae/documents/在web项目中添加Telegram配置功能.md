## 目标
在实际的web项目配置页面(ConfigView.vue)中添加Telegram消息推送配置功能

## 问题分析
- 启动脚本使用的是 `quark_strm/web` 目录
- 我之前修改的是 `quark_strm/frontend` 目录（错误的目录）
- 实际的配置页面是 `web/src/views/ConfigView.vue`
- 当前ConfigView.vue缺少Telegram配置选项

## 涉及文件
1. `quark_strm/web/src/views/ConfigView.vue` - 主配置页面，需要添加Telegram配置标签页
2. `quark_strm/web/src/api/config.ts` - 检查API接口是否支持Telegram配置

## 修改步骤

### 步骤1: 检查config.ts API文件
确认是否有Telegram相关的API接口

### 步骤2: 在ConfigView.vue中添加Telegram配置标签页
- 添加新的"消息通知"标签页
- 添加Telegram配置表单（Bot Token、Chat ID、代理、启用开关）
- 添加测试推送功能
- 统一与现有配置相同的视觉风格

### 步骤3: 同步配置数据
- 在fetchConfig中加载Telegram配置
- 在saveConfig中保存Telegram配置

## 风险点
- 需要确保与现有配置数据结构兼容
- 保持与现有UI风格一致
- 不影响其他配置功能