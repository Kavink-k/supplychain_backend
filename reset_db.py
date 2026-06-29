import models
from database import engine, SessionLocal
from routers.auth import hash_password

def reset_and_seed():
    print("Dropping all tables...")
    models.Base.metadata.drop_all(bind=engine)
    
    print("Creating all tables with updated schema...")
    models.Base.metadata.create_all(bind=engine)
    
    db = SessionLocal()
    try:
        print("Seeding users...")
        # Admin
        admin = models.User(
            name="System Administrator",
            email="admin@smartops.com",
            password=hash_password("adminpassword"),
            role="admin",
            availability="AVAILABLE"
        )
        db.add(admin)
        
        # Warehouse manager
        warehouse = models.User(
            name="Warehouse Manager",
            email="warehouse@smartops.com",
            password=hash_password("warehousepassword"),
            role="warehouse",
            availability="AVAILABLE"
        )
        db.add(warehouse)
        
        # Drivers
        driver1 = models.User(
            name="John Doe",
            email="driver1@smartops.com",
            password=hash_password("driverpassword"),
            role="driver",
            availability="AVAILABLE",
            max_capacity=3,
            delivery_zone="Zone A"
        )
        driver2 = models.User(
            name="Alice Smith",
            email="driver2@smartops.com",
            password=hash_password("driverpassword"),
            role="driver",
            availability="AVAILABLE",
            max_capacity=5,
            delivery_zone="Zone B"
        )
        db.add(driver1)
        db.add(driver2)
        
        print("Seeding inventory items...")
        items = [
            models.Inventory(item_name="Premium Laptop", quantity=50, reserved_stock=0),
            models.Inventory(item_name="Wireless Headphoness", quantity=120, reserved_stock=0),
            models.Inventory(item_name="Mechanical Keyboard", quantity=80, reserved_stock=0),
            models.Inventory(item_name="Ergonomic Mouse", quantity=150, reserved_stock=0),
            models.Inventory(item_name="Smart Watch Ultra", quantity=35, reserved_stock=0)
        ]
        for item in items:
            db.add(item)
            
        db.commit()
        print("Database reset and seeded successfully!")
    except Exception as e:
        db.rollback()
        print(f"Error seeding database: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    reset_and_seed()
