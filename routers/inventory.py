from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

import models
import schemas

from database import get_db
from routers.auth import require_role

router = APIRouter()


@router.post("/")
def add_inventory_item(
    item: schemas.InventoryCreate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(require_role("admin"))
):

    existing_item = db.query(models.Inventory).filter(
        models.Inventory.item_name == item.item_name
    ).first()

    if existing_item:
        raise HTTPException(
            status_code=400,
            detail="Item already exists"
        )

    new_item = models.Inventory(
        item_name=item.item_name,
        quantity=item.quantity
    )

    db.add(new_item)
    db.commit()

    return {"message": "Inventory item added"} 


@router.get("/", response_model=List[schemas.InventoryResponse])
def get_inventory(
    db: Session = Depends(get_db),
    current_user: models.User = Depends(require_role("admin"))
):

    items = db.query(models.Inventory).all()

    return items


@router.patch("/{item_id}")
def update_inventory(
    item_id: int,
    quantity: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(require_role("admin"))
):

    item = db.query(models.Inventory).filter(
        models.Inventory.id == item_id
    ).first()

    if not item:
        raise HTTPException(
            status_code=404,
            detail="Item not found"
        )

    item.quantity = quantity

    db.commit()

    return {"message": "Inventory updated"}


@router.delete("/{item_id}")
def delete_inventory_item(
    item_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(require_role("admin"))
):

    item = db.query(models.Inventory).filter(
        models.Inventory.id == item_id
    ).first()

    if not item:
        raise HTTPException(
            status_code=404,
            detail="Item not found"
        )

    db.delete(item)
    db.commit()

    return {"message": "Inventory item deleted"}