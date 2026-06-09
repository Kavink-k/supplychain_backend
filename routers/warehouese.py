# from fastapi import APIRouter, Depends, HTTPException
# from sqlalchemy.orm import Session
# import models
# from database import get_db
# from routers.auth import require_role

# router = APIRouter()


# @router.get("/pending-orders")
# def get_pending_orders(
#     db: Session = Depends(get_db),
#     current_user: models.User = Depends(require_role("warehouse"))
# ):

#     orders = db.query(models.Order).filter(
#         models.Order.status == "Pending"
#     ).all()

#     return orders


# @router.patch("/{order_id}/pack")
# def mark_as_packed(
#     order_id: int,
#     db: Session = Depends(get_db),
#     current_user: models.User = Depends(require_role("warehouse"))
# ):

#     order = db.query(models.Order).filter(
#         models.Order.id == order_id
#     ).first()

#     if not order:
#         raise HTTPException(
#             status_code=404,
#             detail="Order not found"
#         )

#     if order.status != "Pending":
#         raise HTTPException(
#             status_code=400,
#             detail="Only pending orders can be packed"
#         )

#     order.status = "Packed"

#     db.commit()

#     return {"message": "Order packed successfully"}


from fastapi import (
    APIRouter,
    Depends,
    HTTPException
)

from sqlalchemy.orm import Session

from typing import List

from database import get_db

import models
import schemas

from routers.auth import require_role

from datetime import datetime


router = APIRouter()


# =====================================================
# GET PENDING ORDERS
# =====================================================

@router.get(
    "/pending-orders",
    response_model=List[
        schemas.OrderResponse
    ]
)
def get_pending_orders(

    db: Session = Depends(get_db),

    current_user:
        models.User = Depends(
            require_role("warehouse")
        )
):

    orders = db.query(
        models.Order
    ).filter(

        models.Order.status.in_([
            "PENDING",
            "PACKING",
            "PACKED"
        ])

    ).all()

    return orders


# =====================================================
# START PACKING
# =====================================================

@router.patch("/{order_id}/start-packing")
def start_packing(

    order_id: int,

    db: Session = Depends(get_db),

    current_user:
        models.User = Depends(
            require_role("warehouse")
        )
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

    # VALIDATION

    if order.status != "PENDING":

        raise HTTPException(
            status_code=400,
            detail="Only pending orders can start packing"
        )

    # UPDATE STATUS

    order.status = "PACKING"

    # TIMELINE ENTRY

    timeline = models.OrderTimeline(

            order_id=order.id,

            status="PACKING",

            updated_by=current_user.name,

            note="Warehouse started packing"
        )

    db.add(timeline)

    db.commit()

    return {
        "message":
            "Packing started"
    }


# =====================================================
# COMPLETE PACKING
# =====================================================

@router.patch("/{order_id}/pack")
def pack_order(

    order_id: int,

    db: Session = Depends(get_db),

    current_user:
        models.User = Depends(
            require_role("warehouse")
        )
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

    # VALIDATION

    if order.status not in [
        "PENDING",
        "PACKING"
    ]:

        raise HTTPException(
            status_code=400,
            detail="Invalid workflow"
        )

    # UPDATE STATUS

    order.status = "PACKED"

    # TIMELINE

    timeline =models.OrderTimeline(

            order_id=order.id,

            status="PACKED",

            updated_by=current_user.name,

            note="Order packed successfully"
        )

    db.add(timeline)

    db.commit()

    return {
        "message":
            "Order packed successfully"
    }


# =====================================================
# DISPATCH ORDER
# =====================================================

@router.patch("/{order_id}/dispatch")
def dispatch_order(

    order_id: int,

    db: Session = Depends(get_db),

    current_user:
        models.User = Depends(
            require_role("warehouse")
        )
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

    # VALIDATION

    if order.status != "DRIVER_ASSIGNED":

        raise HTTPException(
            status_code=400,
            detail="Driver must be assigned before dispatch"
        )

    # UPDATE STATUS

    order.status = "DISPATCHED"

    # ESTIMATED DELIVERY

    order.estimated_delivery = (
        datetime.utcnow()
    )

    # TIMELINE ENTRY

    timeline = models.OrderTimeline(

            order_id=order.id,

            status="DISPATCHED",

            updated_by=current_user.name,

            note="Shipment dispatched"
        )

    db.add(timeline)

    db.commit()

    return {
        "message":
            "Order dispatched"
    }


# =====================================================
# WAREHOUSE STATS
# =====================================================

@router.get("/stats")
def warehouse_stats(

    db: Session = Depends(get_db),

    current_user:
        models.User = Depends(
            require_role("warehouse")
        )
):

    pending_orders = db.query(
        models.Order
    ).filter(
        models.Order.status == "PENDING"
    ).count()

    packing_orders = db.query(
        models.Order
    ).filter(
        models.Order.status == "PACKING"
    ).count()

    packed_orders = db.query(
        models.Order
    ).filter(
        models.Order.status == "PACKED"
    ).count()

    dispatched_orders = db.query(
        models.Order
    ).filter(
        models.Order.status == "DISPATCHED"
    ).count()

    return {

        "pending_orders":
            pending_orders,

        "packing_orders":
            packing_orders,

        "packed_orders":
            packed_orders,

        "dispatched_orders":
            dispatched_orders
    }