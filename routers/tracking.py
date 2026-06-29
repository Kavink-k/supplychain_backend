# from fastapi import APIRouter, Depends
# from sqlalchemy.orm import Session
# import models
# from database import get_db

# router = APIRouter()


# @router.get("/order/{order_id}")
# def track_by_order_id(order_id: int, db: Session = Depends(get_db)):

#     order = db.query(models.Order).filter(
#         models.Order.id == order_id
#     ).first()

#     if not order:
#         return {"error": "Order not found"}

#     return {
#         "order_id": order.id,
#         "customer_name": order.customer_name,
#         "status": order.status,
#         "priority": order.priority
#     }
    
    
# @router.get("/phone/{phone}")
# def track_by_phone(phone: str, db: Session = Depends(get_db)):

#     orders = db.query(models.Order).filter(
#         models.Order.phone == phone
#     ).first()

#     if not orders:
#         return {"error": "No orders found"}

#     return {
#         "order_id": orders.id,
#         "customer_name": orders.customer_name,
#         "status": orders.status,
#         "priority": orders.priority
#             }


from fastapi import (
    APIRouter,
    Depends,
    HTTPException
)

from sqlalchemy.orm import Session

from database import get_db

import models
import schemas


router = APIRouter()


# =====================================================
# TRACK BY ORDER ID
# =====================================================

@router.get(
    "/order/{order_id}",
    response_model=schemas.OrderResponse
)
def track_order_by_id(

    order_id: int,

    db: Session = Depends(get_db)
):

    order = db.query(
        models.Order
    ).filter(
        models.Order.id == order_id
    ).first()

    if not order:

        raise HTTPException(
            status_code=404,
            detail="Order not found"
        )

    return order


# =====================================================
# TRACK BY PHONE
# =====================================================

@router.get(
    "/phone/{phone}",
    response_model=list[
        schemas.OrderResponse
    ]
)
def track_order_by_phone(

    phone: str,

    db: Session = Depends(get_db)
):

    orders = db.query(
        models.Order
    ).filter(
        models.Order.phone == phone
    ).all()

    if not orders:

        raise HTTPException(
            status_code=404,
            detail="No orders found"
        )

    return orders


# =====================================================
# TRACK TIMELINE ONLY
# =====================================================

@router.get(
    "/timeline/{order_id}",
    response_model=list[
        schemas.TimelineResponse
    ]
)
def order_timeline(

    order_id: int,

    db: Session = Depends(get_db)
):

    timeline = db.query(
        models.OrderTimeline
    ).filter(
        models.OrderTimeline.order_id
        == order_id
    ).order_by(
        models.OrderTimeline.timestamp.asc()
    ).all()

    if not timeline:

        raise HTTPException(
            status_code=404,
            detail="Timeline not found"
        )

    return timeline