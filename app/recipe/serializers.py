"""
    Serializers for Recipe API
"""

from core.models import Tag
from rest_framework import serializers

from core.models import (Recipe, Tag, Ingredient)


class IngredientSerializer(serializers.ModelSerializer):
    """Serializer for ingredients."""

    class Meta:
        model = Ingredient
        fields = ['id', 'name']
        read_only_fields = ['id']


class TagSerializer(serializers.ModelSerializer):
    """Serializer for tags."""
    class Meta:
        model = Tag
        fields = ['id', 'name']
        read_only_fields = ['id']


class RecipeSerializer(serializers.ModelSerializer):
    """Serializer for recipes."""
    # many means a list. Required means nullable
    tags = TagSerializer(many=True, required=False)

    class Meta:
        model = Recipe
        fields = ['id', 'title', 'time_minutes', 'price', 'link', 'tags']
        read_only_fields = ['id']

    def _get_or_create_tags(self, tags, recipe):
        """Handle getting or creating tags as needed."""
        # Grab the authenticated user from context
        # Note: Passed by view when using as serializer class
        # through self.context.request property
        auth_user = self.context['request'].user
        # Iterate through extracted tags list
        for tag in tags:
            # If doesn't exist, create, else return existing
            tag_obj, created = Tag.objects.get_or_create(
                user=auth_user,
                **tag,
            )
            # add to recipe's tag property
            recipe.tags.add(tag_obj)

    def create(self, validated_data):
        """Create a recipe."""
        # pop the tags property of validated data. Default to empty list
        tags = validated_data.pop('tags', [])
        # Create new recipe using validated data
        recipe = Recipe.objects.create(**validated_data)

        self._get_or_create_tags(tags, recipe)
        return recipe

    # with update you have the instance as well
    def update(self, instance, validated_data):
        """Update a recipe"""
        # Remove tags from validated data and store
        tags = validated_data.pop('tags', None)

        # If tags detected
        if tags is not None:
            # Clear current tags on instance
            instance.tags.clear()
            # Replace with new ones or existing ones
            self._get_or_create_tags(tags, instance)

        # Iterate through remaining validated items
        for attr, value in validated_data.items():
            # Set the attributes within the instance variable
            setattr(instance, attr, value)

        # Save all changes
        instance.save()
        return instance


# Build recipe detail serializer based off of Recipe Serializer


class RecipeDetailSerializer(RecipeSerializer):
    """Serializer for recipe detail"""
    class Meta(RecipeSerializer.Meta):
        # Add fields from above but add description
        fields = RecipeSerializer.Meta.fields + ['description']
