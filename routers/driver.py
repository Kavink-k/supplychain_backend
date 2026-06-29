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

from datetime import datetime
import math

from routers.auth import require_role


router = APIRouter()


# =====================================================
# GET DRIVER ORDERS
# =====================================================

@router.get(
    "/my-orders",
    response_model=List[
        schemas.OrderResponse
    ]
)
def get_driver_orders(

    db: Session = Depends(get_db),

    current_user:
        models.User = Depends(
            require_role("driver")
        )
):

    orders = db.query(
        models.Order
    ).filter(
        models.Order.driver_id
        == current_user.id
    ).all()

    return orders


# =====================================================
# UPDATE DELIVERY STATUS
# =====================================================

@router.patch("/{order_id}/status")
def update_delivery_status(

    order_id: int,

    data: schemas.UpdateStatus,

    db: Session = Depends(get_db),

    current_user:
        models.User = Depends(
            require_role("driver")
        )
):

    order = db.query(
        models.Order
    ).filter(

        models.Order.id == order_id,

        models.Order.driver_id
        == current_user.id

    ).first()

    if not order:

        raise HTTPException(
            status_code=404,
            detail="Order not found"
        )

    # =========================================
    # VALID STATUS FLOW
    # =========================================

    allowed_status = [

        "DISPATCHED",

        "OUT_FOR_DELIVERY",

        "DELIVERED",

        "FAILED",

        "RETURNED",

        "CUSTOMER_UNAVAILABLE"
    ]

    if data.status not in allowed_status:

        raise HTTPException(
            status_code=400,
            detail="Invalid status"
        )

    # =========================================
    # UPDATE ORDER STATUS
    # =========================================

    order.status = data.status

    terminal_statuses = ["DELIVERED", "FAILED", "RETURNED", "CUSTOMER_UNAVAILABLE"]

    # DELIVERY COMPLETION / TERMINAL STATE

    if data.status in terminal_statuses:

        if data.status == "DELIVERED":
            order.delivered_at = datetime.utcnow()
        else:
            order.cancelled_at = datetime.utcnow()

        # REDUCE DRIVER WORKLOAD

        if (
            current_user.active_deliveries
            > 0
        ):

            current_user.active_deliveries -= 1

        # AUTO AVAILABLE

        if (
            current_user.active_deliveries
            < current_user.max_capacity
        ):

            current_user.availability = (
                "AVAILABLE"
            )

    # DRIVER BUSY STATUS

    else:

        current_user.availability = (
            "BUSY"
        )

    # =========================================
    # TIMELINE ENTRY
    # =========================================

    timeline =models.OrderTimeline(

            order_id=order.id,

            status=data.status,

            updated_by=current_user.name,

            note=data.note
        )

    db.add(timeline)

    db.commit()

    return {
        "message":
            "Delivery status updated",

        "status":
            order.status
    }


# =====================================================
# DRIVER DASHBOARD STATS
# =====================================================

@router.get("/stats")
def driver_stats(

    db: Session = Depends(get_db),

    current_user:
        models.User = Depends(
            require_role("driver")
        )
):

    total_orders = db.query(
        models.Order
    ).filter(
        models.Order.driver_id
        == current_user.id
    ).count()

    delivered_orders = db.query(
        models.Order
    ).filter(

        models.Order.driver_id
        == current_user.id,

        models.Order.status
        == "DELIVERED"

    ).count()

    active_orders = db.query(
        models.Order
    ).filter(

        models.Order.driver_id
        == current_user.id,

        models.Order.status.in_([
            "DRIVER_ASSIGNED",
            "DISPATCHED",
            "OUT_FOR_DELIVERY"
        ])

    ).count()

    # Calculate earnings
    completed_orders = db.query(
        models.Order
    ).filter(
        models.Order.driver_id == current_user.id,
        models.Order.status == "DELIVERED"
    ).all()

    base_pay_rate = 50
    base_pay = len(completed_orders) * base_pay_rate
    incentives = 0

    for order in completed_orders:
        if order.priority == "HIGH":
            incentives += 20
        elif order.priority == "MEDIUM":
            incentives += 10
        
        if not order.is_delayed:
            incentives += 10

    total_earnings = base_pay + incentives

    return {

        "driver": current_user.name,

        "availability":
            current_user.availability,

        "active_deliveries":
            current_user.active_deliveries,

        "max_capacity":
            current_user.max_capacity,

        "total_orders":
            total_orders,

        "delivered_orders":
            delivered_orders,

        "active_orders":
            active_orders,

        "earnings": {
            "base_pay": base_pay,
            "incentives": incentives,
            "total_earnings": total_earnings,
            "rate_per_delivery": base_pay_rate
        }
    }


# =====================================================
# GET DRIVER ORDERS OPTIMIZED (TSP Nearest Neighbor)
# =====================================================

@router.get(
    "/my-orders/optimized",
    response_model=List[schemas.OrderResponse]
)
def get_driver_orders_optimized(
    db: Session = Depends(get_db),
    current_user: models.User = Depends(require_role("driver"))
):
    orders = db.query(
        models.Order
    ).filter(
        models.Order.driver_id == current_user.id,
        models.Order.status.in_(["DRIVER_ASSIGNED", "DISPATCHED", "OUT_FOR_DELIVERY"])
    ).all()

    if not orders:
        return []

    # Warehouse location: Lat 19.0760, Lng 72.8777
    warehouse = (19.0760, 72.8777)
    
    def distance(p1, p2):
        # p1, p2: (lat, lng)
        return math.sqrt((p1[0] - p2[0])**2 + (p1[1] - p2[1])**2)

    optimized_orders = []
    unvisited = list(orders)
    current_loc = warehouse

    while unvisited:
        closest_order = min(
            unvisited,
            key=lambda o: distance(current_loc, (o.latitude if o.latitude is not None else 19.0760, o.longitude if o.longitude is not None else 72.8777))
        )
        unvisited.remove(closest_order)
        optimized_orders.append(closest_order)
        current_loc = (closest_order.latitude if closest_order.latitude is not None else 19.0760, closest_order.longitude if closest_order.longitude is not None else 72.8777)

    # Append terminal orders so driver can still view their history if they look
    other_orders = db.query(
        models.Order
    ).filter(
        models.Order.driver_id == current_user.id,
        ~models.Order.status.in_(["DRIVER_ASSIGNED", "DISPATCHED", "OUT_FOR_DELIVERY"])
    ).all()

    return optimized_orders + other_orders