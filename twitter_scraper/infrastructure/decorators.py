import functools
import logging
import time
import traceback
from threading import RLock
from types import GeneratorType
from typing import Iterator

from django.conf import settings
from django.core.cache.backends.base import DEFAULT_TIMEOUT
from memoize import Memoizer as DjangoMemoizer

from twitter_scraper.infrastructure.utils import enforce_sequence

logger = logging.getLogger(__name__)


class RateLimitDecorator(object):
    def __init__(
        self,
        wait_period=900,
        clock=time.monotonic,
        on_exception=Exception,
        default_return_value=None,
    ):
        """
        Instantiate a RateLimitDecorator with some sensible defaults. By
        default the Twitter rate limiting window is respected (15 calls every
        15 minutes).
        :param wait_period: An upper bound time period (in seconds) before the rate
        limit resets.
        :param clock: An optional function retuning the current time.
        :param on_exception: the exception triggers the rate limit event
        :param default_return_value: returning value while the rate limit in progress
        """
        self.wait_period = wait_period
        self.clock = clock
        self.on_exception = on_exception
        self.default_return_value = default_return_value
        self.last_reset = 0

        # Add thread safety.
        self.lock = RLock()

    def __call__(self, func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            period_remaining = self._period_remaining()
            with self.lock:
                if self.last_reset == 0 or period_remaining <= 0:
                    try:
                        return func(*args, **kwargs)
                    except self.on_exception:
                        self.last_reset = self.clock()
                        logger.debug(
                            f"Rate limit on exception: \n{traceback.format_exc()}"
                            f"\nwill return default value until: {period_remaining}"
                            f" seconds."
                        )
                        return self.default_return_value
                logger.debug(
                    f"Rate limit in progress. Will return default value until: " f"{period_remaining} seconds."
                )
            logger.debug(
                f"Rate limit in progress. Lock not released yet. "
                f"Will return default value until: {period_remaining} seconds."
            )
            return self.default_return_value

        return wrapper

    def _period_remaining(self):
        """
        Return the period remaining for the current rate limit window.
        :return: The remaining period.
        :rtype: float
        """
        elapsed = self.clock() - self.last_reset
        return self.wait_period - elapsed


class Memoizer(DjangoMemoizer):
    def memoize_generator(self, timeout=DEFAULT_TIMEOUT, make_name=None, unless=None, max_allowed_cache_items=10000):
        """
        Added generator/iterator cache support by altering existing memoize method
        Args:
            timeout: default cache timeout
            make_name: func to generate cache key
            unless: bypass cache if this callable returns True
            max_allowed_cache_items: max number of items to cache to avoid infinite generators

        Returns:
            generator
        """

        def memoize(f):
            @functools.wraps(f)
            def decorated_function(*args, **kwargs):
                # bypass cache
                if callable(unless) and unless() is True:
                    yield from enforce_sequence(f(*args, **kwargs))
                    return

                is_iterator = isinstance(f, GeneratorType) or isinstance(f, Iterator)
                if not is_iterator:
                    yield from enforce_sequence(f(*args, **kwargs))
                    return
                # try to fetch the function's return value from the cache
                try:
                    cache_key = decorated_function.make_cache_key(f, *args, **kwargs)
                    rv = self.get(cache_key)
                except Exception:
                    if settings.DEBUG:
                        raise
                    logger.exception("Exception possibly due to cache backend.")
                    yield from enforce_sequence(f(*args, **kwargs))
                    return

                # if a cache miss occurs, run the function from scratch
                # and cache the resulting return value
                if rv != self.default_cache_value:
                    yield from enforce_sequence(rv)
                    return

                rv = f(*args, **kwargs)
                _cache_list = []
                item_count = 0

                for element in rv:
                    if item_count < max_allowed_cache_items:
                        _cache_list.append(element)
                    item_count += 1
                    yield element

                try:
                    if item_count >= max_allowed_cache_items:
                        del _cache_list
                        return
                    self.set(cache_key, _cache_list, timeout=decorated_function.cache_timeout)
                except Exception:
                    if settings.DEBUG:
                        raise
                    logger.exception("Exception possibly due to cache backend.")

            decorated_function.uncached = f
            decorated_function.cache_timeout = timeout
            decorated_function.make_cache_key = self._memoize_make_cache_key(make_name, decorated_function)
            decorated_function.delete_memoized = lambda: self.delete_memoized(f)

            return decorated_function

        return memoize


# Memoizer instance
_memoizer = Memoizer()

# Public objects
memoize = _memoizer.memoize
memoize_generator = _memoizer.memoize_generator
delete_memoized = _memoizer.delete_memoized
delete_memoized_verhash = _memoizer.delete_memoized_verhash
