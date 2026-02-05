## 修复代码Bug计划

### 本轮目标
修复代码审查中发现的8个关键bug

### 前置锚点
- 当前Git状态: 需要确认
- 缺失: 需要创建Git提交作为回滚点

### 执行步骤

#### 阶段1: 高优先级Bug修复
1. **修复 config_manager.py 线程安全问题**
   - 添加线程锁保护单例模式
   - 文件: quark_strm/app/core/config_manager.py

2. **修复 quark_size_fetcher.py 递归深度风险**
   - 将递归改为迭代实现
   - 添加最大深度限制
   - 文件: quark_strm/app/services/quark_size_fetcher.py

#### 阶段2: 中优先级Bug修复
3. **修复 quark.py 异常处理问题**
   - 统一异常处理为 HTTPException
   - 文件: quark_strm/app/api/quark.py

4. **修复 strm.py 硬编码空Cookie问题**
   - 从配置读取cookie
   - 文件: quark_strm/app/api/strm.py

5. **修复 strm_service.py 资源泄漏问题**
   - 确保 database 被正确关闭
   - 文件: quark_strm/app/services/strm_service.py

#### 阶段3: 低优先级Bug修复
6. **修复 search_service.py 拼写错误**
   - "夷克" -> "夸克"
   - 文件: quark_strm/app/services/search_service.py

7. **修复 search_service.py 标识符问题**
   - 使用 uuid 替代 id()
   - 文件: quark_strm/app/services/search_service.py

8. **修复 search_service.py 分页逻辑问题**
   - 调整分页和过滤顺序
   - 文件: quark_strm/app/services/search_service.py

### 风险提示
- 修改核心服务文件可能影响现有功能
- 建议先运行现有测试验证

### 回滚方案
- 使用 git reset --hard <锚点> 回滚

请确认是否开始执行修复？