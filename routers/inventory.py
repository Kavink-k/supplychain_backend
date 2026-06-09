# from fastapi import APIRouter, Depends, HTTPException
# from sqlalchemy.orm import Session
# from typing import List

# import models
# import schemas

# from database import get_db
# from routers.auth import require_role

# router = APIRouter()


# @router.post("/")
# def add_inventory_item(
#     item: schemas.InventoryCreate,
#     db: Session = Depends(get_db),
#     current_user: models.User = Depends(require_role("admin"))
# ):

#     existing_item = db.query(models.Inventory).filter(
#         models.Inventory.item_name == item.item_name
#     ).first()

#     if existing_item:
#         raise HTTPException(
#             status_code=400,
#             detail="Item already exists"
#         )

#     new_item = models.Inventory(
#         item_name=item.item_name,
#         quantity=item.quantity
#     )

#     db.add(new_item)
#     db.commit()

#     return {"message": "Inventory item added"} 


# @router.get("/", response_model=List[schemas.InventoryResponse])
# def get_inventory(
#     db: Session = Depends(get_db),
#     current_user: models.User = Depends(require_role("admin"))
# ):

#     items = db.query(models.Inventory).all()

#     return items


# @router.patch("/{item_id}")
# def update_inventory(
#     item_id: int,
#     quantity: int,
#     db: Session = Depends(get_db),
#     current_user: models.User = Depends(require_role("admin"))
# ):

#     item = db.query(models.Inventory).filter(
#         models.Inventory.id == item_id
#     ).first()

#     if not item:
#         raise HTTPException(
#             status_code=404,
#             detail="Item not found"
#         )

#     item.quantity = quantity

#     db.commit()

#     return {"message": "Inventory updated"}


# @router.delete("/{item_id}")
# def delete_inventory_item(
#     item_id: int,
#     db: Session = Depends(get_db),
#     current_user: models.User = Depends(require_role("admin"))
# ):

#     item = db.query(models.Inventory).filter(
#         models.Inventory.id == item_id
#     ).first()

#     if not item:
#         raise HTTPException(
#             status_code=404,
#             detail="Item not found"
#         )

#     db.delete(item)
#     db.commit()

#     return {"message": "Inventory item deleted"}


from fastapi import (
    APIRouter,
    Depends,
    HTTPException
)
from fastapi.responses import StreamingResponse

from sqlalchemy.orm import Session

from typing import List
import csv
from io import StringIO

from database import get_db

import models
import schemas

from routers.auth import require_role


router = APIRouter()

# =====================================================
# EXPORT ALL INVENTORY TO CSV
# =====================================================

@router.get("/export/csv")
def export_inventory_csv(
    db: Session = Depends(get_db),
    current_user: models.User = Depends(require_role("admin"))
):
    inventory = db.query(models.Inventory).all()
    f = StringIO()
    writer = csv.writer(f)
    writer.writerow(["Item ID", "Item Name", "Quantity", "Reserved Stock", "Status"])
    for item in inventory:
        status = "LOW_STOCK" if item.quantity <= 10 else "IN_STOCK"
        writer.writerow([item.id, item.item_name, item.quantity, item.reserved_stock, status])
    f.seek(0)
    response = StreamingResponse(f, media_type="text/csv")
    response.headers["Content-Disposition"] = "attachment; filename=inventory_export.csv"
    return response


# =====================================================
# GET INVENTORY
# =====================================================

@router.get(
    "/",
    response_model=List[
        schemas.InventoryResponse
    ]
)
def get_inventory(
    db: Session = Depends(get_db)
):

    inventory = db.query(
        models.Inventory
    ).all()

    return inventory


# =====================================================
# ADD INVENTORY
# =====================================================

