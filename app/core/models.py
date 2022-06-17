"""Database models."""
from django.db import models
from django.contrib.auth.models import (
    AbstractBaseUser, BaseUserManager, PermissionsMixin)

# Create your models here.


class UserManager(BaseUserManager):
    """Manager for users."""

    # create_user replaces default function
    # password=None is default Django behavior and allows for creation of unusable users
    def create_user(self, email, password=None, **extra_fields):
        """Create save and return a new user."""
        # create user model using email. self = User model
        # extra fields will be added in the case of future additional fields
        # Domain of email is normalized ie. lowercased
        user = self.model(email=self.normalize_email(email), **extra_fields)
        # set the password using hash
        user.set_password(password)
        # save to db using the current db where users are stored
        user.save(using=self._db)

        return user


# Base user is the functionality of the auth system
# Permissions mixin is the functionality of permissions and fields
class User(AbstractBaseUser, PermissionsMixin):
    """User in the system."""
    email = models.EmailField(max_length=255, unique=True)
    name = models.CharField(max_length=255)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)

    # Assign class UserManager to User
    objects = UserManager()

    # Defines default field used for authentication
    USERNAME_FIELD = 'email'
