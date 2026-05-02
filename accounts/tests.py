from django.contrib.auth import get_user_model
from django.test import TestCase
from rest_framework import status
from rest_framework.test import APIClient

User = get_user_model()


class RegistrationTests(TestCase):
    def setUp(self):
        self.client = APIClient()

    def test_consumer_registration(self):
        payload = {
            "email": "new@example.com",
            "username": "newuser",
            "password": "securepass123",
            "full_name": "New User",
        }
        response = self.client.post("/api/auth/register/", payload, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(response.data["success"])
        self.assertEqual(response.data["user"]["email"], "new@example.com")
        self.assertEqual(response.data["user"]["role"], User.Role.CONSUMER)
        self.assertTrue(User.objects.filter(email="new@example.com").exists())


class LoginTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(
            email="login@example.com",
            username="loginuser",
            password="goodpassword1",
            role=User.Role.CONSUMER,
        )

    def test_login_with_email_returns_tokens(self):
        response = self.client.post(
            "/api/auth/login/",
            {"email": self.user.email, "password": "goodpassword1"},
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("access", response.data)
        self.assertIn("refresh", response.data)
        self.assertIn("user", response.data)

    def test_blocked_user_cannot_login(self):
        self.user.is_blocked = True
        self.user.save(update_fields=["is_blocked"])
        response = self.client.post(
            "/api/auth/login/",
            {"email": self.user.email, "password": "goodpassword1"},
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
