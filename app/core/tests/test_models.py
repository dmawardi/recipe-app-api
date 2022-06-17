"""
Tests for models.
"""
# base test class
from django.test import TestCase
# helper model from django to get default user model for project
from django.contrib.auth import get_user_model


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
