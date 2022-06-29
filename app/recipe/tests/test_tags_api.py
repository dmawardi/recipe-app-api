"""
    Tests for the tags API.
"""

from django.contrib.auth import get_user_model
from django.urls import reverse
from django.test import TestCase

from rest_framework import status
from rest_framework.test import APIClient

from core.models import Tag

from recipe.serializers import TagSerializer

TAGS_URL = reverse('recipe:tag-list')


def detail_url(tag_id):
    """Returns url for specific tag detail"""
    return reverse('recipe:tag-detail', args=[tag_id])


def create_user(email='test@example.com', password='samplepass123'):
    """Create and return a new user."""
    return get_user_model().objects.create_user(email, password)


class PublicTagsApiTests(TestCase):
    """Tests unauthenticated"""

    def setUp(self) -> None:
        self.client = APIClient()

    def test_auth_required(self):
        """Tests auth is required for retrieving tag"""
        res = self.client.get(TAGS_URL)

        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class PrivateTagsApiTests(TestCase):
    """Tests authenticated API requests."""

    def setUp(self) -> None:
        # Create user
        self.user = create_user()
        # Init API Client
        self.client = APIClient()
        # Authenticate using user
        self.client.force_authenticate(self.user)

    def test_retrieve_tags(self):
        """Test retrieving a list of tags."""
        Tag.objects.create(user=self.user, name="Vegan")
        Tag.objects.create(user=self.user, name="Dessert")

        # Send auth GET request
        res = self.client.get(TAGS_URL)

        # Obtain from db
        tags = Tag.objects.all().order_by('-name')
        # Run data through serializer
        serialized = TagSerializer(tags, many=True)

        # Assert response and status code as expected
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serialized.data)

    def test_tags_limited_to_user(self):
        """Tests list of tags limited to user."""
        # Create second user
        new_user = create_user(email='user2@example.com')
        # Create dummy data
        Tag.objects.create(user=new_user, name='Dessert')
        tag = Tag.objects.create(user=self.user, name='Vegan')

        # Send GET request
        res = self.client.get(TAGS_URL)

        # Assert response and status code as expected
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        # Check length of response is 1
        self.assertEqual(len(res.data), 1)
        # Check fields are the same
        self.assertEqual(res.data[0]['name'], tag.name)
        self.assertEqual(res.data[0]['id'], tag.id)

    def test_update_tag(self):
        """Tests updating of tag in database."""
        # Create tag in system
        tag = Tag.objects.create(user=self.user, name='Dessert')

        # setup request
        update_url = detail_url(tag.id)
        payload = {
            'name': 'Desert'
        }
        # Send PATCH request
        res = self.client.patch(update_url, payload)

        # update db object
        tag.refresh_from_db()

        # Check response equal
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(tag.name, payload['name'])

    def test_delete_tag(self):
        """Tests deletion of tag in database."""
        # Create tag
        tag = Tag.objects.create(user=self.user, name="Dessert")

        # Build url using tag id
        deletion_url = detail_url(tag.id)
        # Send DELETE request
        res = self.client.delete(deletion_url)

        # Assert response as expected
        self.assertEqual(res.status_code, status.HTTP_204_NO_CONTENT)
        # Assert tag no longer in db
        tag_exists = Tag.objects.filter(id=tag.id).exists()
        self.assertFalse(tag_exists)
