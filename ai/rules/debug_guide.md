# AI 调试指南 - 常见问题与解决方法

## 📋 文档信息
- **版本**: v1.0
- **更新时间**: 2026-02-04
- **用途**: 记录AI开发中的典型错误和正确做法

---

## 🐛 前端问题

### P1: API URL 重复前缀
**症状**: 请求变成 `/api/api/xxx`
```
❌ Request URL: http://localhost:3000/api/api/quark/browse
```

**原因**: axios 的 `baseURL` 和请求路径都包含 `/api`

**排查方法**:
```typescript
// 检查 api/index.ts
const api = axios.create({
  baseURL: '/api',  // 已经有 /api
})

// 检查调用代码
api.get('/api/quark/browse')  // ❌ 多了一个 /api
api.get('/quark/browse')      // ✅ 正确
```

**解决方法**: 请求路径不要再加 `/api` 前缀

---

### P2: 响应数据层级错误
**症状**: `response.items` 是 `undefined`

**原因**: 不理解响应拦截器的返回值

**排查方法**:
```typescript
// 1. 检查拦截器
api.interceptors.response.use(
  (response) => response.data,  // 返回 response.data
  ...
)

// 2. 检查后端返回格式
// 后端返回: { status: 200, data: { items: [...] } }

// 3. 经过拦截器后
// 前端收到: { status: 200, data: { items: [...] } }

// 4. 正确访问方式
response.data.items  // ✅ 正确
response.items       // ❌ 错误
```

**解决方法**: 理解数据流，正确访问层级

---

### P3: 菜单路由不匹配
**症状**: 点击菜单无反应或跳错页面

**原因**: 菜单配置的 path 和 router 配置不一致

**排查方法**:
```typescript
// 检查 router/index.ts
{ path: '/smart-rename', component: SmartRenameView }

// 检查 LayoutView.vue 菜单配置
{ path: '/rename', title: '智能重命名' }  // ❌ 不匹配

// 修正
{ path: '/smart-rename', title: '智能重命名' }  // ✅ 匹配
```

---

### P4: 浏览器缓存问题
**症状**: 代码已修改但页面行为不变

**解决方法**:
1. `Ctrl + Shift + R` 强制刷新
2. `F12` → 右键刷新按钮 → "清空缓存并硬性重新加载"
3. 无痕模式测试
4. 重启开发服务器

---

### P5: TypeScript 类型错误
**症状**: 编译警告或运行时类型错误

**临时解决**: 使用 `any` 类型
```typescript
// 快速修复
const response = await api.get<any>('/quark/browse', ...)

// 正确做法：后续补充完整类型
interface QuarkBrowseResponse {
  status: number
  data: {
    items: QuarkFileItem[]
    total: number
  }
}
```

---

## 🐛 后端问题

### P6: 导入模块失败
**症状**: `ModuleNotFoundError` 或 `ImportError`

**排查方法**:
```python
# 1. 检查模块是否存在
ls app/services/xxx_service.py

# 2. 检查 __init__.py
cat app/services/__init__.py

# 3. 检查导入路径
from app.services.xxx_service import XxxService  # 绝对路径
from .xxx_service import XxxService  # 相对路径
```

**常见原因**:
- 文件不存在
- `__init__.py` 缺失
- 循环导入
- 相对/绝对路径混用

---

### P7: API 端点未生效
**症状**: 404 Not Found

**排查方法**:
```python
# 1. 确认路由已注册
# main.py
app.include_router(quark_router, prefix="/api/quark")

# 2. 确认端点定义
# api/quark.py
@router.get("/browse")
async def browse_quark_directory(...):

# 3. 检查完整路径
# 最终路径 = prefix + endpoint = /api/quark/browse
```

---

### P8: uvicorn 没有重载
**症状**: 代码修改后行为不变

**检查**:
```bash
# 确认使用 --reload 参数
uvicorn app.main:app --reload --port 8000

# 查看终端日志，应该显示
# WARNING:  watchfiles detected changes in 'app/xxx.py'. Reloading...
```

**可能原因**:
- 没有使用 `--reload`
- 文件在监控目录外
- 语法错误导致重载失败

---

### P9: Cookie/认证失败
**症状**: 401 Unauthorized 或 API 返回未登录

