"""Tests for recipe APIs."""
from decimal import Decimal

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from rest_framework import status
from rest_framework.test import APIClient

from core.models import Recipe

from recipe.serializers import (RecipeSerializer, RecipeDetailSerializer)

RECIPES_URL = reverse('recipe:recipe-list')


def detail_url(recipe_id):
    """Create and return a recipe detail URL."""
    return reverse('recipe:recipe-detail', args=[recipe_id])


def create_recipe_user(user, **params):
    """Create and return a simple recipe."""
    defaults = {
        'title': 'sample recipe title',
        'time_minutes': 22,
        'price': Decimal('5.25'),
        'description': 'Sample description',
        'link': 'http://www.example.com/recipe.pdf'
    }
    # Update defaults with any additional params
    defaults.update(params)

    # Create new recipe object
    recipe = Recipe.objects.create(user=user, **defaults)

    return recipe


class PublicRecipeAPITests(TestCase):
    """Tests unauthenticated Recipe APIs"""

    def setUp(self) -> None:
        # Set API client to self object
        self.client = APIClient()

    def test_auth_required(self):
        """Test auth is required to call API."""
        res = self.client.get(RECIPES_URL)
        print(f'recv status: {res.status_code}')
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class PrivateRecipeAPITest(TestCase):
    """Test authenticated Recipe API requests"""

    def setUp(self) -> None:
        self.client = APIClient()

        # Create user
        self.user = get_user_model().objects.create_user(
            email="test@example.com", password="pass123abc")
        # login to user
        self.client.force_authenticate(self.user)

    def test_retrieve_recipes(self):
        """Test retrieving a list of recipes"""

        # create recipes for retrieving
        create_recipe_user(user=self.user)
        create_recipe_user(user=self.user)

        # Get recipes
        res = self.client.get(RECIPES_URL)

        # Retrieve recipes and order by id in reverse order
        recipes = Recipe.objects.all().order_by('-id')
        # Produce data dictionary of objects passed through the serializer
        # 'many = true' indicates multiple items
        serializer = RecipeSerializer(recipes, many=True)

        # Check response status code OK
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        # Check response data is equal to serializer data
        self.assertEqual(res.data, serializer.data)

    def test_recipe_list_limited_to_user(self):
        """Test list of recipes limited to authenticated user."""
        other_user = get_user_model().objects.create_user(
            email="test@duo.com", password="pass123abc")

        # Create recipes for retrieving
        create_recipe_user(user=self.user)
        create_recipe_user(user=other_user)

        # GET Recipes
        res = self.client.get(RECIPES_URL)
        # Query db for data to compare. filter for current user
        recipes = Recipe.objects.filter(user=self.user)
        serialized = RecipeSerializer(recipes, many=True)

        # Check response status code OK
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        # Check response data is equal to serializer data
        self.assertEqual(res.data, serialized.data)

    def test_get_recipe_detail(self):
        """Test get recipe detail."""
        # Create new recipe
        recipe = create_recipe_user(user=self.user)
        # Obtain detail using client
        res = self.client.get(detail_url(recipe.id))

        # Pass created recipe through serializer
        serialized = RecipeDetailSerializer(recipe)

        # Check response status code OK
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        # Check response data is equal to serializer data
        self.assertEqual(res.data, serialized.data)

    def test_create_recipe_self(self):
        """Test creating a recipe."""
        payload = {
            'title': 'sample recipe title',
            'time_minutes': 30,
            'price': Decimal('5.99'),
            'description': 'Sample description',
            'link': 'http://www.example.com/recipe.pdf'
        }

        # POST Recipe
        res = self.client.post(RECIPES_URL, payload)  # api/recipe/recipes

        # Assert response correct
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)

        # Query db for recipe
        recipe = Recipe.objects.get(id=res.data['id'])
        # Loop through payload items
        for k, v in payload.items():
            # Obtain matching key from recipe and compare with value
            self.assertEqual(getattr(recipe, k), v)

        # Assert user also matches with creator
        self.assertEqual(recipe.user, self.user)
