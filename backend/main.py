from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware

import models
from database import engine
from routers import auth, clients, tasks
from deps import get_current_user_dep

app = FastAPI()

# ✅ CORS (ONLY ONCE, BEFORE ROUTES)
origins = [
    "http://localhost:3000",
    "https://innomight.github.io",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# DB tables
models.Base.metadata.create_all(bind=engine)

# Routes
app.include_router(auth.router)
app.include_router(clients.router)
app.include_router(tasks.router)

@app.get("/")
def root():
    return {"message": "API running"}

@app.get("/me")
def get_me(user=Depends(get_current_user_dep)):
    return {"email": user.email}