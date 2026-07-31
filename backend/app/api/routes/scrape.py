from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException
from sqlalchemy.orm import Session

from app.db.session import get_session
from app.repositories.jobs import JobRepository
from app.schemas.scrape import ScrapeJobQueued, ScrapeJobRead, ScrapeRequest
from app.services.scrape_service import ScrapeService, run_scrape_job

router = APIRouter()


@router.post("/scrape", response_model=ScrapeJobQueued, status_code=202)
def create_scrape_job(
    payload: ScrapeRequest,
    background_tasks: BackgroundTasks,
    session: Session = Depends(get_session),
) -> ScrapeJobQueued:
    # 202 Accepted : le job est créé, l'exécution se fait en arrière-plan
    # (BackgroundTasks de FastAPI) pour ne pas bloquer la requête HTTP.
    job_id = ScrapeService(session).enqueue(str(payload.url))
    background_tasks.add_task(run_scrape_job, job_id)
    return ScrapeJobQueued(job_id=job_id)


@router.get("/jobs/latest", response_model=ScrapeJobRead | None)
def get_latest_scrape_job(session: Session = Depends(get_session)) -> ScrapeJobRead | None:
    # Dernier job : utilisé par le dashboard pour afficher l'état du run.
    return JobRepository(session).latest()


@router.get("/jobs/{job_id}", response_model=ScrapeJobRead)
def get_scrape_job(job_id: str, session: Session = Depends(get_session)) -> ScrapeJobRead:
    # Consultation du statut d'un job : le frontend "poll" cet endpoint.
    job = JobRepository(session).get(job_id)
    if job is None:
        raise HTTPException(status_code=404, detail="Scrape job not found")
    return job
