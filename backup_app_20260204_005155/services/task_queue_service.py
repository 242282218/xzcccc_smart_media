from sqlalchemy.orm import Session
from app.models.task import Task
from app.schemas.task import TaskCreate
from datetime import datetime
from typing import Optional, List

class TaskService:
    def __init__(self, db: Session):
        self.db = db

    def get_tasks(self, skip: int = 0, limit: int = 20, status: Optional[str] = None):
        query = self.db.query(Task)
        if status:
            query = query.filter(Task.status == status)
        return query.order_by(Task.created_at.desc()).offset(skip).limit(limit).all()

    def get_task(self, task_id: int):
        return self.db.query(Task).filter(Task.id == task_id).first()

    def create_task(self, task_in: TaskCreate) -> Task:
        task = Task(
            task_type=task_in.task_type,
            priority=task_in.priority,
            params=task_in.params,
            status="pending"
        )
        self.db.add(task)
        self.db.commit()
        self.db.refresh(task)
        return task

    def cancel_task(self, task_id: int) -> bool:
        task = self.get_task(task_id)
        if not task:
            return False
        
        # 只有 pending 或 running 的任务可以取消
        if task.status in ['completed', 'failed', 'cancelled']:
            return False
            
        task.status = 'cancelled'
        task.completed_at = datetime.now()
        task.error_message = "Cancelled by user"
        self.db.commit()
        return True

    def delete_task(self, task_id: int) -> bool:
        task = self.get_task(task_id)
        if not task:
            return False
        self.db.delete(task)
        self.db.commit()
        return True
