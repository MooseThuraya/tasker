from app import db
from datetime import datetime, date
from typing import Optional, List
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import String, Text, Boolean, Date, ForeignKey, Enum
import enum

class Priority(enum.Enum):
    HIGH = 'high'
    MEDIUM = 'medium'
    LOW = 'low'
    NONE = 'none'

class User(db.Model):
    __tablename__ = 'users'
    
    id: Mapped[int] = mapped_column(primary_key=True)
    username: Mapped[str] = mapped_column(String(100), unique=True, nullable=False)
    tasks: Mapped[List['Task']] = relationship('Task', back_populates='user', cascade='all, delete-orphan')
    
    def __repr__(self) -> str:
        return f'<User {self.username}>'

class Task(db.Model):
    __tablename__ = 'tasks'
    
    id: Mapped[int] = mapped_column(primary_key=True)
    title: Mapped[str] = mapped_column(String(100), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    completed: Mapped[bool] = mapped_column(Boolean, default=False)
    created_at: Mapped[datetime] = mapped_column(default=datetime.utcnow)
    due_date: Mapped[Optional[date]] = mapped_column(Date, nullable=True)
    user_id: Mapped[int] = mapped_column(ForeignKey('users.id'), nullable=False)
    user: Mapped['User'] = relationship('User', back_populates='tasks')
    priority: Mapped[Optional[str]] = mapped_column(String(10), nullable=True)
    tags: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    archived: Mapped[bool] = mapped_column(Boolean, default=False)
    archived_at: Mapped[Optional[datetime]] = mapped_column(nullable=True)
    
    def __repr__(self) -> str:
        return f'<Task {self.title}'
    
    @property
    def is_overdue(self) -> bool:
        if self.due_date and not self.completed:
            return self.due_date < date.today()
        return False
    
    def get_priority_label(self) -> str:
        """Get the display label for priority"""
        if not self.priority or self.priority == 'none':
            return 'None'
        return self.priority.capitalize()
    
    def get_tags_list(self) -> List[str]:
        """Get the tags as a list"""
        if not self.tags:
            return []
        return [tag.strip() for tag in self.tags.split(',')]
    
    def add_tag(self, tag: str) -> None:
        """Add a new tag to the task"""
        tags_list = self.get_tags_list()
        if tag.strip() not in tags_list:
            tags_list.append(tag.strip())
            self.tags = ', '.join(tags_list)
    
    def remove_tag(self, tag: str) -> None:
        """Remove a tag from the task"""
        tags_list = self.get_tags_list()
        if tag.strip() in tags_list:
            tags_list.remove(tag.strip())
            self.tags = ', '.join(tags_list) if tags_list else None
    
    def archive(self) -> None:
        """Archive this task"""
        self.archived = True
        self.archived_at = datetime.utcnow()
    
    def unarchive(self) -> None:
        """Unarchive this task"""
        self.archived = False
        self.archived_at = None
