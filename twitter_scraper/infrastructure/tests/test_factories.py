from django.test import TestCase

from twitter_scraper.infrastructure.exceptions import (
    BuilderNotFoundError,
    CanNotBuildError,
)
from twitter_scraper.infrastructure.factories import ObjectFactory


class ObjectFactoryTestCase(TestCase):
    def setUp(self):
        self.factory = ObjectFactory()

        def dummy_builder(first_value, second_value):
            return [first_value, second_value]

        self._dummy_builder = dummy_builder

    def test_register(self):
        self.factory.register_builder("dummy", self._dummy_builder)
        self.assertIn("dummy", self.factory._builders)
        self.assertEqual(self._dummy_builder, self.factory._builders["dummy"])

    def test_create_given_valid_key(self):
        self.factory.register_builder("dummy", self._dummy_builder)
        result = self.factory.create("dummy", first_value="first", second_value="second")
        self.assertListEqual(result, ["first", "second"])

    def test_create_given_invalid_key(self):
        with self.assertRaises(BuilderNotFoundError):
            self.factory.create(key="dummy")

    def test_create_given_invalid_params(self):
        with self.assertRaises(CanNotBuildError):
            self.factory.register_builder("dummy", self._dummy_builder)
            self.factory.create(key="dummy", dummy="dummy")