@router.post("/")
def add_inventory(

    item: schemas.InventoryCreate,

    db: Session = Depends(get_db),

    current_user:
        models.User = Depends(
            require_role("admin")
        )
):

    existing_item = db.query(
        models.Inventory
    ).filter(
        models.Inventory.item_name
        == item.item_name
    ).first()

    # =========================================
    # UPDATE EXISTING STOCK
    # =========================================

    if existing_item:

        existing_item.quantity += (
            item.quantity
        )

        # INVENTORY LOG

        log = models.InventoryLog(

            inventory_id=
                existing_item.id,

            action="STOCK_ADDED",

            quantity=item.quantity
        )

        db.add(log)

        db.commit()

        return {
            "message":
                "Stock updated successfully"
        }

    # =========================================
    # CREATE NEW INVENTORY
    # =========================================

    new_item = models.Inventory(

        item_name=item.item_name,

        quantity=item.quantity
    )

    db.add(new_item)

    db.commit()

    db.refresh(new_item)

    # INVENTORY LOG

    log = models.InventoryLog(

        inventory_id=new_item.id,

        action="NEW_ITEM_CREATED",

        quantity=item.quantity
    )

    db.add(log)

    db.commit()

    return {
        "message":
            "Inventory item created"
    }


# =====================================================
# UPDATE INVENTORY
# =====================================================

@router.patch("/{inventory_id}")
def update_inventory(

    inventory_id: int,

    item: schemas.InventoryCreate,

    db: Session = Depends(get_db),

    current_user:
        models.User = Depends(
            require_role("admin")
        )
):

    inventory = db.query(
        models.Inventory
    ).filter(
        models.Inventory.id
        == inventory_id
    ).first()

    if not inventory:

        raise HTTPException(
            status_code=404,
            detail="Inventory item not found"
        )

    inventory.item_name = (
        item.item_name
    )

    inventory.quantity = (
        item.quantity
    )

    # INVENTORY LOG

    log = models.InventoryLog(

        inventory_id=inventory.id,

        action="STOCK_UPDATED",

        quantity=item.quantity
    )

    db.add(log)

    db.commit()

    return {
        "message":
            "Inventory updated"
    }


# =====================================================
# DELETE INVENTORY
# =====================================================

@router.delete("/{inventory_id}")
def delete_inventory(

    inventory_id: int,

    db: Session = Depends(get_db),

    current_user:
        models.User = Depends(
            require_role("admin")
        )
):

    inventory = db.query(
        models.Inventory
    ).filter(
        models.Inventory.id
        == inventory_id
    ).first()

    if not inventory:

        raise HTTPException(
            status_code=404,
            detail="Inventory item not found"
        )

    # INVENTORY LOG

    log = models.InventoryLog(

        inventory_id=inventory.id,

        action="ITEM_DELETED",

        quantity=inventory.quantity
    )

    db.add(log)

    db.delete(inventory)

    db.commit()

    return {
        "message":
            "Inventory deleted"
    }


# =====================================================
# LOW STOCK ALERTS
# =====================================================

@router.get("/low-stock")
def low_stock_items(

    db: Session = Depends(get_db)
):

    inventory = db.query(
        models.Inventory
    ).all()

    low_stock = []

    for item in inventory:

        if item.quantity <= 10:

            low_stock.append({

                "id": item.id,

                "item_name":
                    item.item_name,

                "quantity":
                    item.quantity,

                "warning":
                    "LOW STOCK"
            })

    return low_stock


# =====================================================
# INVENTORY LOGS
# =====================================================

@router.get(
    "/logs/{inventory_id}",
    response_model=List[
        schemas.InventoryLogResponse
    ]
)
def inventory_logs(

    inventory_id: int,

    db: Session = Depends(get_db)
):

    logs = db.query(
        models.InventoryLog
    ).filter(
        models.InventoryLog.inventory_id
        == inventory_id
    ).all()

    return logs


# =====================================================
# INVENTORY STATS
# =====================================================

@router.get("/stats")
def inventory_stats(

    db: Session = Depends(get_db)
):

    inventory = db.query(
        models.Inventory
    ).all()

    total_items = len(inventory)

    total_stock = sum(
        item.quantity
        for item in inventory
    )

    low_stock_count = len([

        item for item in inventory

        if item.quantity <= 10

    ])

    return {

        "total_items":
            total_items,

        "total_stock":
            total_stock,

        "low_stock_count":
            low_stock_count
    }