from pymongo import MongoClient, UpdateOne, DeleteOne, InsertOne

from responses import error_response, success_response
from item_cache import ItemCache
from config import MONGODB_URL, DEFAULT_GET_ITEMS_QUERY_LIMIT


# retrieves items corresponding to the given item ids using the given collection and the given cache.
# if no item ids are given, it pulls all entries from the collection using the given skip and limit values
def get_items(item_ids, collection, cache, skip, limit):
    try:
        if not item_ids:
            # get all items from collection using given skip and limit values
            # don't use cache here since results should be determined by order of items in database
            items = list(collection.find({}, {"_id": 0}).skip(skip).limit(limit))
            cache.add_or_update_items(items)
        else:
            # check if desired items are in the cache
            cached_items, non_cached_item_ids = cache.get_items(item_ids)
            non_cached_items = []
            if non_cached_item_ids:
                # get items not in cache from database and add them to cache
                non_cached_items = list(
                    collection.find({"_id": {"$in": non_cached_item_ids}}, {"_id": 0})
                )
                cache.add_or_update_items(non_cached_items)
            items = cached_items + non_cached_items

        return {"items": items}
    except Exception as e:
        return error_response(
            f"Exception occurred while retrieving items: {str(e)}", 500
        )


# takes the given items and creates them in the given collection if they don't exist or updates
# them if they do exist. the given cache is updated as well
def create_or_update_items(items, collection, cache):
    bulk_upsert_array = [
        UpdateOne({"_id": item["id"]}, {"$set": item}, upsert=True) for item in items
    ]
    try:
        # add/update items in database
        result = collection.bulk_write(bulk_upsert_array, ordered=False)
        item_ids = [item["id"] for item in items]
        # get the full created/updated items from database and add them to cache
        latest_items = list(collection.find({"_id": {"$in": item_ids}}, {"_id": 0}))
        cache.add_or_update_items(latest_items)
        return success_response(str(result.bulk_api_result))
    except Exception as e:
        # check if error is due to validation failure (e.g. missing fields when creating item)
        if "Document failed validation" in str(e):
            return error_response(f"Validation error occurred: {str(e)}")
        return error_response(
            f"Exception occurred while creating/updating items: {str(e)}", 500
        )


# client used for interacting with MongoDB database to create, read, update, delete, and undelete items
class InventoryMongoClient:
    def __init__(self):
        self.client = MongoClient(MONGODB_URL)
        self.item_cache = ItemCache()
        self.deleted_item_cache = ItemCache()

    def get_items(self, item_ids, skip=0, limit=DEFAULT_GET_ITEMS_QUERY_LIMIT):
        collection = self.client.inventory.items
        cache = self.item_cache
        return get_items(item_ids, collection, cache, skip, limit)

    def create_or_update_items(self, items):
        collection = self.client.inventory.items
        cache = self.item_cache
        return create_or_update_items(items, collection, cache)

    def delete_items(self, items, recover):
        collection = self.client.inventory.items
        print(items)
        id_comment_dict = {item["id"]: item["comment"] for item in items}
        item_ids = id_comment_dict.keys()
        print(item_ids)
        try:
            # does user want to be able to recover deleted items?
            if recover:
                # create and add entries to "deleted item" collection containing items being deleted
                deleted_items = []
                for item in self.get_items(item_ids)["items"]:
                    item_id = item["id"]
                    deleted_items.append(
                        {
                            "id": item_id,
                            "deletion_comment": id_comment_dict[item_id],
                            "item": item,
                        }
                    )
                if deleted_items:
                    self.create_or_update_deleted_items(deleted_items)

            # remove entries from item cache
            self.item_cache.delete_items(item_ids)
            # remove items from item collection
            bulk_delete_array = [DeleteOne({"_id": item_id}) for item_id in item_ids]
            result = collection.bulk_write(bulk_delete_array, ordered=False)
            return success_response(str(result.bulk_api_result))
        except Exception as e:
            return error_response(
                f"Exception occurred while deleting items: {str(e)}", 500
            )

    def get_deleted_items(self, item_ids, skip=0, limit=DEFAULT_GET_ITEMS_QUERY_LIMIT):
        collection = self.client.inventory.deleted_items
        cache = self.deleted_item_cache
        return get_items(item_ids, collection, cache, skip, limit)

    def create_or_update_deleted_items(self, items):
        collection = self.client.inventory.deleted_items
        cache = self.deleted_item_cache
        return create_or_update_items(items, collection, cache)

    def undelete_items(self, item_ids):
        collection = self.client.inventory.deleted_items
        try:
            # add undeleted items to item collection
            undeleted_items = [
                deleted_item["item"]
                for deleted_item in self.get_deleted_items(item_ids)["items"]
            ]
            if undeleted_items:
                self.create_or_update_items(undeleted_items)
            # remove entries from deleted items cache
            self.deleted_item_cache.delete_items(item_ids)
            # remove deleted items from "deleted item" collection
            bulk_undelete_array = [DeleteOne({"_id": item_id}) for item_id in item_ids]
            result = collection.bulk_write(bulk_undelete_array, ordered=False)
            return success_response(str(result.bulk_api_result))
        except Exception as e:
            return error_response(
                f"Exception occurred while undeleting items: {str(e)}", 500
            )
