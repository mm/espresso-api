from tests.factories import UserFactory, CollectionFactory
from src.collections.service import CollectionService


def test_create_collection(scoped_app):
    user = UserFactory()
    document = {"name": "Test", "icon": ":hello:"}

    collection = CollectionService().create_collection(user.id, document)

    assert collection.user_id == user.id
    assert collection.order == 0
    assert collection.id is not None


def test_create_multiple_collections_order(scoped_app):
    user = UserFactory()
    collection_service = CollectionService()
    collection1 = collection_service.create_collection(user.id, {"name": "Test 1"})
    collection2 = collection_service.create_collection(user.id, {"name": "Test 2"})

    assert collection2.order == collection1.order + 1


def test_reset_collection_order(scoped_app):
    user = UserFactory()
    collections = CollectionFactory.create_batch(5, user=user)

    collection_to_delete = collections[3].id
    collection_orders = [collection.order for collection in collections]

    # Are the collections in increasing order to begin with?
    assert all(
        later == earlier + 1
        for later, earlier in zip(collection_orders[1:], collection_orders)
    )

    CollectionService().archive_collection(collection_to_delete)

    # Are they still in order after an archive, with no gaps in between order numbers?
    all_collections = CollectionService().get_collections_for_user(user.id)
    collection_orders = [collection.order for collection in all_collections]
    assert all(
        later == earlier + 1
        for later, earlier in zip(collection_orders[1:], collection_orders)
    )
