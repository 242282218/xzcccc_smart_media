# 文件管理模块架构设计

## 📋 文档信息
- **版本**: v1.0
- **创建时间**: 2026-02-04
- **状态**: 待审核
- **模块名称**: File Manager

---

## 🎯 设计目标

### 核心目标
1. **统一管理**: 支持多种存储终端（本地、夸克、AList、WebDAV）
2. **可扩展性**: 插件式架构，新增存储类型零侵入
3. **高性能**: 支持缓存、分页、懒加载
4. **易维护**: 清晰的分层架构和职责划分

### 功能需求
- ✅ 文件/文件夹浏览
- ✅ 文件信息查看
- ✅ 重命名/移动/删除/创建文件夹
- ✅ 文件搜索（支持模糊匹配）
- ✅ 多选批量操作
- ✅ 路径导航（面包屑）
- ✅ 视图切换（列表/网格）

---

## 🏗️ 系统架构

### 分层架构图

```
┌─────────────────────────────────────────────────────────────┐
│                      Frontend (Vue 3)                        │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────────────┐  │
│  │FileManager  │  │ FileGrid/   │  │  FileOperationBar   │  │
│  │   View      │  │ FileList    │  │                     │  │
│  └─────────────┘  └─────────────┘  └─────────────────────┘  │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼ HTTP/REST
┌─────────────────────────────────────────────────────────────┐
│                      API Layer (FastAPI)                     │
│  ┌─────────────────────────────────────────────────────┐    │
│  │              /api/files/*                            │    │
│  │  browse | info | rename | move | delete | mkdir     │    │
│  └─────────────────────────────────────────────────────┘    │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│                   Service Layer (门面模式)                   │
│  ┌─────────────────────────────────────────────────────┐    │
│  │              FileManagerService                      │    │
│  │  - 路由分发 (根据路径前缀判断存储类型)                 │    │
│  │  - 权限校验                                          │    │
│  │  - 操作日志                                          │    │
│  └─────────────────────────────────────────────────────┘    │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│               Storage Provider Layer (抽象层)                │
│  ┌────────────────────────────────────────────────────┐     │
│  │           StorageProvider (ABC)                     │     │
│  │  list() | info() | rename() | move() | delete()    │     │
│  │  mkdir() | search() | exists() | get_quota()       │     │
│  └────────────────────────────────────────────────────┘     │
│           ▲              ▲              ▲                    │
│           │              │              │                    │
│  ┌────────┴───┐  ┌───────┴────┐  ┌─────┴──────┐             │
│  │   Local    │  │   Quark    │  │   AList    │             │
│  │  Provider  │  │  Provider  │  │  Provider  │             │
│  └────────────┘  └────────────┘  └────────────┘             │
└─────────────────────────────────────────────────────────────┘
```

---

## 📁 目录结构

```
quark_strm/
├── app/
│   ├── api/
│   │   └── file_manager.py          # API 路由
│   │
│   ├── schemas/
│   │   └── file_manager.py          # Pydantic 模型
│   │
│   ├── services/
│   │   ├── file_manager_service.py  # 统一管理服务
│   │   └── storage/                 # 存储提供者
│   │       ├── __init__.py
│   │       ├── base.py              # 抽象基类
│   │       ├── local.py             # 本地文件系统
│   │       ├── quark.py             # 夸克云盘
│   │       └── alist.py             # AList (未来扩展)
│   │
│   └── models/
│       └── file_item.py             # 文件数据模型
│
└── web/src/
    ├── views/
    │   └── FileManagerView.vue      # 主视图
    │
    ├── components/
    │   └── file-manager/
    │       ├── FileGrid.vue         # 网格视图
    │       ├── FileList.vue         # 列表视图
    │       ├── FileBreadcrumb.vue   # 面包屑导航
    │       ├── FileToolbar.vue      # 工具栏
    │       └── FileContextMenu.vue  # 右键菜单
    │
    └── api/
        └── file-manager.ts          # API 客户端
```

---

## 📐 数据模型

### 1. FileItem (核心模型)

```python
from enum import Enum
from typing import Optional, List
from datetime import datetime
from pydantic import BaseModel, Field

class FileType(str, Enum):
    """文件类型枚举"""
    FILE = "file"
    FOLDER = "folder"
    LINK = "link"

class StorageType(str, Enum):
    """存储类型枚举"""
    LOCAL = "local"
    QUARK = "quark"
    ALIST = "alist"
    WEBDAV = "webdav"

class FileItem(BaseModel):
    """统一的文件/文件夹模型"""
    
    # 基础属性
    id: str = Field(..., description="唯一标识（云盘用fid，本地用路径hash）")
    name: str = Field(..., description="文件名")
    path: str = Field(..., description="完整路径")
    parent_path: str = Field(..., description="父目录路径")
    
    # 类型属性
    file_type: FileType = Field(..., description="文件/文件夹")
    storage_type: StorageType = Field(..., description="存储类型")
    mime_type: Optional[str] = Field(None, description="MIME类型")
    extension: Optional[str] = Field(None, description="扩展名")
    
    # 大小与时间
    size: int = Field(0, description="文件大小(字节)")
    created_at: Optional[datetime] = Field(None, description="创建时间")
    updated_at: Optional[datetime] = Field(None, description="修改时间")
    
    # 权限与状态
    is_readable: bool = Field(True, description="是否可读")
    is_writable: bool = Field(True, description="是否可写")
    is_hidden: bool = Field(False, description="是否隐藏")
    
    # 扩展属性 (用于特定存储类型)
    extra: dict = Field(default_factory=dict, description="扩展属性")
```

