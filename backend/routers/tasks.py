from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
import models, schemas
from deps import get_db, get_current_user_dep

router = APIRouter(prefix="/tasks", tags=["Tasks"])


# ➕ Create Task
@router.post("/client/{client_id}")
def create_task(
    client_id: int,
    task: schemas.TaskCreate,
    db: Session = Depends(get_db),
    user = Depends(get_current_user_dep)
):
    # Check client ownership
    client = db.query(models.Client).filter(models.Client.id == client_id).first()

    if not client or client.user_id != user.id:
        raise HTTPException(403, "Not allowed")

    # Limit: max 15 tasks in pending
    count = db.query(models.Task).filter(
        models.Task.client_id == client_id,
        models.Task.status == "pending"
    ).count()

    if count >= 15:
        raise HTTPException(400, "Max 15 tasks allowed in pending")

    new_task = models.Task(
        title=task.title,
        description=task.description,
        status="pending",
        priority=count,  # auto assign
        client_id=client_id
    )

    db.add(new_task)
    db.commit()
    db.refresh(new_task)

    return new_task


# 📋 Get tasks for a client
from sqlalchemy import func

@router.get("/client/{client_id}")
def get_tasks(
    client_id: int,
    db: Session = Depends(get_db),
    user = Depends(get_current_user_dep)
):
    client = db.query(models.Client).filter(
        models.Client.id == client_id
    ).first()

    if not client or client.user_id != user.id:
        raise HTTPException(403, "Not allowed")

    tasks = db.query(models.Task).filter(
        models.Task.client_id == client_id,
        models.Task.archived == False
    ).all()

    result = []

    for task in tasks:

        total_hours = db.query(
            func.coalesce(func.sum(models.TimeLog.hours), 0)
        ).filter(
            models.TimeLog.task_id == task.id
        ).scalar()

        result.append({
            "id": task.id,
            "title": task.title,
            "description": task.description,
            "status": task.status,
            "priority": task.priority,
            "client_id": task.client_id,
            "total_hours": float(total_hours)
        })

    return result


# 🔄 Update Task (status / priority / edit)
@router.put("/{task_id}")
def update_task(
    task_id: int,
    updated: schemas.TaskUpdate,
    db: Session = Depends(get_db),
    user = Depends(get_current_user_dep)
):
    task = db.query(models.Task).filter(models.Task.id == task_id).first()

    if not task:
        raise HTTPException(404, "Task not found")

    # ownership check
    client = db.query(models.Client).filter(models.Client.id == task.client_id).first()
    if client.user_id != user.id:
        raise HTTPException(403, "Not allowed")

    # update fields
    if updated.title is not None:
        task.title = updated.title
    if updated.description is not None:
        task.description = updated.description
    if updated.status is not None:
        task.status = updated.status
    if updated.priority is not None:
        task.priority = updated.priority

    db.commit()
    db.refresh(task)

    return task


# ❌ Delete Task
@router.delete("/{task_id}")
def delete_task(
    task_id: int,
    db: Session = Depends(get_db),
    user = Depends(get_current_user_dep)
):
    task = db.query(models.Task).filter(models.Task.id == task_id).first()

    if not task:
        raise HTTPException(404, "Task not found")

    client = db.query(models.Client).filter(models.Client.id == task.client_id).first()
    if client.user_id != user.id:
        raise HTTPException(403, "Not allowed")

    db.delete(task)
    db.commit()

    return {"message": "Task deleted"}


# 📜 Completed tasks history
@router.get("/client/{client_id}/completed")
def completed_tasks(
    client_id: int,
    db: Session = Depends(get_db),
    user = Depends(get_current_user_dep)
):
    client = db.query(models.Client).filter(models.Client.id == client_id).first()

    if not client or client.user_id != user.id:
        raise HTTPException(403, "Not allowed")

    return db.query(models.Task).filter(
        models.Task.client_id == client_id,
        models.Task.status == "completed"
    ).all()


@router.patch("/reorder")
def reorder_task(
    data: schemas.TaskReorder,
    db: Session = Depends(get_db),
    user = Depends(get_current_user_dep)
):
    task = db.query(models.Task).filter(models.Task.id == data.task_id).first()

    if not task:
        raise HTTPException(404, "Task not found")

    # ownership check
    client = db.query(models.Client).filter(models.Client.id == task.client_id).first()
    if client.user_id != user.id:
        raise HTTPException(403, "Not allowed")

    old_status = task.status
    new_status = data.new_status
    new_pos = data.new_position

    # ---- GET TASKS IN TARGET COLUMN ----
    target_tasks = db.query(models.Task).filter(
        models.Task.client_id == task.client_id,
        models.Task.status == new_status
    ).order_by(models.Task.priority).all()

    # remove task if moving within same column
    if old_status == new_status:
        target_tasks = [t for t in target_tasks if t.id != task.id]

    # limit check (15 max)
    if new_status != "completed" and len(target_tasks) >= 15:
        raise HTTPException(400, "Max 15 tasks allowed in column")

    # insert task at new position
    target_tasks.insert(new_pos, task)

    # reassign priorities
    for idx, t in enumerate(target_tasks):
        t.priority = idx
        t.status = new_status

    # ---- FIX OLD COLUMN (if moved across) ----
    if old_status != new_status:
        old_tasks = db.query(models.Task).filter(
            models.Task.client_id == task.client_id,
            models.Task.status == old_status
        ).order_by(models.Task.priority).all()

        old_tasks = [t for t in old_tasks if t.id != task.id]

        for idx, t in enumerate(old_tasks):
            t.priority = idx

    db.commit()

    return {"message": "Task reordered"}


@router.post("/{task_id}/log-time")
def add_time_log(
    task_id: int,
    data: schemas.TimeLogCreate,
    db: Session = Depends(get_db),
    user = Depends(get_current_user_dep)
):
    task = db.query(models.Task).filter(models.Task.id == task_id).first()

    if not task:
        raise HTTPException(404, "Task not found")

    # ownership check
    client = db.query(models.Client).filter(models.Client.id == task.client_id).first()
    if client.user_id != user.id:
        raise HTTPException(403, "Not allowed")

    log = models.TimeLog(
        task_id=task_id,
        date=data.date,
        hours=data.hours,
        description=data.description
    )

    db.add(log)
    db.commit()

    return {"message": "Time logged"}


@router.get("/{task_id}/logs")
def get_time_logs(
    task_id: int,
    db: Session = Depends(get_db),
    user = Depends(get_current_user_dep)
):
    task = db.query(models.Task).filter(models.Task.id == task_id).first()

    if not task:
        raise HTTPException(404, "Task not found")

    client = db.query(models.Client).filter(
        models.Client.id == task.client_id
    ).first()

    if client.user_id != user.id:
        raise HTTPException(403, "Not allowed")

    return db.query(models.TimeLog).filter(
        models.TimeLog.task_id == task_id
    ).all()


@router.patch("/{task_id}/archive")
def archive_task(
    task_id: int,
    db: Session = Depends(get_db),
    user = Depends(get_current_user_dep)
):
    task = db.query(models.Task).filter(
        models.Task.id == task_id
    ).first()

    if not task:
        raise HTTPException(404, "Task not found")

    client = db.query(models.Client).filter(
        models.Client.id == task.client_id
    ).first()

    if client.user_id != user.id:
        raise HTTPException(403, "Not allowed")

    task.archived = True

    db.commit()

    return {"message": "Task archived"}