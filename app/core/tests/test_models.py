"""
Tests for models.
"""
from decimal import Decimal
# base test class
from django.test import TestCase
# helper model from django to get default user model for project
from django.contrib.auth import get_user_model
# For rest of models in core
from core import models


def create_user(email='user@example.com', password='testpass123'):
    """Create and return a new user."""
    return get_user_model().objects.create_user(email, password)


class ModelTests(TestCase):
    """Test models."""

    def test_create_user_with_email_successful(self):
        """Test creating a user with an email is successful"""
        # init details
        email = 'test@example.com'
        password = 'testpass123'

        user = get_user_model().objects.create_user(email=email, password=password)

        self.assertEqual(user.email, email)
        self.assertTrue(user.check_password(password))

    def test_new_user_email_normalized(self):
        """Test that the email is normalized for new users.
        The domain should be normalized, however, the username should not.
        """
        # Sample emails to test
        sample_emails = [
            ["test1@EXAMPLE.com", "test1@example.com"],
            ["Test2@Example.com", "Test2@example.com"],
            ["TEST3@EXAMPLE.com", "TEST3@example.com"],
            ["test4@example.COM", "test4@example.com"],
        ]

        # Test each email above
        for email, expected in sample_emails:
            user = get_user_model().objects.create_user(email=email, password="sample123")

            # Check if email normalized
            self.assertEqual(user.email, expected)

    def test_new_user_without_email_raises_error(self):
        """Test that creating a user without an email raises a value error."""
        # Check for value error while completing
        with self.assertRaises(ValueError):
            # Creation of new user with an empty email
            get_user_model().objects.create_user(email="", password="sample123")

    def test_create_superuser(self):
        """Test creating a superuser."""
        user = get_user_model().objects.create_superuser(
            email="test@example.com", password="sample123")

        self.assertTrue(user.is_superuser)
        self.assertTrue(user.is_staff)

    def test_create_recipe(self):
        """Test creating a recipe is successful."""
        # Create user to attach to recipe
        user = get_user_model().objects.create_user(
            'test@example.com',
            'testpass123'
        )
        # Create recipe
        recipe = models.Recipe.objects.create(
            user=user,
            title='Sample name',
            time_minutes=5,
            price=Decimal('5.50'),
            description='Sample recipe description.'
        )

        # Asserts that a stringified recipe will return the title
        self.assertEqual(str(recipe), recipe.title)

    def test_create_tag(self):
        """Tests creation of new tag is successful."""
        user = create_user()

        tag = models.Tag.objects.create(
            user=user,
            name="SampleTag"
        )

        self.assertEqual(str(tag), tag.name)

    def test_create_ingredient(self):
        """Tests creation of ingredient successful and returns name as string"""
        user = create_user()

        ingredient = models.Ingredient.objects.create(
            user=user, name='Ingredient 1')

        self.assertEqual(str(ingredient), ingredient.name)
