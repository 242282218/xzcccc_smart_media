## 修复方案

### 目标
将 sdk_config.py 中的 Telegram 频道配置从4个扩展到全部39个频道，支持多种网盘类型。

### 执行步骤

#### 步骤1: 修改 sdk_config.py
**文件**: `quark_strm/app/core/sdk_config.py`
- 修改 `create_search_service` 方法
- Telegram 配置改为从 channels.json 加载所有频道
- 或者直接在代码中配置所有39个频道

#### 步骤2: 验证配置
- 检查配置是否正确加载
- 确保所有频道都被启用

#### 步骤3: 清理缓存并测试
- 清理搜索缓存
- 运行聚合搜索测试
- 验证是否返回多种网盘类型

### 修改内容
将 Telegram 配置从：
```python
"telegram": {
    "enabled": True,
    "channels": [
        {"id": "yunpanshare", "name": "云盘分享", "enabled": True},
        {"id": "alyp_1", "name": "阿里云盘分享", "enabled": True},
        {"id": "Quarkyunpan", "name": "夸克云盘", "enabled": True},
        {"id": "baidu_pan_share", "name": "百度网盘分享", "enabled": True},
    ]
}
```

改为使用 channels.json 中的所有39个频道。

请确认此方案。