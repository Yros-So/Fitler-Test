from fastapi import APIRouter, Depends
from fastapi.responses import Response
from sqlalchemy.orm import Session

from app.db.session import get_session
from app.services.export_service import ExportService

router = APIRouter()


@router.get("/export/json")
def export_json(session: Session = Depends(get_session)) -> Response:
    payload, media_type, filename = ExportService(session).build("json")
    return _download(payload, media_type, filename)


@router.get("/export/csv")
def export_csv(session: Session = Depends(get_session)) -> Response:
    payload, media_type, filename = ExportService(session).build("csv")
    return _download(payload, media_type, filename)


@router.get("/export/xlsx")
def export_xlsx(session: Session = Depends(get_session)) -> Response:
    payload, media_type, filename = ExportService(session).build("xlsx")
    return _download(payload, media_type, filename)


def _download(payload: bytes, media_type: str, filename: str) -> Response:
    # Réponse de téléchargement : le header Content-Disposition force le
    # navigateur à enregistrer le fichier plutôt qu'à l'afficher.
    return Response(
        payload,
        media_type=media_type,
        headers={"Content-Disposition": f'attachment; filename="{filename}"'},
    )
