class Error(Exception):
    """Base exception for the project. All custom exceptions must be derived from this.

    Args:
        Exception (Class): Python Exception Class
    """


class ObjectFactoryError(Error):
    """[summary]

    Args:
        Error ([type]): Base error
    """


class BuilderNotFoundError(ObjectFactoryError):
    """[summary]

    Args:
        Error ([type]): [description]
    """


class CanNotBuildError(ObjectFactoryError):
    """[summary]

    Args:
        Error ([type]): [description]
    """