### 2. 请求/响应模型

```python
class BrowseRequest(BaseModel):
    """浏览目录请求"""
    path: str = Field(default="/", description="目录路径")
    storage: StorageType = Field(default=StorageType.LOCAL)
    page: int = Field(default=1, ge=1)
    size: int = Field(default=50, ge=1, le=200)
    sort_by: str = Field(default="name")  # name, size, updated_at
    sort_order: str = Field(default="asc")  # asc, desc
    show_hidden: bool = Field(default=False)

class BrowseResponse(BaseModel):
    """浏览目录响应"""
    items: List[FileItem]
    total: int
    path: str
    parent_path: Optional[str]
    breadcrumb: List[dict]  # [{name, path}, ...]

class FileOperationRequest(BaseModel):
    """文件操作请求"""
    action: str  # rename, move, delete, mkdir
    paths: List[str]  # 操作的文件路径列表
    storage: StorageType
    target: Optional[str] = None  # 目标路径(移动/重命名用)
    new_name: Optional[str] = None  # 新名称(重命名用)

class FileOperationResponse(BaseModel):
    """文件操作响应"""
    success: bool
    affected_count: int
    errors: List[dict] = []  # [{path, error}, ...]
```

---

## 🔌 存储提供者接口

### 抽象基类

```python
from abc import ABC, abstractmethod
from typing import List, Optional, AsyncGenerator

class StorageProvider(ABC):
    """
    存储提供者抽象基类
    
    所有存储实现必须继承此类并实现所有抽象方法。
    设计原则：
    1. 所有方法异步化
    2. 统一返回 FileItem 模型
    3. 错误通过异常抛出
    """
    
    @property
    @abstractmethod
    def storage_type(self) -> StorageType:
        """返回存储类型标识"""
        pass
    
    @abstractmethod
    async def list(
        self, 
        path: str, 
        page: int = 1, 
        size: int = 50,
        sort_by: str = "name",
        sort_order: str = "asc"
    ) -> tuple[List[FileItem], int]:
        """
        列出目录内容
        
        Args:
            path: 目录路径
            page: 页码
            size: 每页大小
            sort_by: 排序字段
            sort_order: 排序方向
            
        Returns:
            (文件列表, 总数)
        """
        pass
    
    @abstractmethod
    async def info(self, path: str) -> Optional[FileItem]:
        """获取文件/文件夹详情"""
        pass
    
    @abstractmethod
    async def exists(self, path: str) -> bool:
        """检查路径是否存在"""
        pass
    
    @abstractmethod
    async def rename(self, path: str, new_name: str) -> FileItem:
        """重命名文件/文件夹"""
        pass
    
    @abstractmethod
    async def move(self, source: str, target: str) -> FileItem:
        """移动文件/文件夹"""
        pass
    
    @abstractmethod
    async def delete(self, path: str) -> bool:
        """删除文件/文件夹"""
        pass
    
    @abstractmethod
    async def mkdir(self, path: str) -> FileItem:
        """创建文件夹"""
        pass
    
    @abstractmethod
    async def search(
        self, 
        keyword: str, 
        path: str = "/",
        recursive: bool = True
    ) -> List[FileItem]:
        """搜索文件"""
        pass
    
    # 可选方法 (有默认实现)
    async def get_quota(self) -> dict:
        """获取存储配额信息"""
        return {"total": -1, "used": -1, "available": -1}
    
    async def batch_delete(self, paths: List[str]) -> dict:
        """批量删除"""
        success = 0
        errors = []
        for path in paths:
            try:
                await self.delete(path)
                success += 1
            except Exception as e:
                errors.append({"path": path, "error": str(e)})
        return {"success": success, "errors": errors}
```

---

## 🛣️ API 路由设计

### 路由表

| 方法 | 路径 | 描述 |
|------|------|------|
| GET | `/api/files/browse` | 浏览目录 |
| GET | `/api/files/info` | 获取文件信息 |
| POST | `/api/files/operation` | 执行文件操作 |
| GET | `/api/files/search` | 搜索文件 |
| GET | `/api/files/quota` | 获取存储配额 |

### 示例请求

