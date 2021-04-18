from src.signals import link_created
from .service import LinkService

def link_created_receive(sender, **kwargs):
    link_service = LinkService()
    link = link_service.get_link(kwargs['link_id'])

    if not link.title:
        title = link_service.extract_title_from_url(link.url)
        link_service.update_link(link, {'title': title})


# Subscribe to signals:
link_created.connect(link_created_receive)