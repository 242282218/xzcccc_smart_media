import asyncio
import re
import os
import aiofiles
from typing import List, Optional, Tuple
from sqlalchemy.orm import Session
from app.core.db import SessionLocal
from app.core.db_utils import batch_get_models_by_ids, AsyncBatchProcessor
from app.models.emby import EmbyLibrary, EmbyMediaItem
from app.services.emby_api_client import EmbyAPIClient
from app.services.notification_service import get_notification_service, NotificationType
from app.core.config_manager import get_config
from app.core.logging import get_logger

logger = get_logger(__name__)

class EmbyService:
    """Emby集成服务"""

    _instance = None

    def __init__(self):
        self.config = get_config()
        self.notification_service = get_notification_service()
        self._sync_lock = asyncio.Lock()

    @property
    def is_enabled(self) -> bool:
        """检查Emby服务是否启用"""
        emby_url = self.config.get("endpoints.0.emby_url", "")
        emby_api_key = self.config.get("endpoints.0.emby_api_key", "")
        return bool(emby_url and emby_api_key)
        
    @classmethod
    def get_instance(cls):
        if not cls._instance:
            cls._instance = EmbyService()
        return cls._instance

    def _get_api_client(self) -> EmbyAPIClient:
        """获取API客户端"""
        base_url = self.config.get("endpoints.0.emby_url", "http://localhost:8096")
        api_key = self.config.get("endpoints.0.emby_api_key", "")
        return EmbyAPIClient(base_url, api_key)

    async def refresh_library(self, library_id: Optional[str] = None) -> bool:
        """
        触发Emby库刷新

        调用Emby API的POST /Library/Refresh接口刷新媒体库。
        如果指定了library_id，则刷新特定库；否则刷新所有库。

        Args:
            library_id: Emby媒体库ID，如果为None则刷新所有库

        Returns:
            bool: 是否成功触发刷新
        """
        if not self.is_enabled:
            logger.warning("Emby service is disabled, skipping library refresh")
            return False

        try:
            client = self._get_api_client()
            async with client:
                if library_id:
                    endpoint = f"/Items/{library_id}/Refresh"
                    logger.info(f"Triggering Emby library refresh for library: {library_id}")
                else:
                    endpoint = "/Library/Refresh"
                    logger.info("Triggering Emby full library refresh")

                await client._request_json("POST", f"{client.base_url}{endpoint}")
                logger.info(f"Emby library refresh triggered successfully: {library_id or 'All'}")

                await self.notification_service.send_notification(
                    type=NotificationType.TASK_COMPLETED,
                    title="Emby库刷新已触发",
                    content=f"库ID: {library_id or '全部'}"
                )
                return True

        except Exception as e:
            logger.error(f"Failed to refresh Emby library: {e}")
            return False

    async def sync_library(self):
        """全量同步媒体库"""
        if self._sync_lock.locked():
            logger.warning("Emby sync already in progress")
            return

        async with self._sync_lock:
            logger.info("Starting Emby library sync...")
            await self.notification_service.send_notification(
                type=NotificationType.TASK_STARTED,
                title="Emby同步开始",
                content="开始同步Emby媒体库信息"
            )

            client = self._get_api_client()
            stats = {"libraries": 0, "items": 0, "new": 0, "updated": 0, "failed": 0}
            
            try:
                async with client:
                    # 1. 获取所有视图（媒体库）
                    views = await client.get_views()
                    stats["libraries"] = len(views)
                    
                    db = SessionLocal()
                    try:
                        for view in views:
                            await self._sync_single_library(client, db, view, stats)
                    finally:
                        db.close()
                
                logger.info(f"Emby sync finished: {stats}")
                await self.notification_service.send_notification(
                    type=NotificationType.SYNC_FINISHED,
                    title="Emby同步完成",
                    content=f"处理库: {stats['libraries']}\n项目: {stats['items']}\n新增: {stats['new']}\n更新: {stats['updated']}\n失败: {stats['failed']}"
                )
                
            except Exception as e:
                logger.error(f"Emby sync failed: {e}")
                await self.notification_service.notify_sync_error("Emby Sync", str(e))

    async def _sync_single_library(self, client: EmbyAPIClient, db: Session, view: dict, stats: dict):
        """同步单个媒体库"""
        library_id_emby = view['Id']
        library_name = view['Name']
        
        # 1. 更新或创建库记录
        lib_record = db.query(EmbyLibrary).filter(EmbyLibrary.emby_id == library_id_emby).first()
        if not lib_record:
            lib_record = EmbyLibrary(
                emby_id=library_id_emby, 
                name=library_name, 
                path=view.get('Path')
            )
            db.add(lib_record)
            db.commit()
            db.refresh(lib_record)
        
        # 2. 获取库中所有项目
        items = await client.get_items_by_query(
            parent_id=library_id_emby,
            recursive=True,
            include_item_types="Movie,Episode",
            fields="Path,MediaSources"
        )
        
        # 3. 批量处理项目以优化性能
        batch_processor = AsyncBatchProcessor(batch_size=100, delay=0.05)
        
        async def process_item_batch(item_batch):
            """处理项目批次"""
            batch_stats = {"items": 0, "new": 0, "updated": 0, "failed": 0}
            
            # 批量获取已存在的项目（避免N+1查询）
            emby_ids = [item['Id'] for item in item_batch]
            existing_items_dict = batch_get_models_by_ids(db, EmbyMediaItem, emby_ids)
            
            for item in item_batch:
                batch_stats["items"] += 1
                try:
                    is_new = await self._process_item_optimized(
                        db, lib_record.id, item, existing_items_dict.get(item['Id'])
                    )
                    if is_new:
                        batch_stats["new"] += 1
                    else:
                        batch_stats["updated"] += 1
                except Exception as e:
                    logger.error(f"Failed to process item {item.get('Name')}: {e}")
                    batch_stats["failed"] += 1
            
            return batch_stats
        
        # 分批处理所有项目
        batch_results = await batch_processor.process_items_batched(items, process_item_batch)
        
        # 汇总统计信息
        for batch_stat in batch_results:
            stats["items"] += batch_stat["items"]
            stats["new"] += batch_stat["new"]
            stats["updated"] += batch_stat["updated"]
            stats["failed"] += batch_stat["failed"]

    async def _process_item_optimized(self, db: Session, library_id_db: int, item: dict, existing_item = None) -> bool:
        """优化的项目处理方法，支持批量操作"""
        emby_id = item['Id']
        name = item.get('Name')
        path = item.get('Path', '')
        media_type = item.get('Type')
        
        # 提取Pickcode
        pickcode = await self._extract_pickcode(item)
        
        # 使用传入的已存在项目，避免重复查询
        item_record = existing_item
        is_new = False
        
        if not item_record:
            is_new = True
            item_record = EmbyMediaItem(
                emby_id=emby_id,
                library_id=library_id_db,
                name=name,
                type=media_type,
                path=path,
                pickcode=pickcode,
                is_strm=path.lower().endswith('.strm')
            )
            db.add(item_record)
        else:
            # 更新字段
            item_record.name = name
            item_record.path = path
            item_record.pickcode = pickcode
            # 注意：需要导入func或使用datetime.now()
            from datetime import datetime
            item_record.updated_at = datetime.now()
        
        return is_new
    
    async def _process_item(self, db: Session, library_id_db: int, item: dict) -> bool:
        """处理单个项目，返回是否新增（保持向后兼容）"""
        emby_id = item['Id']
        name = item.get('Name')
        path = item.get('Path', '')
        media_type = item.get('Type')
        
        # 提取Pickcode
        pickcode = await self._extract_pickcode(item)
        
        item_record = db.query(EmbyMediaItem).filter(EmbyMediaItem.emby_id == emby_id).first()
        is_new = False
        
        if not item_record:
            is_new = True
            item_record = EmbyMediaItem(
                emby_id=emby_id,
                library_id=library_id_db,
                name=name,
                type=media_type,
                path=path,
                pickcode=pickcode,
                is_strm=path.lower().endswith('.strm')
            )
            db.add(item_record)
        else:
            # 更新字段
            item_record.name = name
            item_record.path = path
            item_record.pickcode = pickcode
            from datetime import datetime
            item_record.updated_at = datetime.now()
        
        db.commit()
        return is_new

    async def _extract_pickcode(self, item: dict) -> Optional[str]:
        """提取Pickcode"""
        media_sources = item.get('MediaSources', [])
        path = item.get('Path', '')
        
        # 1. 尝试从Path解析 (如果是 strm 且包含 proxy url)
        # 例如: http://localhost:8000/api/proxy/video/{file_id}
        # file_id 通常就是 pickcode (对于v2 api)
        match_proxy = re.search(r'/api/proxy/(?:video|stream)/([a-zA-Z0-9]+)', path)
        if match_proxy:
            return match_proxy.group(1)
            
        # 2. 如果是本地STRM文件，读取内容
        if path.lower().endswith('.strm') and os.path.exists(path):
            try:
                async with aiofiles.open(path, 'r', encoding='utf-8') as f:
                    content = await f.read()
                    # 再次尝试匹配URL中的pickcode
                    match_url = re.search(r'/api/proxy/(?:video|stream)/([a-zA-Z0-9]+)', content)
                    if match_url:
                        return match_url.group(1)
            except Exception as e:
                pass
                
        # 3. 尝试从 MediaSources 路径解析
        for source in media_sources:
            s_path = source.get('Path', '')
            if '#pickcode=' in s_path:
                return s_path.split('#pickcode=')[-1].split('&')[0]
                
        return None

    async def link_media_to_sync_file(self, item: dict):
        """WebHook: 关联新媒体"""
        # 这是一个简化版，完整的需建立DB连接
        # 通常Webhook只给基本Item信息，我们可能需要重新查询完整信息
        client = self._get_api_client()
        async with client:
            full_item = await client.get_items(item['Id'])
            
            db = SessionLocal()
            try:
                # 需要找到对应的 Library ID，这里简化处理，如果没有就创建一个临时或默认的
                # 但最好是先执行一次全量同步
                # 如果找不到，我们尝试根据 item.ParentId 去找 Library? 比较复杂
                # 暂时只记录 EmbyMediaItem，如果 Library 未知则留空或设为 0 (需修改Model允许为空)
                
                # 实际上 Webhook 最重要的是触发 Pickcode 提取并保存，供 ProxyService 使用
                await self._process_item(db, 0, full_item) # 0 as placeholder or unknown
            except Exception as e:
                logger.error(f"Link media failed: {e}")
            finally:
                db.close()
    
    async def handle_library_new(self, item: dict):
        """处理新增事件"""
        await self.notification_service.notify_media_added(
            item.get('Name', 'Unknown'), 
            item.get('Type', 'Unknown')
        )
        await self.link_media_to_sync_file(item)
        
    async def handle_library_deleted(self, item: dict):
        """处理删除事件"""
        await self.notification_service.notify_media_removed(
            item.get('Name', 'Unknown')
        )
        # 删除DB记录
        db = SessionLocal()
        try:
            db.query(EmbyMediaItem).filter(EmbyMediaItem.emby_id == item['Id']).delete()
            db.commit()
        finally:
            db.close()

def get_emby_service():
    return EmbyService.get_instance()
