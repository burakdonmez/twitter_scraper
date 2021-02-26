from django.contrib.auth.models import AbstractUser


class User(AbstractUser):
    """Custom user model to extend. This will be used for AUTH_USER_MODEL. Deriving from
     Django AbstractUser class
    is fine for now.

    Args:
        AbstractUser (Class): Django Default AbstractUser class with default
        authentication permissions
    """
