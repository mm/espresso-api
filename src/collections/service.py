from src.model import Collection, CollectionSchema, User, db
from datetime import datetime, timezone
from typing import List


class CollectionService:
    def create_collection(self, user_id: int, document: dict) -> Collection:
        """Creates a new collection, and returns it.

        Args:
            user_id: The user to create this collection under
            document: Dict representing the name and icon for the collection
        """

        # Icons are CLDR short names for emojis. Full list at:
        # https://unicode.org/emoji/charts/emoji-list.html
        icon = document.get("icon", ":thought balloon:")

        try:
            User.query.get(user_id)
        except Exception as e:
            raise ValueError("User specified does not exist")

        all_collections = self.get_collections_for_user(user_id)
        if len(all_collections) > 15:
            raise Exception("You can only have a maximum of 15 collections")

        # Collections can be ordered on the UI. This calculates what the
        # next order value should be (first collection = 0)
        order = 0
        if len(all_collections) > 0:
            current_max_order = all_collections[-1].order
            order = current_max_order + 1

        collection = Collection(
            user_id=user_id,
            date_added=datetime.now(timezone.utc),
            name=document.get("name"),
            icon=icon,
            archived=False,
            order=order,
        )
        db.session.add(collection)
        db.session.commit()
        return collection

    def archive_collection(self, collection_id: int) -> Collection:
        """Archives a collection by ID."""

        collection = Collection.query.get(collection_id)
        collection.archived = True
        db.session.commit()
        return collection

    def get_collection(self, collection_id: int, user_id: int) -> Collection:
        """Returns a single collection by ID."""
        return Collection.query.filter_by(
            id=collection_id, archived=False, user_id=user_id
        ).first()

    def get_collections_for_user(self, user_id: int) -> List[Collection]:
        """Returns all non-archived collections for the user
        specified.
        """

        all_collections = (
            Collection.query.filter_by(user_id=user_id, archived=False)
            .order_by(Collection.order.asc())
            .all()
        )
        return all_collections

    def bulk_update_collection_orders(
        self, document: dict[int, int]
    ) -> List[Collection]:
        """Updates the order of all collections at once. Can be helpful
        when updating the order collections appear in on the UI.

        Args:
            document: A document describing the updates to be made. Dict keys
                should be collection IDs, and values should be the new order values.
        """

        # TODO: Need lots of checks to make sure orders actually exist and
        # will be sequential
        for collection_update in document.items():
            collection_id, new_order = collection_update
            collection = Collection.query.get(collection_id)
            collection.order = new_order

        db.session.commit()
