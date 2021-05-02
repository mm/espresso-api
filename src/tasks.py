from src import celery
from src.links.service import LinkService
from logging import Logger

logger = Logger("task_logger")


@celery.task
def populate_link_title(link_id, link_url):
    """Adds a link's title to the link object in the database,
    by reading the HTML of the website itself.
    """
    logger.info(f"Received title-less link with ID {link_id}: {link_url}")
    link_service = LinkService()
    link = link_service.get_link(link_id)
    metadata = link_service.extract_metadata_from_url(link_url)
    link_service.update_link(link, metadata)
