import time

from app.cache import TTLCache, make_key


def test_set_and_get():
    cache = TTLCache(max_entries=10, ttl_seconds=60)
    cache.set("k", {"v": 1})
    assert cache.get("k") == {"v": 1}


def test_expired_entry_returns_none():
    cache = TTLCache(max_entries=10, ttl_seconds=0)
    cache.set("k", "v")
    time.sleep(0.01)
    assert cache.get("k") is None


def test_lru_evicts_oldest():
    cache = TTLCache(max_entries=2, ttl_seconds=60)
    cache.set("a", 1)
    cache.set("b", 2)
    cache.set("c", 3)
    assert cache.get("a") is None
    assert cache.get("b") == 2
    assert cache.get("c") == 3


def test_make_key_is_order_independent_for_sources():
    assert make_key("11144477735", ["validator", "trt3"]) == make_key(
        "11144477735", ["trt3", "validator"]
    )


def test_make_key_differs_for_all_sources_vs_subset():
    assert make_key("11144477735", None) != make_key("11144477735", ["validator"])
