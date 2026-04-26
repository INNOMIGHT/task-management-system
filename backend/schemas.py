from pydantic import BaseModel
from typing import Optional

# -------- USER --------
class UserCreate(BaseModel):
    email: str
    password: str

class UserLogin(BaseModel):
    email: str
    password: str


# -------- CLIENT --------
class ClientCreate(BaseModel):
    name: str


# -------- TASK --------
class TaskCreate(BaseModel):
    title: str
    description: Optional[str] = None

class TaskUpdate(BaseModel):
    title: Optional[str]
    description: Optional[str]
    status: Optional[str]
    priority: Optional[int]

class TaskReorder(BaseModel):
    task_id: int
    new_status: str   # pending / ongoing / completed
    new_position: int