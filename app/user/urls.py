"""
URL mappings for the User API.
"""
from django.urls import path
from user import views

app_name = 'user'

urlpatterns = [
    # createuserview connects rest_framework to Django User view
    path("create/", views.CreateUserView.as_view(), name='create')
]
