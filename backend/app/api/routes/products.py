from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.db.session import get_session
from app.schemas.product import ProductListResponse, ProductRead
from app.services.catalog_service import CatalogService

router = APIRouter()


@router.get("/products", response_model=ProductListResponse)
def list_products(
    search: str | None = None,
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=25, ge=1, le=100),
    sort: str = Query(default="name", pattern="^(name|price|created_at)$"),
    session: Session = Depends(get_session),
) -> ProductListResponse:
    # Catalogue paginé, recherchable et triable (le tri est contraint par
    # une regex pour ne jamais injecter de colonne arbitraire en SQL).
    items, total = CatalogService(session).list_products(search, page, page_size, sort)
    return ProductListResponse(items=items, total=total, page=page, page_size=page_size)


@router.get("/products/{product_id}", response_model=ProductRead)
def get_product(product_id: str, session: Session = Depends(get_session)) -> ProductRead:
    # Fiche détaillée d'un produit (variantes + guides associés).
    product = CatalogService(session).get_product(product_id)
    if product is None:
        raise HTTPException(status_code=404, detail="Product not found")
    return product
