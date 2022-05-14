from collections import OrderedDict
from config import DEFAULT_CACHE_SIZE


# implementation of LRU (Least Recently Used) cache used to store items
class ItemCache:
    def __init__(self, size=DEFAULT_CACHE_SIZE):
        self.cache = OrderedDict()
        self.size = size

    # add or update items within the cache
    def add_or_update_items(self, items):
        # limit items list to maximum cache size
        items = items[self.size * -1 :]
        for item in items:
            if item["id"] in self.cache:
                # update item entry in cache and mark it as most recently used
                self.cache[item["id"]].update(item)
                self.cache.move_to_end(item["id"])
            else:
                # add item to cache
                self.cache[item["id"]] = item
                # if size exceeded, remove least recently used item
                if len(self.cache) > self.size:
                    self.cache.popitem(last=False)

    # delete items from the cache
    def delete_items(self, item_ids):
        for item_id in item_ids:
            self.cache.pop(item_id, None)

    # for a given list of item ids, returns the corresponding items that are in the cache
    # and the ids of items not in the cache
    def get_items(self, item_ids):
        cached_items = []
        non_cached_item_ids = []
        for item_id in item_ids:
            if item_id in self.cache:
                print("cache triggered")
                cached_items.append(self.cache[item_id])
                # mark cache entry as most recently used
                self.cache.move_to_end(item_id)
            else:
                non_cached_item_ids.append(item_id)
        return cached_items, non_cached_item_ids
