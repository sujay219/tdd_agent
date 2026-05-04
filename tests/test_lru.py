# test_lru_cache.py

import pytest

# initialize class LRUCache(capacity: int)

def test_basic_put_get(LRUCache):
    cache = LRUCache(2)
    cache.put(1, 1)
    cache.put(2, 2)
    assert cache.get(1) == 1

def test_eviction_order(LRUCache):
    cache = LRUCache(2)
    cache.put(1, 1)
    cache.put(2, 2)
    cache.get(1)        # 1 becomes most recent
    cache.put(3, 3)     # evicts key 2
    assert cache.get(2) == -1
    assert cache.get(1) == 1
    assert cache.get(3) == 3

def test_update_existing_key(LRUCache):
    cache = LRUCache(2)
    cache.put(1, 1)
    cache.put(1, 10)
    assert cache.get(1) == 10

def test_recent_use_updates_order(LRUCache):
    cache = LRUCache(2)
    cache.put(1, 1)
    cache.put(2, 2)
    cache.get(1)
    cache.put(3, 3)  # should evict 2
    assert cache.get(2) == -1

def test_capacity_one(LRUCache):
    cache = LRUCache(1)
    cache.put(1, 1)
    cache.put(2, 2)
    assert cache.get(1) == -1
    assert cache.get(2) == 2

def test_get_nonexistent(LRUCache):
    cache = LRUCache(2)
    assert cache.get(99) == -1

def test_overwrite_does_not_increase_size(LRUCache):
    cache = LRUCache(2)
    cache.put(1, 1)
    cache.put(2, 2)
    cache.put(1, 10)  # update key 1, making it most recent
    cache.put(3, 3)  # should evict key 2, not 1
    assert cache.get(1) == 10
    assert cache.get(2) == -1

def test_sequence_operations(LRUCache):
    cache = LRUCache(2)
    cache.put(2, 1)
    cache.put(1, 1)
    cache.put(2, 3)
    cache.put(4, 1)
    assert cache.get(1) == -1
    assert cache.get(2) == 3

def test_large_number_of_operations(LRUCache):
    cache = LRUCache(3)
    for i in range(10):
        cache.put(i, i*i)
    # only last 3 should remain
    assert cache.get(7) == 49
    assert cache.get(8) == 64
    assert cache.get(9) == 81