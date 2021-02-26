from unittest import mock

from django.test import TestCase

from twitter_scraper.infrastructure.services import RequestPaginator


class RequestPaginatorTestCase(TestCase):
    def setUp(self):
        self.paginator_klass = RequestPaginator
        self.request = mock.Mock(return_value=None)
        self.next_page_request = mock.Mock(return_value=None)

    def _prepare_paginator(self, iter_objects_func=None, has_next_page_func=None):
        self.iter_objects = iter_objects_func or mock.Mock(return_value=[])
        self.has_next_page = has_next_page_func or mock.Mock(return_value=False)
        self.paginator = self.paginator_klass(
            request_func=self.request,
            iter_objects_func=self.iter_objects,
            next_page_request_func=self.next_page_request,
            has_next_page_func=self.has_next_page,
        )

    def test_empty_result(self):
        self.iter_objects = mock.Mock(return_value=[])
        self.has_next_page = mock.Mock(return_value=False)
        self._prepare_paginator(iter_objects_func=self.iter_objects, has_next_page_func=self.has_next_page)

        self.assertEqual(list(self.paginator.get_objects()), [])
        self.assertEqual(self.request.call_count, 1)
        self.assertEqual(self.iter_objects.call_count, 1)
        self.assertEqual(self.has_next_page.call_count, 0)
        self.assertEqual(self.next_page_request.call_count, 0)

    def test_without_max_limit_and_no_next_page(self):
        return_value = list(range(10))
        self.iter_objects = mock.Mock(return_value=return_value)
        self.has_next_page = mock.Mock(return_value=False)
        self._prepare_paginator(iter_objects_func=self.iter_objects, has_next_page_func=self.has_next_page)

        result = list(self.paginator.get_objects())
        self.assertEqual(result, return_value)
        self.assertEqual(self.request.call_count, 1)
        self.assertEqual(self.iter_objects.call_count, 1)
        self.assertEqual(self.has_next_page.call_count, 1)
        self.assertEqual(self.next_page_request.call_count, 0)

    def test_exceed_max_limit_and_no_next_page(self):
        return_value = ["x"] * 10
        max_items = 5
        self.iter_objects = mock.Mock(return_value=return_value)
        self.has_next_page = mock.Mock(return_value=False)
        self._prepare_paginator(iter_objects_func=self.iter_objects, has_next_page_func=self.has_next_page)
        self.paginator(max_items=max_items)

        result = list(self.paginator.get_objects())
        self.assertEqual(result, ["x"] * max_items)
        self.assertEqual(self.request.call_count, 1)
        self.assertEqual(self.iter_objects.call_count, 1)
        self.assertEqual(self.has_next_page.call_count, 0)
        self.assertEqual(self.next_page_request.call_count, 0)

    def test_exceed_max_limit_with_next_page(self):
        return_value = ["x"] * 10
        max_items = 5
        self.iter_objects = mock.Mock(return_value=return_value)
        self.has_next_page = mock.Mock(return_value=True)
        self._prepare_paginator(iter_objects_func=self.iter_objects, has_next_page_func=self.has_next_page)
        self.paginator(max_items=max_items)

        result = list(self.paginator.get_objects())
        self.assertEqual(result, ["x"] * max_items)
        self.assertEqual(self.request.call_count, 1)
        self.assertEqual(self.iter_objects.call_count, 1)
        self.assertEqual(self.has_next_page.call_count, 0)
        self.assertEqual(self.next_page_request.call_count, 0)

    def test_less_than_max_limit_with_next_page(self):
        return_value = ["x"] * 5
        max_items = 14
        self.iter_objects = mock.Mock(return_value=return_value)
        self.has_next_page = mock.Mock(return_value=True)
        self._prepare_paginator(iter_objects_func=self.iter_objects, has_next_page_func=self.has_next_page)
        self.paginator(max_items=max_items)

        result = list(self.paginator.get_objects())
        self.assertEqual(result, ["x"] * max_items)
        self.assertEqual(self.request.call_count, 1)
        self.assertEqual(self.iter_objects.call_count, 3)
        self.assertEqual(self.has_next_page.call_count, 2)
        self.assertEqual(self.next_page_request.call_count, 2)

    def test_equal_max_limit_with_next_page(self):
        return_value = ["x"] * 10
        max_items = 10
        self.iter_objects = mock.Mock(return_value=return_value)
        self.has_next_page = mock.Mock(return_value=True)
        self._prepare_paginator(iter_objects_func=self.iter_objects, has_next_page_func=self.has_next_page)
        self.paginator(max_items=max_items)

        result = list(self.paginator.get_objects())
        self.assertEqual(result, ["x"] * max_items)
        self.assertEqual(self.request.call_count, 1)
        self.assertEqual(self.iter_objects.call_count, 1)
        self.assertEqual(self.has_next_page.call_count, 0)
        self.assertEqual(self.next_page_request.call_count, 0)

    def test_exceed_max_page_with_next_page_and_max_limit(self):
        return_value = ["x"] * 5
        max_items = 10
        max_pages = 1
        self.iter_objects = mock.Mock(return_value=return_value)
        self.has_next_page = mock.Mock(return_value=True)
        self._prepare_paginator(iter_objects_func=self.iter_objects, has_next_page_func=self.has_next_page)
        self.paginator(max_items=max_items, max_pages=max_pages)

        result = list(self.paginator.get_objects())
        self.assertEqual(result, return_value)
        self.assertEqual(self.request.call_count, 1)
        self.assertEqual(self.iter_objects.call_count, 2)
        self.assertEqual(self.has_next_page.call_count, 1)
        self.assertEqual(self.next_page_request.call_count, 1)
