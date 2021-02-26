from unittest import mock

from django.test import TestCase
from memoize import DEFAULT_CACHE_OBJECT

from twitter_scraper.infrastructure.decorators import (
    RateLimitDecorator,
    memoize_generator,
)

memoizer_path = "twitter_scraper.infrastructure.decorators"


class DummyClock:
    now = 0

    def __call__(self):
        return self.now

    def reset(self):
        self.now = 0

    def increment(self, num=1):
        self.now += num


class DummyException(Exception):
    pass


class RateLimitDecoratorTestCase(TestCase):
    def setUp(self):
        self.original_return_value = 1
        self.dummy_func = mock.Mock(return_value=self.original_return_value)
        self.return_value = "rate_limit_triggered"
        self.wait_period = 10
        self.clock = DummyClock()
        self.clock.now = 100
        self.decorator = RateLimitDecorator(
            on_exception=DummyException,
            wait_period=self.wait_period,
            clock=self.clock,
            default_return_value=self.return_value,
        )
        self.decorated_func = self.decorator(self.dummy_func)

    def test_rate_limit_not_triggered(self):
        result = self.decorated_func()
        self.assertEqual(result, self.original_return_value)

    def test_rate_limit_triggered(self):
        result = self.decorated_func()
        self.assertEqual(result, self.original_return_value)

        self.dummy_func.side_effect = DummyException
        result = self.decorated_func()
        self.assertEqual(result, self.return_value)

        self.clock.increment(5)
        result = self.decorated_func()
        self.assertEqual(result, self.return_value)

        self.clock.increment(10)
        self.dummy_func.side_effect = None
        result = self.decorated_func()
        self.assertEqual(result, self.original_return_value)


@mock.patch(f"{memoizer_path}._memoizer._memoize_make_cache_key", return_value=mock.Mock(return_value="dummy"))
@mock.patch(f"{memoizer_path}._memoizer.cache.set")
@mock.patch(f"{memoizer_path}._memoizer.cache.get", return_value=DEFAULT_CACHE_OBJECT)
class MemoizeDecoratorTestCase(TestCase):
    def setUp(self):
        self.original_return_value = [1, 2, 3, 4]
        self.cached_value = ["cached"]
        self.dummy_func = mock.Mock(return_value=self.original_return_value)
        self.dummy_generator = mock.MagicMock()
        self.dummy_generator.return_value.__iter__.return_value = iter(self.original_return_value)

        # modify mock object's im_class and __name__ attribute to prevent getting error in memoize decorator
        self.dummy_generator.im_class.__name__ = "MagicMock"
        self.dummy_generator.__name__ = "dummy_generator"

    def test_memoize_generator_with_no_generator(self, mock_cache_get, mock_cache_set, _):
        self.decorated_func = memoize_generator()(self.dummy_func)
        self.assertEqual(list(self.decorated_func()), self.original_return_value)
        self.assertEqual(self.dummy_func.call_count, 1)
        self.assertEqual(mock_cache_get.call_count, 0)
        self.assertEqual(mock_cache_set.call_count, 0)

    def test_memoize_generator_cache_found_with_valid_generator(self, mock_cache_get, mock_cache_set, _):
        mock_cache_get.return_value = self.cached_value
        self.decorated_func = memoize_generator()(self.dummy_generator)
        result = self.decorated_func()
        self.assertEqual(list(result), self.cached_value)
        self.assertEqual(mock_cache_get.call_count, 1)
        self.assertEqual(mock_cache_set.call_count, 0)

    def test_memoize_generator_cache_not_found_with_valid_generator(self, mock_cache_get, mock_cache_set, _):
        self.decorated_func = memoize_generator()(self.dummy_generator)
        result = self.decorated_func()
        self.assertEqual(list(result), self.original_return_value)
        self.assertEqual(mock_cache_get.call_count, 1)
        self.assertEqual(mock_cache_set.call_count, 1)

    def test_memoize_generator_get_cached_result_with_valid_generator(self, mock_cache_get, mock_cache_set, _):
        self.decorated_func = memoize_generator()(self.dummy_generator)
        result = self.decorated_func()
        self.assertEqual(list(result), self.original_return_value)
        self.assertEqual(mock_cache_get.call_count, 1)
        self.assertEqual(mock_cache_set.call_count, 1)

        mock_cache_get.return_value = self.original_return_value
        result = self.decorated_func()
        self.assertEqual(list(result), self.original_return_value)
        self.assertEqual(mock_cache_get.call_count, 2)
        self.assertEqual(mock_cache_set.call_count, 1)

    def test_memoize_generator_exceed_max_cache_item_with_valid_generator(self, mock_cache_get, mock_cache_set, _):
        max_items = 5
        return_value = list(range(7))
        self.dummy_generator.return_value.__iter__.return_value = return_value
        self.decorated_func = memoize_generator(max_allowed_cache_items=max_items)(self.dummy_generator)
        result = self.decorated_func()
        self.assertEqual(list(result), return_value)
        self.assertEqual(mock_cache_get.call_count, 1)
        self.assertEqual(mock_cache_set.call_count, 0)
