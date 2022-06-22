"""Tests for the user API."""

from django.test import TestCase
from django.contrib.auth import get_user_model
from django.urls import reverse

from rest_framework.test import APIClient
from rest_framework import status

CREATE_USER_URL = reverse('user:create')
TOKEN_URL = reverse('user:token')

# **params allows any parameters to be passed


def create_user(**params):
    """Create and return a new user."""
    return get_user_model().objects.create_user(**params)


class PublicUserApiTests(TestCase):
    """Test the public features of the user API."""

    def setUp(self):
        self.client = APIClient()

    def test_create_user_success(self):
        """Test creating a user is successful."""
        payload = {
            'email': 'test@example.com',
            'password': 'testpass123',
            'name': 'Test Name'
        }

        # Post new user to create user URL
        res = self.client.post(CREATE_USER_URL, payload)

        # Check that returned status code is correct
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        # Ensure key password is not returned in response for security purposes
        self.assertNotIn('password', res.data)

        # Obtain associated user model from db
        user = get_user_model().objects.get(email=payload['email'])

        # Check if payload details were created
        self.assertTrue(user.check_password(payload['password']))
        self.assertEqual(user.email, payload['email'])
        self.assertEqual(user.name, payload['name'])

    def test_user_with_email_exists_error(self):
        """Test that error is returned if user with email exists."""
        payload = {
            'email': 'test@example.com',
            'password': 'testpass123',
            'name': 'Test Name'
        }

        # Create user with above email
        create_user(**payload)

        # Try to create user for second time with same email
        res = self.client.post(CREATE_USER_URL, payload)

        # Check response is bad request
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_password_too_short_error(self):
        """Test an error is returned if password is less than 5 chars."""
        payload = {
            'email': 'test@example.com',
            'password': 't3',
            'name': 'Test Name'
        }
        # Attempt to create user with short password
        res = self.client.post(CREATE_USER_URL, payload)
        # Ensure bad request returned
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

        # Search db for user if exists
        user_exists = get_user_model().objects.filter(
            email=payload['email']).exists()
        # check that false returned
        self.assertFalse(user_exists)
