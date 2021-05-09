from src import celery
from src.links.service import LinkService
from logging import Logger

logger = Logger("task_logger")


@celery.task
def populate_link_metadata(link_id, link_url):
    """Adds title and description data to a link."""
    logger.info(f"Received title-less link with ID {link_id}: {link_url}")
    link_service = LinkService()
    link = link_service.get_link(link_id)
    metadata = link_service.extract_metadata_from_url(link_url)
    link_service.update_link(link, metadata)
