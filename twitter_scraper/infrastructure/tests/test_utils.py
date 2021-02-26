from django.test import TestCase

from twitter_scraper.infrastructure.utils import enforce_sequence, get_list


class EnforceSequenceTestCase(TestCase):
    def test_given_not_sequence(self):
        value = 1
        expected_value = (value,)
        result = enforce_sequence(value)
        self.assertEqual(result, expected_value)

        value = "dummy"
        expected_value = (value,)
        result = enforce_sequence(value)
        self.assertEqual(result, expected_value)

        value = {"a": "b"}
        expected_value = (value,)

        result = enforce_sequence(value)
        self.assertEqual(result, expected_value)

    def test_given_sequence(self):
        value = [1, 2, 3]
        result = enforce_sequence(value)
        self.assertEqual(result, value)

        value = (1, 2, 3)
        result = enforce_sequence(value)
        self.assertEqual(result, value)


class GetListTestCase(TestCase):
    def test_given_dict_with_existing_keys(self):
        value = {"a": {"b": {"c": 1}}}
        expected_value = [1]
        result = get_list(value, ["a", "b", "c"])
        self.assertEqual(result, expected_value)

        value = {"a": {"b": {"c": 2}}}
        expected_value = [{"c": 2}]
        result = get_list(value, ["a", "b"])
        self.assertEqual(result, expected_value)

        value = {"a": {"b": {"c": 2}}}
        expected_value = [{"b": {"c": 2}}]
        result = get_list(value, "a")
        self.assertEqual(result, expected_value)

    def test_given_dict_with_non_existing_keys(self):
        value = {"a": {"b": {"c": 1}}}
        expected_value = []
        result = get_list(value, ["a", "d", "c"])
        self.assertEqual(result, expected_value)

        value = {"a": {"b": {"c": 2}}}
        expected_value = []
        result = get_list(value, "d")
        self.assertEqual(result, expected_value)
