from sqlalchemy import Column, Integer, String, ForeignKey
from database import Base
from sqlalchemy.orm import relationship 
from sqlalchemy import DateTime
from datetime import datetime

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True)
    name = Column(String(50))
    email = Column(String(50))
    password = Column(String(100))
    role = Column(String(20))


class Order(Base):
    __tablename__ = "orders"

    id = Column(Integer, primary_key=True)
    customer_name = Column(String(50))
    phone = Column(String(20))
    address = Column(String(200))
    status = Column(String(50))
    driver_id = Column(Integer, nullable=True)
    priority = Column(String(10))
    items = relationship("OrderItem", backref="order")
    created_at = Column(DateTime, default=datetime.utcnow)
    
class OrderItem(Base):
    __tablename__ = "order_items"

    id = Column(Integer, primary_key=True)
    order_id = Column(Integer, ForeignKey("orders.id"))
    item_name = Column(String(50))
    quantity = Column(Integer)
    
class Inventory(Base):
    __tablename__ = "inventory"

    id = Column(Integer, primary_key=True)
    item_name = Column(String(50))
    quantity = Column(Integer)