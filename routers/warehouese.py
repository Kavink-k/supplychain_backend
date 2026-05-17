# from fastapi import APIRouter, Depends
# from sqlalchemy.orm import Session
# import models
# from database import get_db
# from routers.auth import require_role

# router = APIRouter()

# @router.get("/pending-orders")
# def get_pending_orders(db: Session = Depends(get_db)):

#     orders = db.query(models.Order).filter(
#         models.Order.status == "Pending"
#     ).all()

#     return orders

# @router.patch("/{order_id}/pack")
# def mark_as_packed(order_id: int, db: Session = Depends(get_db)):

#     order = db.query(models.Order).filter(models.Order.id == order_id).first()

#     if not order:
#         return {"error": "Order not found"}

#     if order.status != "Pending":
#         return {"error": "Only pending orders can be packed"}

#     order.status = "Packed"

#     db.commit()

#     return {"message": "Order packed successfully"}


from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
import models
from database import get_db
from routers.auth import require_role

router = APIRouter()


@router.get("/pending-orders")
def get_pending_orders(
    db: Session = Depends(get_db),
    current_user: models.User = Depends(require_role("warehouse"))
):

    orders = db.query(models.Order).filter(
        models.Order.status == "Pending"
    ).all()

    return orders


@router.patch("/{order_id}/pack")
def mark_as_packed(
    order_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(require_role("warehouse"))
):

    order = db.query(models.Order).filter(
        models.Order.id == order_id
    ).first()

    if not order:
        raise HTTPException(
            status_code=404,
            detail="Order not found"
        )

    if order.status != "Pending":
        raise HTTPException(
            status_code=400,
            detail="Only pending orders can be packed"
        )

    order.status = "Packed"

    db.commit()

    return {"message": "Order packed successfully"}