"""Tests for Ingredients API."""
from django.contrib.auth import get_user_model
from django.urls import reverse
from django.test import TestCase

from rest_framework import status
from rest_framework.test import APIClient

from core.models import Ingredient
from recipe.serializers import IngredientSerializer

INGREDIENTS_URL = reverse('recipe:ingredient-list')


def detail_url(ingredient_id):
    """Create and return an ingredient URL"""
    return reverse('recipe:ingredient-detail', args=[ingredient_id])


def create_user(email='test@example.com', password='testpass123'):
    """Create and return new user."""
    return get_user_model().objects.create(email=email, password=password)


class PublicIngredientsApiTests(TestCase):
    """Tests unauthenticated API requests."""

    def setUp(self) -> None:
        self.client = APIClient()

    def test_auth_required(self):
        """Tests auth is required for retrieving ingredients."""
        res = self.client.get(INGREDIENTS_URL)

        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class PrivateIngredientsApiTests(TestCase):
    """Tests authenticated API requests."""

    def setUp(self) -> None:
        self.client = APIClient()
        # Create user and login
        self.user = create_user()
        self.client.force_authenticate(self.user)

    def test_auth_required(self):
        """Tests auth is required for retrieving ingredients."""
        # Create dummy data
        Ingredient.objects.create(user=self.user, name='Parsley')
        Ingredient.objects.create(user=self.user, name='Beef')

        # Send GET request
        res = self.client.get(INGREDIENTS_URL)

        # Check response
        self.assertEqual(res.status_code, status.HTTP_200_OK)

        # Query db for data and order by name
        ingredients = Ingredient.objects.all().order_by('-name')
        # Serialize to simulate API
        serialized = IngredientSerializer(ingredients, many=True)

        self.assertEqual(ingredients.count(), 2)
        self.assertEqual(res.data, serialized.data)

    def test_ingredients_limited_to_user(self):
        """Tests list of ingredients is limited to authenticated user"""
        # Create secondary user
        new_user = create_user(email='test2@example.com',
                               password='testpass231')
        # Create ingredients
        ingredient = Ingredient.objects.create(user=self.user, name='Parsley')
        Ingredient.objects.create(user=new_user, name='Beef')

        # Send GET request
        res = self.client.get(INGREDIENTS_URL)

        # Assert response is OK
        self.assertEqual(res.status_code, status.HTTP_200_OK)

        # Query db
        ingredients = Ingredient.objects.filter(user=self.user)
        # serialize data
        serialized = IngredientSerializer(ingredients, many=True)
        # Assert received same as db
        self.assertEqual(len(res.data), 1)
        self.assertEqual(res.data, serialized.data)

    def test_update_ingredient(self):
        """Test updating an ingredient."""
        # Create ingredient
        ingredient = Ingredient.objects.create(user=self.user, name='Bread')
        # Prepare for API call
        payload = {
            'name': 'Breadcrumbs'
        }
        url = detail_url(ingredient.id)
        # Send PATCH request
        res = self.client.patch(url, payload)

        # Assert response OK
        self.assertEqual(res.status_code, status.HTTP_200_OK)

        # Refresh ingredient details from db
        ingredient.refresh_from_db()
        # Assert name has been changed
        self.assertEqual(ingredient.name, payload['name'])

    def test_delete_ingredient(self):
        """Test deleting an ingredient."""
        # Create ingredient
        ingredient = Ingredient.objects.create(user=self.user, name='Bread')
        # Build url for API call
        url = detail_url(ingredient.id)
        # Send DELETE request
        res = self.client.delete(url)

        # Assert response code OK
        self.assertEqual(res.status_code, status.HTTP_204_NO_CONTENT)

        # Assert that no ingredient exists
        ingredients = Ingredient.objects.filter(user=self.user)
        self.assertFalse(ingredients.exists())
