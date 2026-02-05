## 本轮 | 智能体: Dev Agent | 目标: 修复Test_Report中的P1/P2级别Bug

### 前置 | 已阅读文件
- ✅ C:\Users\24228\Desktop\smart_media\ai\rules\agent.md
- ✅ C:\Users\24228\Desktop\smart_media\ai\runner.md
- ✅ C:\Users\24228\Desktop\smart_media\ai\state\plan.md
- ✅ C:\Users\24228\Desktop\smart_media\quark_strm\Test_Report_2026-02-02.md

### 问题分析
根据测试报告，存在以下P1/P2级Bug需要修复：

| ID | 问题 | 严重程度 | 文件位置 |
|----|------|---------|---------|
| BUG-001 | Rename status响应缺少`rename_service`字段 | P2 | app/api/rename.py |
| BUG-002 | `/api/rename/preview`请求体不兼容(返回422) | P1 | app/api/rename.py |
| BUG-003 | `/api/rename/info`端点缺失(404) | P1 | app/api/rename.py |
| BUG-004 | CronService不支持6字段Cron表达式 | P2 | app/services/cron_service.py |
| BUG-005 | CronService interval job传递None给IntervalTrigger | P2 | app/services/cron_service.py |
| BUG-006 | CronService任务去重不生效 | P2 | app/services/cron_service.py |
| BUG-007 | Quark SDK导入失败 | P2 | app/api/quark_sdk.py |
| BUG-008 | RenameService缺少`_calculate_confidence/_generate_new_name/_match_media`方法 | P1 | app/services/rename_service.py |
| BUG-009 | RenameService缺少`asyncio`导入 | P1 | app/services/rename_service.py |

### 约束范围
- **仅修改**：
  - `app/services/rename_service.py`
  - `app/services/cron_service.py`
  - `app/api/rename.py`
  - `app/api/quark_sdk.py`
- **禁止修改**：测试文件、配置文件、其他未列出的文件

### 执行计划

#### 阶段1: 修复RenameService核心方法 (P1)
1. 添加缺失的`import asyncio`
2. 实现`_match_media()`方法 - TMDB媒体匹配
3. 实现`_generate_new_name()`方法 - 生成新文件名
4. 实现`_calculate_confidence()`方法 - 计算匹配置信度
5. 实现`_find_related_files()`方法 - 查找关联文件

#### 阶段2: 修复API端点 (P1)
1. 修改`/api/rename/preview`请求体字段从`path`改为`target_path`
2. 添加缺失的`/api/rename/info`端点
3. 更新`/api/rename/status`响应，添加`rename_service`字段

#### 阶段3: 修复CronService (P2)
1. 支持6字段Cron表达式(带秒)
2. 修复IntervalTrigger传递None的问题
3. 修复任务去重逻辑

#### 阶段4: 修复SDK导入 (P2)
1. 修复`SearchService`导入路径

### 风险点
- 修改API请求体可能影响前端调用，需要保持兼容性
- Cron表达式修改可能影响现有定时任务

### 回滚方案
```bash
git reset --hard <当前commit hash>
```

### 验证计划
1. 运行`python -m pytest tests/test_rename_service.py -v`验证RenameService
2. 运行`python -m pytest tests/test_api_routes.py -v`验证API路由
3. 检查编码是否为UTF-8

---

**请确认以上计划后，我将开始执行优化。** (Y/N)