from twitter_scraper.infrastructure.exceptions import Error


class TwitterBaseError(Error):
    pass


class TwitterUnknown(TwitterBaseError):
    pass


class TwitterBadRequest(TwitterBaseError):
    pass


class TwitterAuthorization(TwitterBaseError):
    pass


class TwitterAccessForbidden(TwitterBaseError):
    pass


class TwitterNotFound(TwitterBaseError):
    pass


class TwitterInvalidRequestFormat(TwitterBaseError):
    pass


class TwitterRateLimit(TwitterBaseError):
    pass


class TwitterInvalidFilters(TwitterBaseError):
    pass


ERRORS = {
    400: TwitterBadRequest,
    401: TwitterAuthorization,
    403: TwitterAccessForbidden,
    404: TwitterNotFound,
    406: TwitterInvalidRequestFormat,
    429: TwitterRateLimit,
}
