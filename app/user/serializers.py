"""
Serializers for the user API view.
"""
from django.contrib.auth import get_user_model

from rest_framework import serializers

# Converts JSON to Python object

# Use base class for creating serializer


class UserSerializer(serializers.ModelSerializer):
    """Serializer for the user object."""

    # Meta tells Django what model and fields to pass to serializer
    class Meta:
        model = get_user_model()
        # fields to be created or set by user
        fields = ['email', 'password', 'name']
        # Additional options: set password unreadable with a min length
        extra_kwargs = {'password': {'write_only': True, 'min_length': 5}}

    # Allows overriding of serializers base creation method.
    # Called once data is validated by conditions above
    def create(self, validated_data):
        """Create and return user with encrypted password."""
        return get_user_model().objects.create_user(**validated_data)
