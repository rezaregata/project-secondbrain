from datetime import datetime, time

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.database.models import Task


class TaskService:
    def __init__(self, session: Session):
        self.session = session

    def add_task(self, task_text: str) -> Task:
        task = Task(task=task_text, status="OPEN")
        self.session.add(task)
        self.session.commit()
        self.session.refresh(task)
        return task

    def get_today_tasks(self) -> list[Task]:
        today_start = datetime.combine(datetime.utcnow().date(), time.min)
        stmt = (
            select(Task)
            .where(Task.created_at >= today_start)
            .order_by(Task.created_at.desc())
        )
        return list(self.session.scalars(stmt).all())

    def get_tasks_since(self, since: datetime) -> list[Task]:
        stmt = (
            select(Task)
            .where(Task.created_at >= since)
            .order_by(Task.created_at.desc())
        )
        return list(self.session.scalars(stmt).all())

    def get_completed_since(self, since: datetime) -> list[Task]:
        stmt = (
            select(Task)
            .where(Task.created_at >= since, Task.status == "DONE")
            .order_by(Task.created_at.desc())
        )
        return list(self.session.scalars(stmt).all())

    def mark_done(self, task_id: int) -> Task | None:
        task = self.session.get(Task, task_id)
        if not task:
            return None
        task.status = "DONE"
        self.session.commit()
        self.session.refresh(task)
        return task

    def format_task_list(self, tasks: list[Task]) -> str:
        if not tasks:
            return "Tidak ada task."
        lines = []
        for task in tasks:
            status_icon = "✅" if task.status == "DONE" else "⬜"
            lines.append(f"{status_icon} #{task.id} {task.task} [{task.status}]")
        return "\n".join(lines)
