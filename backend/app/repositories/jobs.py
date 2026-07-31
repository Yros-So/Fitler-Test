from datetime import UTC, datetime

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.scrape_job import ScrapeJob
from app.models.website import Website


class JobRepository:
    """Suivi des jobs de scraping : création et transitions de statut."""

    def __init__(self, session: Session) -> None:
        self.session = session

    def create(self, website: Website) -> ScrapeJob:
        # Nouveau job à l'état "pending", exécuté ensuite en arrière-plan.
        job = ScrapeJob(website_id=website.id, status="pending", stats={})
        self.session.add(job)
        self.session.flush()
        return job

    def get(self, job_id: str) -> ScrapeJob | None:
        return self.session.scalar(select(ScrapeJob).where(ScrapeJob.id == job_id))

    def latest(self) -> ScrapeJob | None:
        # Dernier job (dashboard) : tri par date de création décroissante.
        return self.session.scalar(
            select(ScrapeJob).order_by(ScrapeJob.created_at.desc()).limit(1)
        )

    def mark_running(self, job: ScrapeJob) -> None:
        job.status = "running"
        job.started_at = datetime.now(UTC)
        job.error = None
        self.session.flush()

    def mark_completed(self, job: ScrapeJob, stats: dict) -> None:
        job.status = "completed"
        job.finished_at = datetime.now(UTC)
        job.stats = stats
        self.session.flush()

    def mark_failed(self, job: ScrapeJob, error: str) -> None:
        # Conserve le message d'erreur pour le diagnostic dans l'UI.
        job.status = "failed"
        job.finished_at = datetime.now(UTC)
        job.error = error
        self.session.flush()
