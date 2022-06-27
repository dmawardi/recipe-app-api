"""
    Serializers for Recipe API
"""

from rest_framework import serializers

from core.models import Recipe


class RecipeSerializer(serializers.ModelSerializer):
    """Serializer for recipes."""

    class Meta:
        model = Recipe
        fields = ['id', 'title', 'time_minutes', 'price', 'link']
        read_only_fields = ['id']

# Build recipe detail serializer based off of Recipe Serializer


class RecipeDetailSerializer(RecipeSerializer):
    """Serializer for recipe detail"""
    class Meta(RecipeSerializer.Meta):
        # Add fields from above but add description
        fields = RecipeSerializer.Meta.fields + ['description']
