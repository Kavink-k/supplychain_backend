from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from database import get_db

import models


router = APIRouter()


# =====================================================
# DASHBOARD STATS
# =====================================================

@router.get("/stats")
def dashboard_stats(

    db: Session = Depends(get_db)
):

    orders = db.query(
        models.Order
    ).all()

    inventory = db.query(
        models.Inventory
    ).all()

    drivers = db.query(
        models.User
    ).filter(
        models.User.role == "driver"
    ).all()

    total_orders = len(orders)

    active_deliveries = len([

        o for o in orders

        if o.status in [
            "DISPATCHED",
            "OUT_FOR_DELIVERY",
            "DRIVER_ASSIGNED"
        ]
    ])

    delayed_orders = len([

        o for o in orders

        if o.is_delayed
    ])

    total_revenue = sum([

        o.total_amount or 0

        for o in orders

        if o.payment_status == "PAID"
    ])

    low_stock_count = len([

        item for item in inventory

        if item.quantity <= 10
    ])

    available_drivers = len([

        d for d in drivers

        if d.availability == "AVAILABLE"
    ])

    busy_drivers = len([

        d for d in drivers

        if d.availability == "BUSY"
    ])

    return {

        "total_orders":
            total_orders,

        "active_deliveries":
            active_deliveries,

        "delayed_orders":
            delayed_orders,

        "total_revenue":
            total_revenue,

        "low_stock_count":
            low_stock_count,

        "available_drivers":
            available_drivers,

        "busy_drivers":
            busy_drivers
    }