"""
URL mappings for the User API.
"""
from django.urls import path
from user import views

# allows for reverse referencing with (app_name:pathname)
app_name = 'user'

urlpatterns = [
    # createuserview connects rest_framework to Django User view
    path("create/", views.CreateUserView.as_view(), name='create'),
    path("token/", views.CreateTokenView.as_view(), name='token'),
    path("me/", views.ManageUserView.as_view(), name='me')

]
