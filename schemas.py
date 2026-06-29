# from pydantic import BaseModel
# from typing import List


# class OrderItemResponse(BaseModel):
#     item_name: str
#     quantity: int

#     class Config:
#         from_attributes = True


# class OrderResponse(BaseModel):
#     id: int
#     customer_name: str
#     phone: str
#     address: str
#     status: str
#     driver_id: int | None
#     priority: str
#     is_delayed: bool
#     items: list[OrderItemResponse]

#     class Config:
#         from_attributes = True


# class OrderItemCreate(BaseModel):
#     item_name: str
#     quantity: int


# class OrderCreate(BaseModel):
#     customer_name: str
#     phone: str
#     address: str
#     items: list[OrderItemCreate]


# class UpdateStatus(BaseModel):
#     status: str


# class AssignDriver(BaseModel):
#     driver_id: int


# class UserCreate(BaseModel):
#     name: str
#     email: str
#     password: str
#     role: str


# class LoginSchema(BaseModel):
#     email: str
#     password: str
    
# class InventoryCreate(BaseModel):
#     item_name: str
#     quantity: int


# class InventoryResponse(BaseModel):
#     id: int
#     item_name: str
#     quantity: int

#     class Config:
#         from_attributes = True



from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime


# =====================================================
# ORDER ITEMS
# =====================================================

class OrderItemCreate(BaseModel):

    item_name: str

    quantity: int

    price: Optional[int] = 0


class OrderItemResponse(BaseModel):

    item_name: str

    quantity: int

    price: int

    subtotal: int

    class Config:
        from_attributes = True


# =====================================================
# ORDER TIMELINE
# =====================================================

class TimelineResponse(BaseModel):

    status: str

    updated_by: str

    note: Optional[str]

    timestamp: datetime

    class Config:
        from_attributes = True


# =====================================================
# CUSTOMER
# =====================================================

class CustomerResponse(BaseModel):

    id: int

    name: str

    phone: str

    address: str

    class Config:
        from_attributes = True


# =====================================================
# DRIVER RESPONSE
# =====================================================

class DriverResponse(BaseModel):

    id: int

    name: str

    availability: str

    active_deliveries: int

    max_capacity: int

    delivery_zone: Optional[str]

    class Config:
        from_attributes = True


# =====================================================
# ORDER CREATE
# =====================================================

class OrderCreate(BaseModel):

    customer_name: str

    phone: str

    address: str

    payment_method: Optional[str] = "COD"

    delivery_fee: Optional[int] = 0

    latitude: Optional[float] = None

    longitude: Optional[float] = None

    items: List[OrderItemCreate]


# =====================================================
# ORDER RESPONSE
# =====================================================

class OrderResponse(BaseModel):

    id: int

    customer_name: str

    phone: str

    address: str

    status: str

    priority: str

    is_delayed: bool

    payment_method: str

    payment_status: str

    payment_details: Optional[str] = None

    total_amount: int

    delivery_fee: int

    invoice_number: Optional[str]

    created_at: datetime

    assigned_at: Optional[datetime]

    delivered_at: Optional[datetime]

    estimated_delivery: Optional[datetime]

    driver_id: Optional[int]

    latitude: Optional[float] = None

    longitude: Optional[float] = None

    items: List[OrderItemResponse]

    timeline: List[TimelineResponse]

    class Config:
        from_attributes = True


# =====================================================
# UPDATE STATUS
# =====================================================

class UpdateStatus(BaseModel):

    status: str

    note: Optional[str] = None


# =====================================================
# DRIVER ASSIGNMENT
# =====================================================

class AssignDriver(BaseModel):

    driver_id: int


# =====================================================
# PAYMENT UPDATE
# =====================================================

class PaymentUpdate(BaseModel):

    payment_status: str

    payment_details: Optional[str] = None


# =====================================================
# USER CREATE
# =====================================================

class UserCreate(BaseModel):

    name: str

    email: str

    password: str

    role: str


# =====================================================
# LOGIN
# =====================================================

class LoginSchema(BaseModel):

    email: str

    password: str


# =====================================================
# INVENTORY
# =====================================================

class InventoryCreate(BaseModel):

    item_name: str

    quantity: int


class InventoryResponse(BaseModel):

    id: int

    item_name: str

    quantity: int

    reserved_stock: int

    class Config:
        from_attributes = True


# =====================================================
# INVENTORY LOGS
# =====================================================

class InventoryLogResponse(BaseModel):

    action: str

    quantity: int

    reference_order: Optional[int]

    timestamp: datetime

    class Config:
        from_attributes = True


# =====================================================
# NOTIFICATIONS
# =====================================================

class NotificationResponse(BaseModel):

    id: int

    title: str

    message: str

    type: str

    is_read: bool

    created_at: datetime

    class Config:
        from_attributes = True
        
        
        # =====================================================
# CREATE NOTIFICATION
# =====================================================

class NotificationCreate(BaseModel):

    title: str

    message: str

    type: str