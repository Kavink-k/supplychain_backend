from fastapi import APIRouter, Depends ,HTTPException
from sqlalchemy.orm import Session
from typing import List
import models
import schemas
from database import get_db
from datetime import datetime
from routers.auth import require_role


router = APIRouter()


@router.get("/", response_model=List[schemas.OrderResponse])
def get_orders(db: Session = Depends(get_db)):

    orders = db.query(models.Order).all()

    for order in orders:
        time_diff = datetime.utcnow() - order.created_at

        # ⏱ Check delay (2 hours = 7200 seconds)
        if order.status == "Pending" and time_diff.seconds > 7200:
            order.priority = "HIGH"   # auto boost
            order.is_delayed = True   # 👈 new flag
        else:
            order.is_delayed = False

    return orders

@router.post("/")
def create_order(order: schemas.OrderCreate, db: Session = Depends(get_db)):

    # 🧠 Priority logic based on item count
    item_count = len(order.items)

    if item_count >= 5:
        priority = "HIGH"
    elif item_count >= 3:
        priority = "MEDIUM"
    else:
        priority = "LOW"

    # 1️⃣ Create order
    new_order = models.Order(
        customer_name=order.customer_name,
        phone=order.phone,
        address=order.address,
        status="Pending",
        priority=priority
    )

    db.add(new_order)
    db.commit()
    db.refresh(new_order)

    # 2️⃣ Add items
    for item in order.items:

    # 🔍 Find inventory item
        inventory_item = db.query(models.Inventory).filter(
            models.Inventory.item_name == item.item_name
        ).first()

        # ❌ Item not found
        if not inventory_item:
            raise HTTPException(
                status_code=404,
                detail=f"{item.item_name} not found in inventory"
            )

        # ❌ Not enough stock
        if inventory_item.quantity < item.quantity:
            raise HTTPException(
                status_code=400,
                detail=f"Insufficient stock for {item.item_name}"
            )

        # ➖ Reduce stock
        inventory_item.quantity -= item.quantity

        # 🧾 Add order item
        new_item = models.OrderItem(
            order_id=new_order.id,
            item_name=item.item_name,
            quantity=item.quantity
        )

        db.add(new_item)

    db.commit()

    return {
        "message": "Order Created with Smart Priority",
        "priority": priority,
        "order_id": new_order.id
    }  

@router.patch("/{order_id}/assign-driver")
def assign_driver(
    order_id: int,
    data: schemas.AssignDriver,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(require_role("admin"))
):
    
    order = db.query(models.Order).filter(
        models.Order.id == order_id
    ).first()

    if not order:
        return {"error": "Order not found"}

    # assign only after packing
    if order.status != "Packed":
        return {"error": "Driver can be assigned only after packing"}

    order.driver_id = data.driver_id

    db.commit()

    return {
        "message": "Driver assigned successfully",
        "driver_id": order.driver_id
    }
    
    
    