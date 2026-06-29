from fastapi import APIRouter,Depends,HTTPException

# pyrefly: ignore [missing-import]
from sqlalchemy.orm import Session

from typing import List

from database import get_db

import models
import schemas

from routers.auth import (
    get_current_user
)


router = APIRouter()


# =====================================================
# GET ALL NOTIFICATIONS
# =====================================================

@router.get (
    "/",
    response_model=List[
        schemas.NotificationResponse
    ]
)
def get_notifications(

    db: Session = Depends(get_db),

    current_user:
        models.User = Depends(
            get_current_user
        )
):

    notifications = db.query(
        models.Notification
    ).order_by(
        models.Notification.created_at.desc()
    ).all()

    return notifications


# =====================================================
# CREATE NOTIFICATION
# =====================================================

@router.post("/")
def create_notification(

    data:
        schemas.NotificationCreate,

    db: Session = Depends(get_db)
):

    notification =models.Notification(

            title=data.title,

            message=data.message,

            type=data.type
        )

    db.add(notification)

    db.commit()

    return {
        "message":
            "Notification created"
    }


# =====================================================
# MARK AS READ
# =====================================================

@router.patch("/{notification_id}/read")
def mark_as_read(

    notification_id: int,

    db: Session = Depends(get_db)
):

    notification = db.query(
        models.Notification
    ).filter(
        models.Notification.id
        == notification_id
    ).first()

    if not notification:

        raise HTTPException(

            status_code=404,

            detail=
                "Notification not found"
        )

    notification.is_read = True

    db.commit()

    return {
        "message":
            "Notification marked as read"
    }


# =====================================================
# DELETE NOTIFICATION
# =====================================================

@router.delete("/{notification_id}")
def delete_notification(

    notification_id: int,

    db: Session = Depends(get_db)
):

    notification = db.query(
        models.Notification
    ).filter(
        models.Notification.id
        == notification_id
    ).first()

    if not notification:

        raise HTTPException(

            status_code=404,

            detail=
                "Notification not found"
        )

    db.delete(notification)

    db.commit()

    return {
        "message":
            "Notification deleted"
    }


# =====================================================
# LOW STOCK ALERTS
# =====================================================

@router.post("/generate-low-stock")
def generate_low_stock_alerts(

    db: Session = Depends(get_db)
):
    try:
        inventory = db.query(
            models.Inventory
        ).all()

        generated = 0

        for item in inventory:

            if item.quantity <= 10:

                existing = db.query(
                    models.Notification
                ).filter(

                    models.Notification.title
                    == f"Low Stock: {item.item_name}"

                ).first()

                if not existing:

                    notification = models.Notification(

                        title=
                            f"Low Stock: {item.item_name}",

                        message=
                            f"{item.item_name} stock is critically low ({item.quantity})",

                        type="LOW_STOCK"
                    )

                    db.add(notification)

                    generated += 1

        db.commit()

        return {
            "message": "Low stock alerts generated",
            "count": generated
        }

    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=500,
            detail=f"Failed to generate low stock alerts: {str(e)}"
        )


# =====================================================
# DELAYED ORDER ALERTS
# =====================================================

@router.post("/generate-delayed-orders")
def generate_delayed_alerts(

    db: Session = Depends(get_db)
):
    try:
        delayed_orders = db.query(
            models.Order
        ).filter(
            models.Order.is_delayed == True
        ).all()

        generated = 0

        for order in delayed_orders:

            existing = db.query(
                models.Notification
            ).filter(

                models.Notification.title
                == f"Delayed Order #{order.id}"

            ).first()

            if not existing:

                notification = models.Notification(

                    title=
                        f"Delayed Order #{order.id}",

                    message=
                        f"Order #{order.id} is delayed",

                    type="DELAY_ALERT"
                )

                db.add(notification)

                generated += 1

        db.commit()

        return {
            "message": "Delayed alerts generated",
            "count": generated
        }

    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=500,
            detail=f"Failed to generate delayed order alerts: {str(e)}"
        )