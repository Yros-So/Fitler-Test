from loguru import logger
from sqlalchemy.orm import Session

from app.db.session import SessionLocal
from app.repositories.catalog import CatalogRepository
from app.repositories.jobs import JobRepository
from app.repositories.websites import WebsiteRepository
from app.scraper.client import ShopifyScraper


class ScrapeService:
    """Cycle de vie d'un job de scraping (création / statuts)."""

    def __init__(self, session: Session) -> None:
        self.session = session
        self.websites = WebsiteRepository(session)
        self.jobs = JobRepository(session)

    def enqueue(self, url: str) -> str:
        # Enregistre la boutique (création si inconnue) puis un job "pending".
        # Le job est exécuté ensuite en arrière-plan (BackgroundTasks).
        website = self.websites.get_or_create(url)
        job = self.jobs.create(website)
        self.session.commit()
        return job.id


def run_scrape_job(job_id: str) -> None:
    """Exécution asynchrone : scraping + écriture en base + suivi du statut."""
    # Session dédiée au job en arrière-plan (hors cycle requête HTTP).
    session = SessionLocal()
    jobs = JobRepository(session)
    catalog = CatalogRepository(session)
    scraper = ShopifyScraper()

    try:
        job = jobs.get(job_id)
        if job is None:
            logger.error("Scrape job {} does not exist", job_id)
            return

        jobs.mark_running(job)
        session.commit()

        # 1) Extraction sur la boutique, 2) persistance du résultat,
        # 3) clôture du job avec les statistiques écrites.
        result = scraper.scrape(job.website.url)
        stats = catalog.persist_result(job.website_id, result)
        jobs.mark_completed(job, stats)
        session.commit()
        logger.info("Scrape job {} completed with {}", job_id, stats)
    except Exception as exc:
        # Toute erreur doit laisser une trace : statut "failed" + message.
        session.rollback()
        job = jobs.get(job_id)
        if job is not None:
            jobs.mark_failed(job, str(exc))
            session.commit()
        logger.exception("Scrape job {} failed", job_id)
    finally:
        session.close()