```http
# 浏览目录
GET /api/files/browse?storage=local&path=/media&page=1&size=50

# 获取文件信息
GET /api/files/info?storage=quark&path=/我的资源/电影

# 重命名文件
POST /api/files/operation
{
    "action": "rename",
    "storage": "local",
    "paths": ["/media/movie.mp4"],
    "new_name": "电影.mp4"
}

# 批量删除
POST /api/files/operation
{
    "action": "delete",
    "storage": "quark",
    "paths": ["/回收站/file1.mp4", "/回收站/file2.mp4"]
}

# 搜索
GET /api/files/search?storage=local&keyword=三体&path=/media
```

---

## 🎨 前端组件设计

### 组件层次

```
FileManagerView.vue (主视图)
├── FileToolbar.vue (工具栏: 视图切换、排序、搜索)
├── FileBreadcrumb.vue (面包屑导航)
├── FileGrid.vue / FileList.vue (文件展示)
│   └── FileItem.vue (单个文件项)
├── FileContextMenu.vue (右键菜单)
├── FileOperationDialog.vue (操作对话框: 重命名、移动)
└── FileUploadArea.vue (上传区域, 未来扩展)
```

### 状态管理 (Pinia)

```typescript
// stores/fileManager.ts
interface FileManagerState {
    // 当前状态
    currentPath: string;
    currentStorage: StorageType;
    items: FileItem[];
    selectedItems: Set<string>;
    
    // 视图设置
    viewMode: 'grid' | 'list';
    sortBy: string;
    sortOrder: 'asc' | 'desc';
    showHidden: boolean;
    
    // 加载状态
    loading: boolean;
    error: string | null;
    
    // 分页
    page: number;
    total: int;
    pageSize: number;
}

interface FileManagerActions {
    browse(path: string): Promise<void>;
    refresh(): Promise<void>;
    rename(path: string, newName: string): Promise<void>;
    move(paths: string[], target: string): Promise<void>;
    delete(paths: string[]): Promise<void>;
    mkdir(name: string): Promise<void>;
    search(keyword: string): Promise<void>;
    toggleSelect(id: string): void;
    selectAll(): void;
    clearSelection(): void;
}
```

---

## ⚡ 性能优化策略

### 1. 缓存策略

```python
# 目录缓存 (TTL: 30秒)
cache_key = f"file_list:{storage}:{path}:{page}:{size}"

# 文件信息缓存 (TTL: 60秒)
cache_key = f"file_info:{storage}:{path}"
```

### 2. 分页加载
- 默认每页 50 项
- 支持懒加载 (滚动加载更多)

### 3. 前端优化
- 虚拟滚动 (大量文件时)
- 图片懒加载
- 防抖搜索 (300ms)

---

## 🔒 安全考虑

### 路径校验
```python
def validate_path(path: str) -> bool:
    """防止路径遍历攻击"""
    if ".." in path:
        raise ValueError("Invalid path: contains ..")
    if not path.startswith("/"):
        raise ValueError("Path must be absolute")
    return True
```

### 权限控制
- 本地文件: 检查 `os.access()` 权限
- 云盘: 依赖云盘 API 权限

---

## 📅 实施计划

### Phase 1: 后端基础 (Day 1)
- [ ] 创建 `schemas/file_manager.py` (数据模型)
- [ ] 创建 `services/storage/base.py` (抽象接口)
- [ ] 实现 `services/storage/local.py` (本地存储)
- [ ] 创建 `services/file_manager_service.py` (统一服务)
- [ ] 创建 `api/file_manager.py` (路由)

### Phase 2: 云盘集成 (Day 2)
- [ ] 实现 `services/storage/quark.py` (夸克存储)
- [ ] 适配现有 `quark_service.py`
- [ ] 测试云盘操作

### Phase 3: 前端开发 (Day 3-4)
- [ ] 创建 `FileManagerView.vue`
- [ ] 创建子组件 (Grid, List, Toolbar)
- [ ] 实现状态管理
- [ ] 实现文件操作

### Phase 4: 测试与优化 (Day 5)
- [ ] 编写单元测试
- [ ] 性能测试
- [ ] 错误处理完善

---

## 🎯 验收标准

### 功能验收
- [ ] 可浏览本地文件系统
- [ ] 可浏览夸克云盘
- [ ] 支持重命名、移动、删除、创建文件夹
- [ ] 支持多选批量操作
- [ ] 支持文件搜索

### 性能验收
- [ ] 目录浏览响应时间 < 500ms
- [ ] 支持显示 1000+ 文件
- [ ] 操作反馈延迟 < 200ms

### 质量验收
- [ ] 代码有完整注释
- [ ] 测试覆盖率 > 80%
- [ ] 无严重错误

---

## 📝 待确认事项

1. **存储优先级**: 默认显示哪个存储？本地还是夸克？
2. **权限需求**: 是否需要密码保护文件操作？
3. **上传功能**: 是否在本期实现文件上传？
4. **预览功能**: 是否需要文件预览（图片、视频、文本）？
5. **回收站**: 删除是否需要回收站机制？

---

**请审阅后确认，我将开始实施。**
