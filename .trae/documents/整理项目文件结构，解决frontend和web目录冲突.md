## 问题分析
项目存在两个前端目录造成混乱：
1. `quark_strm/frontend/` - 文档中说明的目录，包含我错误修改的Settings配置页面
2. `quark_strm/web/` - 实际运行的前端目录，启动脚本使用的目录

## 目标
统一前端目录结构，保留实际使用的`web`目录，清理或归档`frontend`目录

## 涉及文件/目录
1. `quark_strm/frontend/` - 需要清理的目录
2. `quark_strm/web/` - 保留的实际使用目录
3. `quark_strm/docs/PROJECT_STRUCTURE.md` - 需要更新的文档
4. `quark_strm/scripts/start-all.bat` - 确认脚本指向正确

## 修改步骤

### 步骤1: 备份frontend目录内容
将frontend目录重命名为frontend_backup或删除（确认无重要内容后）

### 步骤2: 更新项目文档
修改PROJECT_STRUCTURE.md，将frontend改为web，与实际目录结构保持一致

### 步骤3: 验证启动脚本
确认start-all.bat指向正确的web目录

### 步骤4: 清理无用文件
删除frontend目录（如果确认web目录已包含所有必要功能）

## 风险点
- 需要确认frontend目录中没有web目录缺少的重要文件
- 需要确保Settings配置功能在web目录中已正确实现
- 修改文档后需要与实际结构保持一致