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
        """Tests that users are listed on the page using name and email."""
        # build url to test using reverse function and Django location string
        url = reverse("admin:core_user_changelist")
        # Obtain response using client
        res = self.client.get(url)

        self.assertContains(res, self.user.name)
        self.assertContains(res, self.user.email)

    def test_edit_user_page(self):
        """Tests that the edit user page works."""
        # Use reverse to obtain url required (found by looking in browser)
        # sample admin url: core/user/:id/change
        # User
        url = reverse("admin:core_user_change", args=[self.user.id])
        # Obtain response using client
        res = self.client.get(url)

        self.assertEqual(res.status_code, 200)

    def test_create_user_page(self):
        """Test that the create user page works"""
        url = reverse("admin:core_user_add")
        res = self.client.get(url)

        self.assertEqual(res.status_code, 200)
