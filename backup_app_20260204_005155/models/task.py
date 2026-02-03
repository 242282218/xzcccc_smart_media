from sqlalchemy import Column, Integer, String, DateTime, Text, JSON
from sqlalchemy.sql import func
from app.core.db import Base

class Task(Base):
    """异步任务模型"""
    __tablename__ = "tasks"
    
    id = Column(Integer, primary_key=True, index=True)
    task_type = Column(String, nullable=False, comment="任务类型")
    status = Column(String, default='pending', index=True, comment="状态: pending, running, completed, failed, cancelled")
    priority = Column(String, default='normal', comment="优先级: low, normal, high")
    
    progress = Column(Integer, default=0, comment="进度百分比 0-100")
    total_items = Column(Integer, default=0, comment="总项目数")
    processed_items = Column(Integer, default=0, comment="已处理项目数")
    
    error_message = Column(Text, nullable=True, comment="错误信息")
    logs = Column(JSON, default=list, comment="执行日志")
    params = Column(JSON, default=dict, comment="任务参数")
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    started_at = Column(DateTime(timezone=True), nullable=True)
    completed_at = Column(DateTime(timezone=True), nullable=True)
