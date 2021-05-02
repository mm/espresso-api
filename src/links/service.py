"""Middleware between an endpoint defined in the blueprint,
and the database itself for links. Handles data CRUD operations.
"""

from src.model import User, Link, db, DISALLOWED_UPDATE_FIELDS
from src.signals import link_created
from parsel import Selector
from typing import Union
import requests


class LinkService:
    def get_link(self, link_id: int) -> Link:
        """Attempts to retrieve a link at a given ID. Raises a 404
        error if not found
        """
        link = Link.query.get_or_404(link_id)
        return link

    def get_many_links(self, user_id: int, params: dict) -> dict:
        """Retrieves a collection of links added by the user, and handles
        pagination (pagination params given by params dict). Returns links
        within pagination window, and pagination information for the current
        request.
        """

        page, per_page, show = params["page"], params["per_page"], params["show"]

        link_query = Link.query.filter(Link.user_id == user_id)
        if show == "read":
            link_query = link_query.filter(Link.read == True)
        elif show == "unread":
            link_query = link_query.filter(Link.read == False)

        # Paginate results:
        link_query = link_query.order_by(Link.date_added.desc()).paginate(
            page=page, per_page=per_page
        )

        total_links = len(User.query.get(user_id).links)

        return {
            "total_links": total_links,
            "page": link_query.page,
            "total_pages": link_query.pages,
            "next_page": link_query.next_num,
            "per_page": per_page,
            "links": link_query.items,
        }

    def create_link(self, link: Link) -> Link:
        """Creates a new link in the database. Accepts a pending
        Link instance and returns a persisted one to serialize to JSON
        later using Marshmallow.
        """

        db.session.add(link)
        db.session.commit()

        link_created.send(
            self, **{"link_id": link.id, "link_url": link.url, "link_title": link.title}
        )

        return link

    def update_link(self, link: Link, changes: dict) -> None:
        """Updates a link given a set of changes in a dict."""
        print(f'Incoming changes: {changes}')
        change_counter = 0
        for key, value in changes.items():
            if hasattr(link, key) and getattr(link, key) != value:
                if key not in DISALLOWED_UPDATE_FIELDS:
                    # Make a change to the Link object stored in the database
                    # if the values actually differ (and are allowed)
                    setattr(link, key, value)
                    change_counter += 1
        # If we've made any changes, commit them:
        if change_counter > 0:
            db.session.commit()

    def delete_link(self, link: Link) -> None:
        """Deletes a given Link instance."""

        try:
            db.session.delete(link)
            db.session.commit()
        except Exception as e:
            print(f"Delete exception: {e}")
            raise

    @staticmethod
    def extract_metadata_from_url(url: str) -> Union[dict, None]:
        """Attempts to extract information about a website given a URL.

        Args:
            url: The URL to check.

        Returns:
            A dict with:
            - title: Title extracted from <title> element on site
            - description: Description extracted from og:description on site
        """
        if url:
            html_text = requests.get(url).text
            selector = Selector(text=html_text)
            title = selector.xpath("//title/text()").get()
            description = selector.xpath('//meta[@property="og:description"]/@content').get()
            if not description:
                description = selector.xpath('//meta[@name="description"]/@content').get()
            return {
                'title': title.strip() if title else None,
                'description': description.strip() if description else None
            }
        return None
