from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
import models
from database import get_db

router = APIRouter()


@router.get("/order/{order_id}")
def track_by_order_id(order_id: int, db: Session = Depends(get_db)):

    order = db.query(models.Order).filter(
        models.Order.id == order_id
    ).first()

    if not order:
        return {"error": "Order not found"}

    return {
        "order_id": order.id,
        "customer_name": order.customer_name,
        "status": order.status,
        "priority": order.priority
    }
    
    
@router.get("/phone/{phone}")
def track_by_phone(phone: str, db: Session = Depends(get_db)):

    orders = db.query(models.Order).filter(
        models.Order.phone == phone
    ).first()

    if not orders:
        return {"error": "No orders found"}

    return {
        "order_id": orders.id,
        "customer_name": orders.customer_name,
        "status": orders.status,
        "priority": orders.priority
            }