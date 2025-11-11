from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update

from database import get_async_db
from app.models.task import TaskModel
from app.models.project import ProjectModel
from app.schemas.task import TaskUpdate, TaskSchema


router = APIRouter()

@router.put("/{task_id}", response_model=TaskSchema)
async def update_task(task: TaskUpdate, task_id: int, db: AsyncSession = Depends(get_async_db)):
    db_task = await db.scalar(select(TaskModel).where(TaskModel.id == task_id,
                                                      TaskModel.is_active == True))
    if not db_task:
        raise HTTPException(status_code=404, detail="Task not found")

    db_project = await db.scalar(select(ProjectModel).where(ProjectModel.id == task.project_id,
                                                            ProjectModel.is_active == True))
    if not db_project:
        raise HTTPException(status_code=404, detail="Project not found")

    await db.execute(
        update(TaskModel)
        .where(TaskModel.id == task_id)
        .values(**task.model_dump())

    )
    await db.commit()
    await db.refresh(db_task)

    return db_task