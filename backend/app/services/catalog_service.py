from sqlalchemy.orm import Session

from app.repositories.catalog import CatalogRepository


class CatalogService:
    """Façade d'accès au catalogue : délègue les requêtes au repository."""

    def __init__(self, session: Session) -> None:
        self.repository = CatalogRepository(session)

    def list_products(self, search: str | None, page: int, page_size: int, sort: str):
        return self.repository.list_products(
            search=search,
            page=page,
            page_size=page_size,
            sort=sort,
        )

    def get_product(self, product_id: str):
        return self.repository.get_product(product_id)

    def list_size_guides(self, page: int, page_size: int):
        return self.repository.list_size_guides(page=page, page_size=page_size)
