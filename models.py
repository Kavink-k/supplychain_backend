# from sqlalchemy import Column, Integer, String, ForeignKey
# from database import Base
# from sqlalchemy.orm import relationship 
# from sqlalchemy import DateTime
# from datetime import datetime

# class User(Base):
#     __tablename__ = "users"

#     id = Column(Integer, primary_key=True)
#     name = Column(String(50))
#     email = Column(String(50))
#     password = Column(String(100))
#     role = Column(String(20))


# class Order(Base):
#     __tablename__ = "orders"

#     id = Column(Integer, primary_key=True)
#     customer_name = Column(String(50))
#     phone = Column(String(20))
#     address = Column(String(200))
#     status = Column(String(50))
#     driver_id = Column(Integer, nullable=True)
#     priority = Column(String(10))
#     items = relationship("OrderItem", backref="order")
#     created_at = Column(DateTime, default=datetime.utcnow)
    
# class OrderItem(Base):
#     __tablename__ = "order_items"

#     id = Column(Integer, primary_key=True)
#     order_id = Column(Integer, ForeignKey("orders.id"))
#     item_name = Column(String(50))
#     quantity = Column(Integer)
    
# class Inventory(Base):
#     __tablename__ = "inventory"

#     id = Column(Integer, primary_key=True)
#     item_name = Column(String(50))
#     quantity = Column(Integer)



from sqlalchemy import (
    Column,
    Integer,
    String,
    ForeignKey,
    DateTime,
    Boolean,
    Float,
)

from sqlalchemy.orm import relationship

from database import Base

from datetime import datetime


# =====================================================
# USERS
# =====================================================

class User(Base):

    __tablename__ = "users"

    id = Column(Integer, primary_key=True)

    name = Column(String(50))

    email = Column(String(50), unique=True)

    password = Column(String(100))

    role = Column(String(20))

    # NEW DRIVER FEATURES

    availability = Column(
        String(25),
        default="AVAILABLE"
    )

    active_deliveries = Column(
        Integer,
        default=0
    )

    max_capacity = Column(
        Integer,
        default=3
    )

    delivery_zone = Column(
        String(50),
        nullable=True
    )

    last_active = Column(
        DateTime,
        default=datetime.utcnow
    )

    latitude = Column(
        Float,
        nullable=True
    )

    longitude = Column(
        Float,
        nullable=True
    )


# =====================================================
# CUSTOMERS
# =====================================================

class Customer(Base):

    __tablename__ = "customers"

    id = Column(Integer, primary_key=True)

    name = Column(String(50))

    phone = Column(
        String(20),
        unique=True
    )

    address = Column(String(200))

    created_at = Column(
        DateTime,
        default=datetime.utcnow
    )

    orders = relationship(
        "Order",
        back_populates="customer"
    )


# =====================================================
# ORDERS
# =====================================================

class Order(Base):

    __tablename__ = "orders"

    id = Column(Integer, primary_key=True)

    customer_id = Column(
        Integer,
        ForeignKey("customers.id")
    )

    customer_name = Column(String(50))

    phone = Column(String(20))

    address = Column(String(200))

    status = Column(String(50))

    priority = Column(String(20))

    created_at = Column(
        DateTime,
        default=datetime.utcnow
    )

    # DRIVER RELATION

    driver_id = Column(
        Integer,
        ForeignKey("users.id"),
        nullable=True
    )

    driver = relationship("User")

    # PAYMENT SYSTEM

    payment_method = Column(
        String(20),
        default="COD"
    )

    payment_status = Column(
        String(20),
        default="PENDING"
    )

    payment_details = Column(
        String(200),
        nullable=True
    )

    total_amount = Column(
        Integer,
        default=0
    )

    delivery_fee = Column(
        Integer,
        default=0
    )

    invoice_number = Column(
        String(50),
        nullable=True
    )

    # COORDINATES FOR ROUTE OPTIMIZATION

    latitude = Column(
        Float,
        nullable=True
    )

    longitude = Column(
        Float,
        nullable=True
    )

    # DELIVERY TIMESTAMPS

    assigned_at = Column(
        DateTime,
        nullable=True
    )

    delivered_at = Column(
        DateTime,
        nullable=True
    )

    cancelled_at = Column(
        DateTime,
        nullable=True
    )

    estimated_delivery = Column(
        DateTime,
        nullable=True
    )

    delivery_notes = Column(
        String(200),
        nullable=True
    )

    is_delayed = Column(
        Boolean,
        default=False
    )

    # RELATIONSHIPS

    items = relationship(
        "OrderItem",
        back_populates="order"
    )

    customer = relationship(
        "Customer",
        back_populates="orders"
    )

    timeline = relationship(
        "OrderTimeline",
        back_populates="order"
    )

    @property
    def driver_latitude(self):
        return self.driver.latitude if self.driver else None

    @property
    def driver_longitude(self):
        return self.driver.longitude if self.driver else None


# =====================================================
# ORDER ITEMS
# =====================================================

class OrderItem(Base):

    __tablename__ = "order_items"

    id = Column(Integer, primary_key=True)

    order_id = Column(
        Integer,
        ForeignKey("orders.id")
    )

    item_name = Column(String(50))

    quantity = Column(Integer)

    # NEW PRICE SYSTEM

    price = Column(
        Integer,
        default=0
    )

    subtotal = Column(
        Integer,
        default=0
    )

    order = relationship(
        "Order",
        back_populates="items"
    )


# =====================================================
# ORDER TIMELINE
# =====================================================

class OrderTimeline(Base):

    __tablename__ = "order_timeline"

    id = Column(Integer, primary_key=True)

    order_id = Column(
        Integer,
        ForeignKey("orders.id")
    )

    status = Column(String(50))

    updated_by = Column(String(50))

    note = Column(
        String(200),
        nullable=True
    )

    timestamp = Column(
        DateTime,
        default=datetime.utcnow
    )

    order = relationship(
        "Order",
        back_populates="timeline"
    )


# =====================================================
# INVENTORY
# =====================================================

class Inventory(Base):

    __tablename__ = "inventory"

    id = Column(Integer, primary_key=True)

    item_name = Column(String(50))

    quantity = Column(Integer)

    reserved_stock = Column(
        Integer,
        default=0
    )

    logs = relationship(
        "InventoryLog",
        back_populates="inventory"
    )


# =====================================================
# INVENTORY LOGS
# =====================================================

class InventoryLog(Base):

    __tablename__ = "inventory_logs"

    id = Column(Integer, primary_key=True)

    inventory_id = Column(
        Integer,
        ForeignKey("inventory.id")
    )

    action = Column(String(50))

    quantity = Column(Integer)

    reference_order = Column(
        Integer,
        nullable=True
    )

    timestamp = Column(
        DateTime,
        default=datetime.utcnow
    )

    inventory = relationship(
        "Inventory",
        back_populates="logs"
    )


# =====================================================
# NOTIFICATIONS
# =====================================================

class Notification(Base):

    __tablename__ = "notifications"

    id = Column(Integer, primary_key=True)

    title = Column(String(100))

    message = Column(String(300))

    type = Column(String(50))

    is_read = Column(
        Boolean,
        default=False
    )

    created_at = Column(
        DateTime,
        default=datetime.utcnow
    )