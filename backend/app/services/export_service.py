from sqlalchemy.orm import Session, selectinload
from sqlalchemy import select

from app.exporters import products_to_csv, products_to_json, products_to_xlsx
from app.models.product import Product


class ExportService:
    def __init__(self, session: Session) -> None:
        self.session = session

    def build(self, export_format: str) -> tuple[bytes, str, str]:
        products = list(
            self.session.scalars(
                select(Product)
                .options(selectinload(Product.variants))
                .order_by(Product.name)
            )
        )
        if export_format == "csv":
            return products_to_csv(products), "text/csv", "products.csv"
        if export_format == "xlsx":
            return (
                products_to_xlsx(products),
                "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                "products.xlsx",
            )
        return products_to_json(products), "application/json", "products.json"
