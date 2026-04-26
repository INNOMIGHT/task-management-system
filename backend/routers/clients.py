from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
import models, schemas
from deps import get_db, get_current_user_dep

router = APIRouter(prefix="/clients", tags=["Clients"])


# ➕ Create Client
@router.post("/")
def create_client(
    client: schemas.ClientCreate,
    db: Session = Depends(get_db),
    user = Depends(get_current_user_dep)
):
    new_client = models.Client(
        name=client.name,
        user_id=user.id
    )

    db.add(new_client)
    db.commit()
    db.refresh(new_client)

    return new_client


# 📋 Get All Clients (only for logged-in user)
@router.get("/")
def get_clients(
    db: Session = Depends(get_db),
    user = Depends(get_current_user_dep)
):
    return db.query(models.Client).filter(models.Client.user_id == user.id).all()


# ❌ Delete Client (with ownership check)
@router.delete("/{client_id}")
def delete_client(
    client_id: int,
    db: Session = Depends(get_db),
    user = Depends(get_current_user_dep)
):
    client = db.query(models.Client).filter(models.Client.id == client_id).first()

    if not client:
        raise HTTPException(status_code=404, detail="Client not found")

    if client.user_id != user.id:
        raise HTTPException(status_code=403, detail="Not allowed")

    db.delete(client)
    db.commit()

    return {"message": "Client deleted"}