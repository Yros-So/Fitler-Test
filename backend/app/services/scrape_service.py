from loguru import logger
from sqlalchemy.orm import Session

from app.db.session import SessionLocal
from app.repositories.catalog import CatalogRepository
from app.repositories.jobs import JobRepository
from app.repositories.websites import WebsiteRepository
from app.scraper.client import ShopifyScraper


class ScrapeService:
    def __init__(self, session: Session) -> None:
        self.session = session
        self.websites = WebsiteRepository(session)
        self.jobs = JobRepository(session)

    def enqueue(self, url: str) -> str:
        website = self.websites.get_or_create(url)
        job = self.jobs.create(website)
        self.session.commit()
        return job.id


def run_scrape_job(job_id: str) -> None:
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

        result = scraper.scrape(job.website.url)
        stats = catalog.persist_result(job.website_id, result)
        jobs.mark_completed(job, stats)
        session.commit()
        logger.info("Scrape job {} completed with {}", job_id, stats)
    except Exception as exc:
        session.rollback()
        job = jobs.get(job_id)
        if job is not None:
            jobs.mark_failed(job, str(exc))
            session.commit()
        logger.exception("Scrape job {} failed", job_id)
    finally:
        session.close()
