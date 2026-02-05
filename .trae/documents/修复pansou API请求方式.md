## 问题根源

pansou API 的 **POST 方式有 bug**，导致忽略 `kw` 参数，返回固定结果集。

**GET 方式正常工作**，返回82条"流浪地球"相关结果。

## 修复方案

修改 `quark_strm/app/services/search_service.py`：

1. 将 POST 请求改为 GET 请求
2. 将 JSON 参数改为 URL 查询参数
3. 保持其他逻辑不变

## 修改内容

```python
# 修改前（POST）
response = await client.post(
    self._get_pansou_url("/api/search"),
    json=params
)

# 修改后（GET）
response = await client.get(
    self._get_pansou_url("/api/search"),
    params=params
)
```

请确认是否执行？