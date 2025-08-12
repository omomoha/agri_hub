from fastapi import APIRouter
from app.api.v1.endpoints import auth, users, farms, listings, offers, contracts, escrow, orders, kyc, health

api_router = APIRouter()

# Include all endpoint routers
api_router.include_router(auth.router, prefix="/auth", tags=["authentication"])
api_router.include_router(users.router, prefix="/users", tags=["users"])
api_router.include_router(farms.router, prefix="/farms", tags=["farms"])
api_router.include_router(listings.router, prefix="/listings", tags=["listings"])
api_router.include_router(offers.router, prefix="/offers", tags=["offers"])
api_router.include_router(contracts.router, prefix="/contracts", tags=["contracts"])
api_router.include_router(escrow.router, prefix="/escrow", tags=["escrow"])
api_router.include_router(orders.router, prefix="/orders", tags=["orders"])
api_router.include_router(kyc.router, prefix="/kyc", tags=["kyc"])
api_router.include_router(health.router, prefix="/health", tags=["health"])
