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
            User.get(user_id)
        except Exception as e:
            raise ValueError("User specified does not exist")

        all_collections = self.get_collections_for_user(user_id)
        if len(all_collections) > 15:
            raise Exception("You can only have a maximum of 15 collections")
        
        collection = Collection(
            user_id=user_id,
            date_added=datetime.now(timezone.utc),
            name=document.get("name"),
            icon=icon,
            archived=False
        )
        db.session.add(collection)
        db.session.commit()
        return collection

    def archive_collection(self, collection_id: int) -> Collection:
        """Archives a collection by ID.
        """

        collection = Collection.get(collection_id)
        collection.archived = True
        db.session.commit()
        return collection

    def get_collection(self, collection_id: int) -> Collection:
        """Returns a single collection by ID.
        """
        return Collection.get(collection_id)

    def get_collections_for_user(self, user_id: int) -> List[Collection]:
        """Returns all non-archived collections for the user
        specified.
        """

        all_collections = Collection.query.filter_by(
            user_id=user_id, archived=False
        ).all()
        return all_collections
    
