"""
Views for the user API.
"""
from rest_framework import generics
from user.serializers import UserSerializer

# Create your views here.

# Create API view handles a HTTP Post request for creating objects


class CreateUserView(generics.CreateAPIView):
    """Create a new user in the system."""
    # set serializer for CreateAPIView of Users to use custom serializer
    # Model associated is defined in serializer
    serializer_class = UserSerializer
