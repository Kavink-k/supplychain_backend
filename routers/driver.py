# from fastapi import APIRouter, Depends
# from sqlalchemy.orm import Session
# import models
# from database import get_db
# from sqlalchemy import case

# router = APIRouter()

# @router.get("/{driver_id}/orders")
# def get_driver_orders(driver_id: int, db: Session = Depends(get_db)):

#     orders = db.query(models.Order).filter(
#         models.Order.driver_id == driver_id
#     ).order_by(
#         case(
#             (models.Order.priority == "HIGH", 1),
#             (models.Order.priority == "MEDIUM", 2),
#             (models.Order.priority == "LOW", 3),
#         )
#     ).all()

#     return orders

# @router.patch("/{order_id}/status")
# def driver_update_status(
#     order_id: int,
#     status: str,
#     db: Session = Depends(get_db)
    
# ):

#     order = db.query(models.Order).filter(models.Order.id == order_id).first()

#     if not order:
#         return {"error": "Order not found"}

#     # Driver allowed flow
#     valid_flow = {
#         "Packed": ["Out for Delivery"],
#         "Out for Delivery": ["Delivered"]
#     }

#     if order.status not in valid_flow or status not in valid_flow[order.status]:
#         return {"error": "Invalid status update"}

#     order.status = status

#     db.commit()

#     return {"message": "Updated by driver", "status": order.status}

from fastapi import APIRouter, Depends, HTTPException
import models
from database import get_db
from sqlalchemy.orm import Session
from sqlalchemy import case
from routers.auth import require_role

router = APIRouter()


@router.get("/my-orders")
def get_driver_orders(db: Session = Depends(get_db),current_user: models.User = Depends(require_role("driver"))):

    orders = db.query(models.Order).filter(
        models.Order.driver_id == current_user.id
    ).order_by(
        case(
            (models.Order.priority == "HIGH", 1),
            (models.Order.priority == "MEDIUM", 2),
            (models.Order.priority == "LOW", 3),
        )
    ).all()

    return orders


@router.patch("/{order_id}/status")
def driver_update_status(
    order_id: int,
    status: str,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(require_role("driver"))
):

    order = db.query(models.Order).filter(
        models.Order.id == order_id
    ).first()

    if not order:
        raise HTTPException(
            status_code=404,
            detail="Order not found"
        )

    if order.driver_id != current_user.id:
        raise HTTPException(
            status_code=403,
            detail="Not your order"
        )

    valid_flow = {
        "Packed": ["Out for Delivery"],
        "Out for Delivery": ["Delivered"]
    }

    if order.status not in valid_flow or status not in valid_flow[order.status]:
        raise HTTPException(
            status_code=400,
            detail="Invalid status update"
        )

    order.status = status

    db.commit()

    return {
        "message": "Updated by driver",
        "status": order.status
    }