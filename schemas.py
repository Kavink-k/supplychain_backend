from pydantic import BaseModel
from typing import List


class OrderItemResponse(BaseModel):
    item_name: str
    quantity: int

    class Config:
        from_attributes = True


class OrderResponse(BaseModel):
    id: int
    customer_name: str
    phone: str
    address: str
    status: str
    driver_id: int | None
    priority: str
    is_delayed: bool
    items: list[OrderItemResponse]

    class Config:
        from_attributes = True


class OrderItemCreate(BaseModel):
    item_name: str
    quantity: int


class OrderCreate(BaseModel):
    customer_name: str
    phone: str
    address: str
    items: list[OrderItemCreate]


class UpdateStatus(BaseModel):
    status: str


class AssignDriver(BaseModel):
    driver_id: int


class UserCreate(BaseModel):
    name: str
    email: str
    password: str
    role: str


class LoginSchema(BaseModel):
    email: str
    password: str
    
class InventoryCreate(BaseModel):
    item_name: str
    quantity: int


class InventoryResponse(BaseModel):
    id: int
    item_name: str
    quantity: int

    class Config:
        from_attributes = True