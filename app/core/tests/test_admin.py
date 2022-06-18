"""Tests for Django admin customizations."""

from django.test import TestCase, Client
from django.contrib.auth import get_user_model
from django.urls import reverse


class AdminSiteTests(TestCase):
    """Tests for Django admin."""

    def setUp(self) -> None:
        """Create user and client to prepare for tests."""
        self.client = Client()
        # create a super user using our custom method
        self.admin_user = get_user_model().objects.create_superuser(
            email="admin@example.com", password="testpass123")
        # Allows us to force authentication for user
        # (all requests through client will be as this user)
        self.client.force_login(self.admin_user)
        self.user = get_user_model().objects.create_user(
            email="user@example.com", password="testpass123")

    def test_users_list(self):
        """Tests that users are listed on the page"""
        # build url to test using reverse function and Django location string
        url = reverse("admin:core_user_changelist")
        # Obtain response using client
        res = self.client.get(url)

        self.assertContains(res, self.user.name)
        self.assertContains(res, self.user.email)
