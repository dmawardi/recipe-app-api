"""
Serializers for the user API view.
"""
from django.contrib.auth import (
    get_user_model,
    authenticate
)
from django.utils.translation import gettext as _

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


class AuthTokenSerializer(serializers.Serializer):
    """Serializer for the user auth token."""
    email = serializers.EmailField()
    password = serializers.CharField(
        style={'input-type': 'password'}, trim_whitespace=False)

    # called at validation stage of view
    # When data posted to view, it is sent to serializer to call validate

    def validate(self, attrs):
        """Validate and authenticate the user."""
        # Obtain email and password from user input
        email = attrs.get('email')
        password = attrs.get('password')

        # Authenticate returns user if found or nothing if not found
        user = authenticate(
            # Accepts request context
            request=self.context.get('request'),
            # uesrname
            username=email,
            # password
            password=password
        )

        if not user:
            msg = _('Unable to authenticate with provided credentials.')
            # Standard way to raise error with serializer
            # translates to HTTP 400 bad request with our message
            raise serializers.ValidationError(msg, code='authorization')

        # if above condition not met, set user in the view
        attrs['user'] = user
        return attrs
