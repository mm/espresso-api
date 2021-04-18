from src.signals import link_created
from src.tasks import populate_link_title


def link_created_receive(sender, **kwargs):
    link_id = kwargs["link_id"]
    link_url = kwargs["link_url"]
    link_title = kwargs["link_title"]
    if not link_title:
        populate_link_title.delay(link_id, link_url)


# Subscribe to signals:
link_created.connect(link_created_receive)