**排查**:
```python
# 1. 检查配置文件
cat config.yaml | grep cookie

# 2. 测试 Cookie 有效性
python -c "
import requests
r = requests.get('http://localhost:8000/api/quark/browse?pdir_fid=0')
print(r.status_code, r.text[:200])
"
```

---

### P10: 递归逻辑问题
**症状**: 选项开关无效果

**排查**:
```python
# 1. 确认前端传递参数
console.log('递归选项:', options.recursive)

# 2. 确认后端接收参数
logger.info(f"递归={request.options.get('recursive')}")

# 3. 确认逻辑实现
if recursive:
    # 递归处理
else:
    # 只处理当前目录
```

---

## 🔧 调试技巧

### T1: 添加临时日志
```python
# 后端
logger.info(f"[DEBUG] 变量值: {variable}")

# 前端
console.log('[DEBUG] 响应:', response)
```

### T2: 创建测试页面
```html
<!-- public/test-xxx.html -->
<script>
fetch('/api/quark/browse?pdir_fid=0')
  .then(r => r.json())
  .then(data => console.log('API响应:', data))
</script>
```

### T3: 使用 curl 测试
```bash
# Windows PowerShell
python -c "import requests; print(requests.get('http://localhost:8000/api/xxx').text)"

# 或者
Invoke-WebRequest -Uri "http://localhost:8000/api/xxx" | Select-Object -ExpandProperty Content
```

### T4: 检查网络请求
1. 按 F12 打开开发者工具
2. 切换到 Network 选项卡
3. 刷新页面
4. 查看请求的 URL、Status、Response

---

## ✅ 验证清单

### 前端修改后
```
□ 代码语法正确（无红色波浪线）
□ 终端无编译错误
□ 浏览器控制台无报错
□ 网络请求正确发送
□ 页面功能正常
```

### 后端修改后
```
□ uvicorn 成功重载（查看终端）
□ 无 ImportError
□ API 返回正确状态码
□ 日志正常输出
□ 数据格式正确
```

---

## 📌 常用命令

```bash
# 测试后端 API
python -c "import requests; r = requests.get('http://localhost:8000/api/xxx'); print(r.status_code, r.text[:500])"

# 查看后端日志
Get-Content logs/quark_strm.log -Tail 50

# 重启前端
cd web; npm run dev

# 检查进程
Get-Process -Name node | Select-Object Id, ProcessName
```

---

## 🚫 终端命令最佳实践

### 为什么终端命令会卡住？

**常见原因**:
1. **交互式命令**: `npm run dev`, `python`, `uvicorn` 等持续运行的服务
2. **等待输入**: `Read-Host`, `pause`, 交互式安装
3. **超时设置过长**: `WaitMsBeforeAsync` 设置太大

### ✅ 正确做法

#### 1. 长期服务 → 后台运行
```python
# ✅ 正确
run_command(
    "uvicorn app.main:app --reload --port 8000",
    WaitMsBeforeAsync=500,  # 0.5秒后后台运行
    SafeToAutoRun=True
)
# 返回 command_id，不会卡住
```

#### 2. 快速命令 → 短超时
```python
# ✅ 正确
run_command(
    "python -c 'import requests; print(requests.get(\"http://localhost:8000/api/xxx\").status_code)'",
    WaitMsBeforeAsync=3000,  # 3秒完成
    SafeToAutoRun=True
)
```

#### 3. 避免交互 → 使用参数
```python
# ❌ 错误
run_command("npm init")  # 需要回答问题

# ✅ 正确
run_command("npm init -y")  # 自动回答
```

#### 4. 检查状态 → 异步查询
```python
# 启动后台服务
cmd_id = run_command(..., WaitMsBeforeAsync=500)

# 稍后检查状态
command_status(cmd_id, WaitDurationSeconds=2)
```

### 超时时间建议
```yaml
API 测试: 3000ms (3秒)
文件操作: 1000ms (1秒)
长期服务: 500ms (后台运行)
最大超时: 10000ms (10秒)
```

### ❌ 绝对避免
```python
# 永远不要这样做
run_command("npm run dev")  # 卡住！
run_command("python")  # 卡住！
run_command("pause")  # 卡住！
run_command(..., WaitMsBeforeAsync=60000)  # 卡太久！
```

---

**维护者**: AI Engineering Team  
**最后更新**: 2026-02-04
