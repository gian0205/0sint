from app.ratelimit import RateLimiter, TokenBucket


def test_bucket_allows_up_to_capacity():
    bucket = TokenBucket(capacity=3, rate=1)
    assert bucket.take()[0] is True
    assert bucket.take()[0] is True
    assert bucket.take()[0] is True
    allowed, retry = bucket.take()
    assert allowed is False
    assert retry > 0


def test_separate_operators_have_independent_buckets():
    rl = RateLimiter(per_minute=2)
    assert rl.check("alice")[0] is True
    assert rl.check("alice")[0] is True
    assert rl.check("alice")[0] is False  # alice exhausted
    assert rl.check("bob")[0] is True  # bob untouched


def test_reset_clears_buckets():
    rl = RateLimiter(per_minute=1)
    rl.check("alice")
    assert rl.check("alice")[0] is False
    rl.reset()
    assert rl.check("alice")[0] is True
