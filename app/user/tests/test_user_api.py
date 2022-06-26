"""Tests for the user API."""

from django.test import TestCase
from django.contrib.auth import get_user_model
from django.urls import reverse

from rest_framework.test import APIClient
from rest_framework import status

CREATE_USER_URL = reverse('user:create')
TOKEN_URL = reverse('user:token')
ME_URL = reverse('user:me')

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

    def test_create_token_for_user(self):
        """Test generates token for valid credentials"""
        # User creation details
        user_details = {
            'email': 'test@example.com',
            'password': 'test-user-123',
            'name': 'Test Name'
        }
        # Create user with above credentials
        create_user(**user_details)

        # payload for login
        payload = {
            'email': user_details['email'],
            'password': user_details['password'],
        }
        # Login with payload credentials
        res = self.client.post(TOKEN_URL, payload)
        # Test token contained in response and status code is OK
        self.assertIn('token', res.data)
        self.assertEqual(res.status_code, status.HTTP_200_OK)

    def test_create_token_bad_credentials(self):
        """Test returns error if credentials invalid."""
        # User creation details
        user_details = {
            'email': 'test@example.com',
            'password': 'test-user-123',
            'name': 'Test Name'
        }
        # Create user with above credentials
        create_user(**user_details)

        # payload for login
        payload = {
            'email': user_details['email'],
            'password': 'wrong-pass',
        }
        # Send incorrect credentials
        res = self.client.post(TOKEN_URL, payload)

        # Ensure bad request returned
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)
        # Ensure key token not returned in response data
        self.assertNotIn('token', res.data)

    def test_create_token_blank_password(self):
        """Test returns error if password is blank."""
        # User creation details
        user_details = {
            'email': 'test@example.com',
            'password': 'test-user-123',
            'name': 'Test Name'
        }
        # Create user with above credentials
        create_user(**user_details)

        # payload for login
        payload = {
            'email': user_details['email'],
            'password': '',
        }
        # Send incorrect credentials
        res = self.client.post(TOKEN_URL, payload)

        # Ensure bad request returned
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)
        # Ensure key token not returned in response data
        self.assertNotIn('token', res.data)

    def test_retrieve_user_unauthorized(self):
        """Test that authentication is required for users."""

        res = self.client.get(ME_URL)
        print('recv status code: '+str(res.status_code))

        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class PrivateUserApiTests(TestCase):
    """Test API requests that require authentication."""

    def setUp(self):
        # Create user
        user_details = {
            'email': 'test@example.com',
            'password': 'test123abc',
            'name': 'Test Name'
        }
        self.user = create_user(**user_details)

        # Set client
        self.client = APIClient()
        # Authenticate using user
        self.client.force_authenticate(user=self.user)

    def test_retrieve_profile_success(self):
        """Test retrieving profile when authenticated"""
        res = self.client.get(ME_URL)
        # Check response and data as expected
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, {
            'name': self.user.name,
            'email': self.user.email
        })

    def test_post_me_not_allowed(self):
        """Test POST not allowed for me endpoint"""
        res = self.client.post(ME_URL, {})

        # Check that POST method is not allowed
        self.assertEqual(res.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

    def test_update_user_profile(self):
        """Test updating the user profile for the authenticated user"""
        payload = {
            'name': 'Updated Name',
            'password': 'BobRyan123'
        }
        res = self.client.patch(ME_URL, payload)

        # ORM object refresh
        self.user.refresh_from_db()
        # Status code
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        # db values
        self.assertEqual(self.user.name, payload['name'])
        self.assertTrue(self.user.check_password(payload['password']))
