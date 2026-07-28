from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.db.session import get_session
from app.schemas.size_guide import SizeGuideListResponse
from app.services.catalog_service import CatalogService

router = APIRouter()


@router.get("/size-guides", response_model=SizeGuideListResponse)
def list_size_guides(
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=25, ge=1, le=100),
    session: Session = Depends(get_session),
) -> SizeGuideListResponse:
    items, total = CatalogService(session).list_size_guides(page, page_size)
    return SizeGuideListResponse(items=items, total=total, page=page, page_size=page_size)
