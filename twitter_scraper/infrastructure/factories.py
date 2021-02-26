from twitter_scraper.infrastructure.exceptions import (
    BuilderNotFoundError,
    CanNotBuildError,
)


class ObjectFactory:
    def __init__(self):
        self._builders = {}

    def register_builder(self, key, builder):
        self._builders[key] = builder

    def create(self, key, **kwargs):
        builder = self._builders.get(key)
        if not builder:
            raise BuilderNotFoundError(key)
        try:
            obj = builder(**kwargs)
        except (TypeError, KeyError) as exc:
            raise CanNotBuildError(repr(exc))
        return obj
