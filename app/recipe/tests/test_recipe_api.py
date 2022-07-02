"""Tests for recipe APIs."""
from decimal import Decimal
from re import T

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from rest_framework import status
from rest_framework.test import APIClient

from core.models import (Recipe, Tag, Ingredient)

from recipe.serializers import (
    RecipeSerializer, RecipeDetailSerializer, IngredientSerializer)

RECIPES_URL = reverse('recipe:recipe-list')

# Helper functions


def detail_url(recipe_id):
    """Create and return a recipe detail URL."""
    return reverse('recipe:recipe-detail', args=[recipe_id])


def create_recipe(user, **params):
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


def create_user(**params):
    """Create and return a new user."""
    return get_user_model().objects.create_user(**params)


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
        self.user = create_user(
            email="test@example.com", password="pass123abc")
        # login to user
        self.client.force_authenticate(self.user)

    def test_retrieve_recipes(self):
        """Test retrieving a list of recipes"""

        # create recipes for retrieving
        create_recipe(user=self.user)
        create_recipe(user=self.user)

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
        other_user = create_user(
            email="test@duo.com", password="pass123abc")

        # Create recipes for retrieving
        create_recipe(user=self.user)
        create_recipe(user=other_user)

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
        recipe = create_recipe(user=self.user)
        # Obtain detail using client
        res = self.client.get(detail_url(recipe.id))

        # Pass created recipe through serializer
        serialized = RecipeDetailSerializer(recipe)

        # Check response status code OK
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        # Check response data is equal to serializer data
        self.assertEqual(res.data, serialized.data)

    def test_create_recipe(self):
        """Test creating a recipe."""
        payload = {
            'title': 'sample recipe title',
            'time_minutes': 30,
            'price': Decimal('5.99'),
            'description': 'Sample description',
            'link': 'http://www.example.com/recipe.pdf'
        }

        # POST Recipe
        try:
            res = self.client.post(RECIPES_URL, payload,
                                   format='json')  # api/recipe/recipes
        except Exception as e:
            print(e)

        # print(f'response for recipe create: {res.status_code}')
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

    def test_partial_update(self):
        """Test partial update of a recipe."""
        payload = {
            'title': 'Updated Recipe Name',
            'time_minutes': 35,
            'description': 'Updated description',
        }

        # Create recipe
        recipe = create_recipe(user=self.user)

        # Create url based on recipe id
        url = detail_url(recipe.id)
        # PATCH update to url
        res = self.client.patch(url, payload)

        # Ensure response status code is OK
        self.assertEqual(res.status_code, status.HTTP_200_OK)

        # Refresh updated recipe from db
        recipe.refresh_from_db()

        # Cycle through payload keys and check equal
        for k, v in payload.items():
            # Obtain matching key from recipe and compare with value
            self.assertEqual(getattr(recipe, k), v)

        # Assert user also matches with creator
        self.assertEqual(recipe.user, self.user)

    def test_full_update(self):
        """Test full update of a recipe."""
        recipe = create_recipe(user=self.user)
        payload = {
            'title': 'Updated recipe title',
            'time_minutes': 37,
            'price': Decimal('8.25'),
            'description': 'Updated description',
            'link': 'http://www.updated.com/recipe.pdf'
        }

        # Create url based on recipe id
        url = detail_url(recipe.id)
        # PATCH update to url
        res = self.client.put(url, payload)

        # Ensure response status code is OK
        self.assertEqual(res.status_code, status.HTTP_200_OK)

        # Refresh updated recipe from db
        recipe.refresh_from_db()

        # Cycle through payload keys and check equal
        for k, v in payload.items():
            # Obtain matching key from recipe and compare with value
            self.assertEqual(getattr(recipe, k), v)

        # Assert user also matches with creator
        self.assertEqual(recipe.user, self.user)

    def test_update_recipe_user_returns_error(self):
        """Test that updating a user for a recipe returns an error"""
        # Create a new user to move the recipe to
        new_user = create_user(email="wookie@test.com", password='beluga123')
        # Create a recipe using current user
        recipe = create_recipe(user=self.user)

        payload = {
            'user': new_user.id
        }
        # Generate specific detial url
        url = detail_url(recipe.id)

        # PATCH update to particular recipe
        res = self.client.patch(url, payload)

        # Refresh recipe
        recipe.refresh_from_db()

        # Assert that unsuccessful and blocked
        self.assertEqual(recipe.user, self.user)

    def test_delete_recipe(self):
        """Tests that deleting a recipe is successful."""
        # Create recipe for current user
        recipe = create_recipe(user=self.user)
        # Generate recipe url
        url = detail_url(recipe.id)
        # DELETE request to specific recipe url
        res = self.client.delete(url)

        # Check if recipe still exists
        recipe_exists = Recipe.objects.filter(id=recipe.id).exists()

        # Assert response was successful and that recipe no longer exists
        self.assertEqual(res.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(recipe_exists)

    def test_delete_other_users_recipe_error(self):
        # Create a new user to move the recipe to
        new_user = create_user(email="wookie@test.com", password='beluga123')
        # Create recipe for different user
        recipe = create_recipe(user=new_user)

        # Generate recipe url
        url = detail_url(recipe.id)
        # DELETE request to specific recipe url
        res = self.client.delete(url)

        # Check if recipe still exists
        recipe_exists = Recipe.objects.filter(id=recipe.id).exists()

        # Assert response was successful and that recipe still exists
        self.assertEqual(res.status_code, status.HTTP_404_NOT_FOUND)
        self.assertTrue(recipe_exists)

    def test_create_recipe_with_new_tags(self):
        """Test creating a recipe with new tags."""
        payload = {
            'title': 'Thai Prawn Curry',
            'time_minutes': 45,
            'price': Decimal('10.55'),
            'description': 'Prawn Curry description',
            'link': 'http://www.updated.com/recipe.pdf',
            'tags': [{'name': 'Thai'}, {'name': 'Dinner'}]
        }

        # POST request
        res = self.client.post(RECIPES_URL, payload, format='json')

        # Ensure response is correct
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)

        recipes = Recipe.objects.filter(user=self.user)
        # Check that there's 1 recipe before accessing
        self.assertEqual(recipes.count(), 1)
        # Grab only recipe and ensure there are two tags associated
        recipe = recipes[0]
        # Check there's 2 tags
        self.assertEqual(recipe.tags.count(), 2)

        # Iterate through tags in payload
        for tag in payload['tags']:
            # Check for matching tag in first recipe to see if exists
            exists = recipe.tags.filter(
                name=tag['name'], user=self.user).exists()
            self.assertTrue(exists)

    def test_create_recipe_with_existing_tags(self):
        """Test creating a recipe with existing tag."""
        tag_indian = Tag.objects.create(user=self.user, name='Indian')
        payload = {
            'title': 'Pongal',
            'time_minutes': 60,
            'price': Decimal('4.50'),
            'description': 'Indian food description',
            'link': 'http://www.updated.com/recipe.pdf',
            'tags': [{'name': 'Indian'}, {'name': 'Breakfast'}]
        }

        # Send POST request
        res = self.client.post(RECIPES_URL, payload, format='json')
        # Check response
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)

        # Retrieve user's recipes
        recipes = Recipe.objects.filter(user=self.user)
        # Ensure only 1 recipe
        self.assertEqual(recipes.count(), 1)
        # Access recipe
        recipe = recipes[0]
        # Ensure only 2 tags are available ie. no duplicate created
        self.assertEqual(recipe.tags.count(), 2)
        # Ensure Indian tag is present in recipes
        self.assertIn(tag_indian, recipe.tags.all())

        # Iterate through tags in payload
        for tag in payload['tags']:
            # Check for matching tag in first recipe to see if exists
            exists = recipe.tags.filter(
                name=tag['name'], user=self.user).exists()
            self.assertTrue(exists)

    def test_create_tag_on_update(self):
        """Test creating a new tag on update recipe."""
        recipe = create_recipe(user=self.user)

        # Build payload and url
        payload = {'tags': [{'name': 'Lunch'}]}
        url = detail_url(recipe.id)

        # Send PATCH request
        res = self.client.patch(url, payload, format='json')
        # Check response
        self.assertEqual(res.status_code, status.HTTP_200_OK)

        # Search for newly created tag through recipe
        new_tag = Tag.objects.get(user=self.user, name='Lunch')
        # Assert that all list items in tags
        self.assertIn(new_tag, recipe.tags.all())

    def test_update_recipe_assign_tag(self):
        """Test assigning an existing tag when updating a recipe."""
        # Create new tag
        tag_breakfast = Tag.objects.create(user=self.user, name="Breakfast")

        # Create new recipe and add the new tag
        recipe = create_recipe(user=self.user)
        recipe.tags.add(tag_breakfast)

        # Create new tag lunch
        tag_lunch = Tag.objects.create(user=self.user, name="Lunch")

        # Prepare for recipe update API call
        payload = {
            'tags': [{'name': 'Lunch'}]
        }
        url = detail_url(recipe.id)
        # Send PATCH to update recipe with new tags
        res = self.client.patch(url, payload, format='json')
        # Check response
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        # Check that only updated tag is within
        self.assertIn(tag_lunch, recipe.tags.all())
        self.assertNotIn(tag_breakfast, recipe.tags.all())

    def test_clear_recipe_tags(self):
        """Tests clearing a recipe's tags"""
        # Create new tag
        tag_breakfast = Tag.objects.create(user=self.user, name="Breakfast")

        # Create new recipe and add the new tag
        recipe = create_recipe(user=self.user)
        recipe.tags.add(tag_breakfast)

        # Prepare for recipe update API call
        payload = {
            'tags': []
        }
        url = detail_url(recipe.id)
        # Send PATCH to update recipe with new tags
        res = self.client.patch(url, payload, format='json')
        # Check response
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(recipe.tags.count(), 0)

    def test_create_recipe_with_new_ingredients(self):
        """Test creating recipe with new ingredients."""
        # Prepare for API call
        payload = {
            'title': 'Butter Chicken Curry',
            'time_minutes': 60,
            'price': Decimal('4.50'),
            'description': 'Indian food description',
            'link': 'http://www.updated.com/recipe.pdf',
            'tags': [{'name': 'Dinner'}],
            'ingredients': [{'name': 'Butter'}, {'name': 'Salt'}]
        }
        # Send POST request
        res = self.client.post(RECIPES_URL, payload, format='json')
        # Assert response Created
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)

        # Assert 1 recipe for user
        recipes = Recipe.objects.filter(user=self.user)
        self.assertEqual(recipes.count(), 1)

        # Assert 2 ingredients in recipe
        recipe = recipes[0]
        self.assertEqual(recipe.ingredients.count(), 2)
        # Iterate through payload ingredients to ensure present within recipe
        for ingredient in payload['ingredients']:
            exists = recipe.ingredients.filter(
                name=ingredient['name'], user=self.user).exists()
            self.assertTrue(exists)

    def test_create_recipe_with_existing_ingredient(self):
        """Test creating recipe with new ingredients"""
        ingredient = Ingredient.objects.create(user=self.user, name="Salt")
        # Prepare for API call
        payload = {
            'title': 'Butter Chicken Curry',
            'time_minutes': 60,
            'price': Decimal('4.50'),
            'description': 'Indian food description',
            'link': 'http://www.updated.com/recipe.pdf',
            'tags': [{'name': 'Dinner'}],
            'ingredients': [{'name': 'Butter'}, {'name': 'Salt'}]
        }
        # Send POST request
        res = self.client.post(RECIPES_URL, payload, format='json')
        # Assert response Created
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)

        # Assert 2 total ingredients for user
        ingredients = Ingredient.objects.filter(user=self.user)
        self.assertEqual(ingredients.count(), 2)

        # Assert 1 recipe for user
        recipes = Recipe.objects.filter(user=self.user)
        self.assertEqual(recipes.count(), 1)

        # Assert 2 ingredients in recipe
        recipe = recipes[0]
        self.assertEqual(recipe.ingredients.count(), 2)
        # Iterate through payload ingredients to ensure present within recipe
        for ingredient in payload['ingredients']:
            exists = recipe.ingredients.filter(
                name=ingredient['name'], user=self.user).exists()
            self.assertTrue(exists)

    def test_create_ingredient_on_update(self):
        """Test creating an ingredient in recipe update."""
        # create a new recipe
        recipe = create_recipe(user=self.user)

        # Prepare for API call
        payload = {
            'ingredients': [{'name': 'Beef'}]
        }
        url = detail_url(recipe.id)
        # Send PATCH request
        res = self.client.patch(url, payload, format='json')
        # Assert proper response
        self.assertEqual(res.status_code, status.HTTP_200_OK)

        new_ingredient = Ingredient.objects.get(
            user=self.user, name='Beef')
        # Assert new ingredient in ingredients list of recipe
        self.assertIn(new_ingredient, recipe.ingredients.all())

    def test_update_recipe_assign_ingredient(self):
        """Test assigning an existing ingredient."""
        # Create recipe, ingredient, then add ingredient to recipe
        recipe = create_recipe(user=self.user)
        ingredient1 = Ingredient.objects.create(
            user=self.user, name='Coriander')
        recipe.ingredients.add(ingredient1)

        # Create a second ingredient
        ingredient2 = Ingredient.objects.create(
            user=self.user, name='Chili')

        # Prepare payload to replace ingredients
        payload = {
            'ingredients': [{'name': 'Chili'}]
        }
        url = detail_url(recipe.id)
        # Send PATCH request
        res = self.client.patch(url, payload, format='json')
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        # Assert that ingredient 2 has replaced ingredient 1
        self.assertIn(ingredient2, recipe.ingredients.all())
        self.assertNotIn(ingredient1, recipe.ingredients.all())

    def test_clear_recipe_ingredients(self):
        """Test clearing a recipe's ingredients."""
        # Create recipe, ingredient, then add ingredient to recipe
        recipe = create_recipe(user=self.user)
        ingredient1 = Ingredient.objects.create(
            user=self.user, name='Coriander')
        recipe.ingredients.add(ingredient1)

        # Prepare payload to replace ingredients
        payload = {
            'ingredients': []
        }
        url = detail_url(recipe.id)
        # Send PATCH request
        res = self.client.patch(url, payload, format='json')
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        # Assert that there are no ingredients in recipe
        self.assertEqual(recipe.ingredients.count(), 0)
