import asyncio
import json
from datetime import datetime
from sqlalchemy.orm import Session
from app.models.task import Task
from app.core.websocket_manager import ws_manager
from app.core.db import SessionLocal
from app.core.logging import get_logger

logger = get_logger(__name__)

class TaskRunner:
    """任务执行器"""
    
    @staticmethod
    async def run_task(task_id: int):
        """后台运行任务（示例实现：模拟10秒处理过程）"""
        logger.info(f"Starting task {task_id}")
        
        # 获取独立的 DB Session
        db: Session = SessionLocal()
        
        try:
            task = db.query(Task).filter(Task.id == task_id).first()
            if not task:
                logger.error(f"Task {task_id} not found")
                return

            # 更新状态为运行中
            task.status = 'running'
            task.started_at = datetime.now()
            task.progress = 0
            task.total_items = 100 # Mock total
            
            # 确保 logs 初始化
            if task.logs is None:
                task.logs = []
                
            db.commit()

            # 广播开始
            await ws_manager.broadcast({
                "type": "task_update",
                "task_id": task_id,
                "status": "running",
                "progress": 0
            })

            # 根据任务类型分发
            if task.task_type == 'strm_generation':
                from app.services.media_organize_service import MediaOrganizeService
                service = MediaOrganizeService(db)
                
                async def update_progress(progress, message, new_logs_data):
                    # 检查取消
                    db.expire(task)
                    db.refresh(task)
                    if task.status == 'cancelled':
                         raise asyncio.CancelledError("Task cancelled")
                         
                    task.progress = progress
                    
                    logs_to_push = []
                    if message:
                        log_entry = {
                            "ts": datetime.now().timestamp(), 
                            "level": "INFO", 
                            "message": message
                        }
                        # JSON 类型字段需重新赋值
                        current_logs = list(task.logs or [])
                        current_logs.append(log_entry)
                        task.logs = current_logs
                        logs_to_push.append(log_entry)
                    
                    db.commit()
                    
                    payload = {
                        "type": "task_update",
                        "task_id": task_id,
                        "status": "running",
                        "progress": progress,
                    }
                    if logs_to_push:
                        payload["logs"] = logs_to_push
                        
                    await ws_manager.broadcast(payload)

                await service.process_strm_generation(task, update_progress)
                
            else:
                # 默认模拟逻辑 (用于测试其他类型)
                total = 100
                for i in range(1, total + 1):
                    # 检查取消
                    db.expire(task)
                    db.refresh(task)
                    if task.status == 'cancelled':
                        logger.info(f"Task {task_id} cancelled")
                        await ws_manager.broadcast({
                            "type": "task_update",
                            "task_id": task_id,
                            "status": "cancelled"
                        })
                        return # 直接返回

                    await asyncio.sleep(0.1) 
                    task.progress = int((i / total) * 100)
                    if i % 10 == 0:
                        db.commit()
                        await ws_manager.broadcast({
                            "type": "task_update",
                            "task_id": task_id,
                            "status": "running",
                            "progress": task.progress
                        })
            
            # 完成 (如果没有被 Exception 中断)
            task.status = 'completed'
            task.completed_at = datetime.now()
            task.progress = 100
            db.commit()
            
            await ws_manager.broadcast({
                "type": "task_update",
                "task_id": task_id,
                "status": "completed",
                "progress": 100
            })
            logger.info(f"Task {task_id} completed")

        except Exception as e:
            logger.error(f"Task {task_id} failed: {e}")
            import traceback
            logger.error(traceback.format_exc())
            
            task.status = 'failed'
            task.error_message = str(e)
            task.completed_at = datetime.now()
            db.commit()
            
            await ws_manager.broadcast({
                "type": "task_update",
                "task_id": task_id,
                "status": "failed",
                "error": str(e)
            })
        finally:
            db.close()
