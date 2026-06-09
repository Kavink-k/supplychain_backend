# from fastapi import APIRouter, Depends ,HTTPException
# from sqlalchemy.orm import Session
# from typing import List
# import models
# import schemas
# from database import get_db
# from datetime import datetime
# from routers.auth import require_role


# router = APIRouter()


# @router.get("/", response_model=List[schemas.OrderResponse])
# def get_orders(db: Session = Depends(get_db)):

#     orders = db.query(models.Order).all()

#     for order in orders:
#         time_diff = datetime.utcnow() - order.created_at

#         # ⏱ Check delay (2 hours = 7200 seconds)
#         if order.status == "Pending" and time_diff.seconds > 7200:
#             order.priority = "HIGH"   # auto boost
#             order.is_delayed = True   # 👈 new flag
#         else:
#             order.is_delayed = False

#     return orders

# @router.post("/")
# def create_order(order: schemas.OrderCreate, db: Session = Depends(get_db)):

#     # 🧠 Priority logic based on item count
#     item_count = len(order.items)

#     if item_count >= 5:
#         priority = "HIGH"
#     elif item_count >= 3:
#         priority = "MEDIUM"
#     else:
#         priority = "LOW"

#     # 1️⃣ Create order
#     new_order = models.Order(
#         customer_name=order.customer_name,
#         phone=order.phone,
#         address=order.address,
#         status="Pending",
#         priority=priority
#     )

#     db.add(new_order)
#     db.commit()
#     db.refresh(new_order)

#     # 2️⃣ Add items
#     for item in order.items:

#     # 🔍 Find inventory item
#         inventory_item = db.query(models.Inventory).filter(
#             models.Inventory.item_name == item.item_name
#         ).first()

#         # ❌ Item not found
#         if not inventory_item:
#             raise HTTPException(
#                 status_code=404,
#                 detail=f"{item.item_name} not found in inventory"
#             )

#         # ❌ Not enough stock
#         if inventory_item.quantity < item.quantity:
#             raise HTTPException(
#                 status_code=400,
#                 detail=f"Insufficient stock for {item.item_name}"
#             )

#         # ➖ Reduce stock
#         inventory_item.quantity -= item.quantity

#         # 🧾 Add order item
#         new_item = models.OrderItem(
#             order_id=new_order.id,
#             item_name=item.item_name,
#             quantity=item.quantity
#         )

#         db.add(new_item)

#     db.commit()

#     return {
#         "message": "Order Created with Smart Priority",
#         "priority": priority,
#         "order_id": new_order.id
#     }  

# @router.patch("/{order_id}/assign-driver")
# def assign_driver(
#     order_id: int,
#     data: schemas.AssignDriver,
#     db: Session = Depends(get_db),
#     current_user: models.User = Depends(require_role("admin"))
# ):
    
#     order = db.query(models.Order).filter(
#         models.Order.id == order_id
#     ).first()

#     if not order:
#         return {"error": "Order not found"}

#     # assign only after packing
#     if order.status != "Packed":
#         return {"error": "Driver can be assigned only after packing"}

#     order.driver_id = data.driver_id

#     db.commit()

#     return {
#         "message": "Driver assigned successfully",
#         "driver_id": order.driver_id
#     }
    
    
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

from datetime import datetime
import hashlib

from routers.auth import require_role


router = APIRouter()

def get_coords_from_address(address: str):
    # Deterministic latitude/longitude generation in Mumbai region (Lat 19.0760, Lng 72.8777)
    h = hashlib.md5(address.encode('utf-8')).hexdigest()
    lat_offset = (int(h[:4], 16) % 100 - 50) / 1000.0  # -0.05 to +0.05 degrees (~5km)
    lng_offset = (int(h[4:8], 16) % 100 - 50) / 1000.0  # -0.05 to +0.05 degrees
    return round(19.0760 + lat_offset, 6), round(72.8777 + lng_offset, 6)

# =====================================================
# EXPORT ALL ORDERS TO CSV
# =====================================================

