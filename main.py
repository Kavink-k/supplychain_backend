from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from database import engine
import models
from routers import auth
from routers import orders
from routers import driver
from routers import warehouese
from routers import tracking
from routers import inventory
from routers import notifications
from routers import dashboard

origins = [
    "http://localhost:3000",
    'https://smartops-127f.onrender.com' # React frontend
]
app = FastAPI()
app.add_middleware(CORSMiddleware,allow_origins=origins,allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],)


app.include_router(auth.router, prefix="/auth",tags=["Auth"])
app.include_router(orders.router, prefix="/orders", tags=["Orders"])
app.include_router(driver.router,prefix='/drivers',tags=["Driver"])
app.include_router(warehouese.router,prefix='/warehouse',tags=["Warehouse"])
app.include_router(tracking.router, prefix="/tracking", tags=["Tracking"])
app.include_router(inventory.router, prefix="/inventory", tags=["inventory"])
app.include_router(
    notifications.router,
    prefix="/notifications",
    tags=["Notifications"]
)
app.include_router(
    dashboard.router,
    prefix="/dashboard",
    tags=["Dashboard"]
)

models.Base.metadata.create_all(bind=engine)

@app.get('/')
def Helo():
    return "Hi"

