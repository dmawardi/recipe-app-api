"""
URL mappings for the Recipe app.
"""

from django.urls import (path, include)
# Import router. Used with view to produce routes automatically
from rest_framework.routers import DefaultRouter

from recipe import views

# setup router
router = DefaultRouter()
# Register viewset with router
router.register('recipes', views.RecipeViewSet)

app_name = 'recipe'

# Set url patters to correspond to router
urlpatterns = [
    # include allows including urls by router
    path('', include(router.urls))
]
