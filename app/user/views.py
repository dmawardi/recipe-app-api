"""
Views for the user API.
"""
from rest_framework import generics, authentication, permissions
from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.settings import api_settings
from user.serializers import (UserSerializer, AuthTokenSerializer)

# Create your views here.

# Create API view handles a HTTP Post request for creating objects


class CreateUserView(generics.CreateAPIView):
    """Create a new user in the system."""
    # set serializer for CreateAPIView of Users to use custom serializer
    # Model associated is defined in serializer
    serializer_class = UserSerializer

# Using Obtain auth token view provided by Django rest framework


class CreateTokenView(ObtainAuthToken):
    """Create a new auth token for user."""
    # customize to use our custom serializer (switch from username to email)
    serializer_class = AuthTokenSerializer
    # Allows for browsable API from Django Rest framework UI
    renderer_class = api_settings.DEFAULT_RENDERER_CLASSES


class ManageUserView(generics.RetrieveUpdateAPIView):
    """Manage the authenticated user."""
    # customize to use our custom serializer (switch from username to email)
    serializer_class = UserSerializer
    # set auth class to token auth
    authentication_class = [authentication.TokenAuthentication]
    # Determines if user can do action
    permission_classes = [permissions.IsAuthenticated]

    # Override default get object
    # get object for the HTTP GET request
    def get_object(self):
        """Retrieve and return the authenticated user."""
        # The user will be attached to request object
        return self.request.user
