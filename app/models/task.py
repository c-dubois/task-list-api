from datetime import datetime
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import DateTime, ForeignKey
from ..db import db
from typing import Optional, TYPE_CHECKING
if TYPE_CHECKING:
    from .goal import Goal

class Task(db.Model):
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    title: Mapped[str]
    description: Mapped[str]
    completed_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    goal_id: Mapped[Optional[int]] = mapped_column(ForeignKey("goal.id"), nullable=True)
    goal: Mapped[Optional["Goal"]] = relationship(back_populates="tasks")

    def to_dict(self):
        task_dict = {
            "id": self.id,
            "title": self.title,
            "description": self.description,
            "is_complete": self.completed_at is not None,
        }
        if self.goal:
            task_dict["goal_id"] = self.goal.id

        return task_dict

    
    @classmethod
    def from_dict(cls, task_data):
        goal_id = task_data.get("goal_id")
        task = cls(title=task_data["title"], 
                description=task_data["description"], 
                completed_at=task_data.get("completed_at"),
                goal_id = goal_id)
        return task