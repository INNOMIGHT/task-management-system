from fastapi import FastAPI, Depends
import models
from database import engine
from routers import auth
from deps import get_current_user_dep
from routers import clients
from routers import tasks
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

origins = [
    "http://localhost:3000",
    "https://innomight.github.io"
]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

models.Base.metadata.create_all(bind=engine)

app = FastAPI()

origins = [
    "http://localhost:3000",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router)

@app.get("/")
def root():
    return {"message": "API running"}

@app.get("/me")
def get_me(user = Depends(get_current_user_dep)):
    return {"email": user.email}


app.include_router(clients.router)
app.include_router(tasks.router)