@router.get("/export/csv")
def export_orders_csv(
    db: Session = Depends(get_db),
    current_user: models.User = Depends(require_role("admin"))
):
    orders = db.query(models.Order).all()
    f = StringIO()
    writer = csv.writer(f)
    writer.writerow([
        "Order ID", "Customer Name", "Phone", "Address", "Status",
        "Priority", "Total Amount", "Delivery Fee", "Payment Status",
        "Payment Method", "Driver", "Created At", "Delivered At"
    ])
    for o in orders:
        driver_name = o.driver.name if o.driver else "None"
        writer.writerow([
            o.id, o.customer_name, o.phone, o.address, o.status,
            o.priority, o.total_amount, o.delivery_fee, o.payment_status,
            o.payment_method, driver_name, o.created_at, o.delivered_at or "—"
        ])
    f.seek(0)
    response = StreamingResponse(f, media_type="text/csv")
    response.headers["Content-Disposition"] = "attachment; filename=orders_export.csv"
    return response

# =====================================================
# GET SINGLE ORDER
# =====================================================

@router.get(
    "/{order_id}",
    response_model=schemas.OrderResponse
)
def get_single_order(

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
# ORDER TIMELINE
# =====================================================

@router.get(
    "/{order_id}/timeline",
    response_model=List[
        schemas.TimelineResponse
    ]
)
def get_order_timeline(

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

    return timeline
# =====================================================
# GET ALL ORDERS
# =====================================================

@router.get(
    "/",
    response_model=List[
        schemas.OrderResponse
    ]
)
def get_orders(
    db: Session = Depends(get_db)
):

    orders = db.query(
        models.Order
    ).all()

    for order in orders:

        time_diff = (
            datetime.utcnow()
            - order.created_at
        )

        # DELAY DETECTION

        if (
            order.status == "PENDING"
            and time_diff.seconds > 7200
        ):

            order.priority = "HIGH"

            order.is_delayed = True

        else:

            order.is_delayed = False

    db.commit()

    return orders


# =====================================================
# CREATE ORDER
# =====================================================

@router.post("/")
def create_order(
    order: schemas.OrderCreate,
    db: Session = Depends(get_db)
):

    # =========================================
    # FIND OR CREATE CUSTOMER
    # =========================================

    customer = db.query(
        models.Customer
    ).filter(
        models.Customer.phone
        == order.phone
    ).first()

    if not customer:

        customer = models.Customer(
            name=order.customer_name,
            phone=order.phone,
            address=order.address
        )

        db.add(customer)

        db.commit()

        db.refresh(customer)

    # =========================================
    # PRIORITY LOGIC
    # =========================================

    item_count = len(order.items)

    if item_count >= 5:
        priority = "HIGH"

    elif item_count >= 3:
        priority = "MEDIUM"

    else:
        priority = "LOW"

    # =========================================
    # CALCULATE TOTAL
    # =========================================

    total_amount = 0

    for item in order.items:

        subtotal = (
            item.price
            * item.quantity
        )

        total_amount += subtotal

    total_amount += order.delivery_fee

    # Determine coordinates
    lat = order.latitude
    lng = order.longitude
    if lat is None or lng is None:
        lat, lng = get_coords_from_address(order.address)

    # =========================================
    # CREATE ORDER
    # =========================================

    new_order = models.Order(

        customer_id=customer.id,

        customer_name=order.customer_name,

        phone=order.phone,

        address=order.address,

        status="PENDING",

        priority=priority,

        payment_method=
            order.payment_method,

        payment_status="PENDING",

        total_amount=total_amount,

        delivery_fee=order.delivery_fee,

        latitude=lat,

        longitude=lng,
    )

    db.add(new_order)

    db.commit()

    db.refresh(new_order)

    # =========================================
    # CREATE ORDER ITEMS
    # =========================================

    for item in order.items:

        # FIND INVENTORY

        inventory_item = db.query(
            models.Inventory
        ).filter(
            models.Inventory.item_name
            == item.item_name
        ).first()

        # ITEM NOT FOUND

        if not inventory_item:

            raise HTTPException(
                status_code=404,
                detail=f"{item.item_name} not found"
            )

        # STOCK VALIDATION

        if (
            inventory_item.quantity
            < item.quantity
        ):

            raise HTTPException(
                status_code=400,
                detail=f"Insufficient stock for {item.item_name}"
            )

        # STOCK REDUCTION

        inventory_item.quantity -= (
            item.quantity
        )

        # CREATE ORDER ITEM

        subtotal = (
            item.price
            * item.quantity
        )

        new_item = models.OrderItem(

            order_id=new_order.id,

            item_name=item.item_name,

            quantity=item.quantity,

            price=item.price,

            subtotal=subtotal
        )

        db.add(new_item)

        # =====================================
        # INVENTORY LOG
        # =====================================

        inventory_log = models.InventoryLog(

                inventory_id=
                    inventory_item.id,

                action="ORDER_USED",

                quantity=item.quantity,

                reference_order=
                    new_order.id
            )

        db.add(inventory_log)

    # =========================================
    # CREATE TIMELINE ENTRY
    # =========================================

    timeline = models.OrderTimeline(

            order_id=new_order.id,

            status="PENDING",

            updated_by="SYSTEM",

            note="Order Created"
        )

    db.add(timeline)

    db.commit()

    return {
        "message":
            "Order Created Successfully",

        "order_id":
            new_order.id,

        "priority":
            priority,

        "total_amount":
            total_amount
    }


# =====================================================
# ASSIGN DRIVER
# =====================================================

@router.patch("/{order_id}/assign-driver")
def assign_driver(

    order_id: int,

    data: schemas.AssignDriver,

    db: Session = Depends(get_db),

    current_user:
        models.User = Depends(
            require_role("admin")
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

    # ONLY PACKED ORDERS

    if order.status != "PACKED":

        raise HTTPException(
            status_code=400,
            detail="Only packed orders can be assigned"
        )

    # FIND DRIVER

    driver = db.query(
        models.User
    ).filter(

        models.User.id
        == data.driver_id,

        models.User.role
        == "driver"

    ).first()

    if not driver:

        raise HTTPException(
            status_code=404,
            detail="Driver not found"
        )

    # CHECK WORKLOAD LIMITS
    if driver.active_deliveries >= driver.max_capacity:
        raise HTTPException(
            status_code=400,
            detail=f"Driver has reached maximum delivery capacity ({driver.max_capacity} active deliveries)"
        )

    # CHECK AVAILABILITY

    if driver.availability != "AVAILABLE":

        raise HTTPException(
            status_code=400,
            detail="Driver unavailable"
        )

    # ASSIGN DRIVER

    order.driver_id = driver.id

    order.status = "DRIVER_ASSIGNED"

    order.assigned_at = (
        datetime.utcnow()
    )

    # UPDATE DRIVER WORKLOAD

    driver.active_deliveries += 1

    # UPDATE DRIVER STATUS IF BUSY
    if driver.active_deliveries >= driver.max_capacity:
        driver.availability = "BUSY"

    # TIMELINE ENTRY

    timeline = models.OrderTimeline(

            order_id=order.id,

            status="DRIVER_ASSIGNED",

            updated_by=current_user.name,

            note=f"Assigned to {driver.name}"
        )

    db.add(timeline)

    db.commit()

    return {
        "message":
            "Driver assigned successfully",

        "driver":
            driver.name
    }

# =====================================================
# SMART DRIVER AUTO ASSIGNMENT
# =====================================================

@router.patch("/{order_id}/auto-assign")
def auto_assign_driver(

    order_id: int,

    db: Session = Depends(get_db),

    current_user:
        models.User = Depends(
            require_role("admin")
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

    # ONLY PACKED ORDERS

    if order.status != "PACKED":

        raise HTTPException(

            status_code=400,

            detail=
                "Only packed orders can be assigned"
        )

    # =========================================
    # FIND AVAILABLE DRIVERS
    # =========================================

    available_drivers = db.query(
        models.User
    ).filter(

        models.User.role == "driver",

        models.User.availability
        == "AVAILABLE",

        models.User.active_deliveries
        < models.User.max_capacity

    ).all()

    if not available_drivers:

        raise HTTPException(

            status_code=400,

            detail=
                "No available drivers"
        )

    # =========================================
    # SMART SORTING
    # LEAST BUSY DRIVER
    # =========================================

    selected_driver = min(

        available_drivers,

        key=lambda driver:
            driver.active_deliveries
    )

    # =========================================
    # ASSIGN DRIVER
    # =========================================

    order.driver_id = (
        selected_driver.id
    )

    order.status = (
        "DRIVER_ASSIGNED"
    )

    order.assigned_at = (
        datetime.utcnow()
    )

    # DRIVER WORKLOAD

    selected_driver.active_deliveries += 1

    # AUTO BUSY STATUS

    if (
        selected_driver.active_deliveries
        >= selected_driver.max_capacity
    ):

        selected_driver.availability = (
            "BUSY"
        )

    # =========================================
    # TIMELINE ENTRY
    # =========================================

    timeline = models.OrderTimeline(

        order_id=order.id,

        status="DRIVER_ASSIGNED",

        updated_by="SMARTOPS_AI",

        note=f"Auto assigned to {selected_driver.name}"
    )

    db.add(timeline)

    db.commit()

    return {

        "message":
            "Driver auto assigned",

        "driver":
            selected_driver.name,

        "active_deliveries":
            selected_driver.active_deliveries
    }
# =====================================================
# UPDATE PAYMENT STATUS
# =====================================================

@router.patch("/{order_id}/payment")
def update_payment_status(

    order_id: int,

    data: schemas.PaymentUpdate,

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

    order.payment_status = (
        data.payment_status
    )

    if data.payment_details:
        order.payment_details = data.payment_details

    timeline_note = f"Payment status set to {data.payment_status}"
    if data.payment_details:
        timeline_note += f" ({data.payment_details})"

    timeline = models.OrderTimeline(

            order_id=order.id,

            status="PAYMENT_UPDATED",

            updated_by="SYSTEM",

            note=timeline_note
        )

    db.add(timeline)

    db.commit()

    return {
        "message":
            "Payment updated"
    }

# =====================================================
# RE-DISPATCH ORDER
# =====================================================

@router.patch("/{order_id}/redispatch")
def redispatch_order(
    order_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(require_role("admin"))
):
    order = db.query(models.Order).filter(models.Order.id == order_id).first()
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
    
    if order.status not in ["FAILED", "RETURNED", "CUSTOMER_UNAVAILABLE"]:
        raise HTTPException(status_code=400, detail="Only failed or returned orders can be re-dispatched")

    # Validate stock and deduct inventory again
    for item in order.items:
        inventory_item = db.query(models.Inventory).filter(
            models.Inventory.item_name == item.item_name
        ).first()
        if not inventory_item or inventory_item.quantity < item.quantity:
            raise HTTPException(
                status_code=400,
                detail=f"Insufficient stock to re-dispatch {item.item_name} ({inventory_item.quantity if inventory_item else 0} available)"
            )
        
        inventory_item.quantity -= item.quantity
        
        inv_log = models.InventoryLog(
            inventory_id=inventory_item.id,
            action="REDISPATCH_USED",
            quantity=item.quantity,
            reference_order=order.id
        )
        db.add(inv_log)

    order.status = "PENDING"
    order.driver_id = None
    order.assigned_at = None
    order.delivered_at = None
    order.cancelled_at = None

    timeline = models.OrderTimeline(
        order_id=order.id,
        status="PENDING",
        updated_by=current_user.name,
        note="Order re-dispatched by admin"
    )
    db.add(timeline)
    
    db.commit()
    return {"message": "Order re-dispatched successfully"}