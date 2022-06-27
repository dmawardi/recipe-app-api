"""
Views for the Recipe APIs.
"""
from rest_framework import viewsets
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated

from core.models import Recipe
from recipe import serializers


class RecipeViewSet(viewsets.ModelViewSet):
    """View for manage recipe APIs."""
    # Set serializer to be detailed serializer as default
    serializer_class = serializers.RecipeDetailSerializer
    # Set model associated by setting queryset
    queryset = Recipe.objects.all()
    # Set support for token authentication
    authentication_classes = [TokenAuthentication]
    # Set so must by authenticated to access
    permission_classes = [IsAuthenticated]

    # Override default get query to only return logged in user
    def get_queryset(self):
        """Retrieve recipes for authenticated user."""
        # filter query set by current user
        # self.request.user contains the user data from authentication system
        return self.queryset.filter(user=self.request.user).order_by('-id')

    # Override default
    def get_serializer_class(self):
        """Return serializer class for request."""
        if self.action == 'list':
            return serializers.RecipeSerializer

        # Else return current class
        return self.serializer_class

    # Override default create
    # accepts second argument which is validated data from serializer
    def perform_create(self, serializer):
        """Create a new recipe"""
        # Save currently serialized data with additional argument user from authentication system
        serializer.save(user=self.request.user)
