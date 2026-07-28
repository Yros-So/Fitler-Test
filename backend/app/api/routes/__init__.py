from fastapi import APIRouter

from app.api.routes import exports, health, products, scrape, size_guides

api_router = APIRouter()
api_router.include_router(health.router, tags=["health"])
api_router.include_router(scrape.router, tags=["scraping"])
api_router.include_router(products.router, tags=["products"])
api_router.include_router(size_guides.router, tags=["size guides"])
api_router.include_router(exports.router, tags=["exports"])
