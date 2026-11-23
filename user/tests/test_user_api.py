from django.contrib.auth import get_user_model
from django.urls import reverse

from rest_framework import status
from rest_framework.test import APITestCase


class UserApiTests(APITestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_user(
            username="test_user",
            email="test@example.com",
            password="TestPassword123!",
        )

        self.register_url = reverse("register")
        self.token_url = reverse("token")
        self.me_url = reverse("me")

    def test_create_user(self):
        payload = {
            "username": "new_user",
            "email": "new@example.com",
            "first_name": "John",
            "last_name": "Smith",
            "password": "NewPassword123!",
        }

        response = self.client.post(
            self.register_url,
            payload,
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_201_CREATED,
        )

        user = get_user_model().objects.get(
            username=payload["username"],
        )

        self.assertTrue(
            user.check_password(payload["password"])
        )

        self.assertNotIn("password", response.data)

    def test_create_token(self):
        payload = {
            "username": "test_user",
            "password": "TestPassword123!",
        }

        response = self.client.post(
            self.token_url,
            payload,
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )

        self.assertIn("token", response.data)

    def test_create_token_with_invalid_credentials(self):
        payload = {
            "username": "test_user",
            "password": "WrongPassword123!",
        }

        response = self.client.post(
            self.token_url,
            payload,
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_400_BAD_REQUEST,
        )

        self.assertNotIn("token", response.data)

    def test_authentication_required_for_profile(self):
        response = self.client.get(self.me_url)

        self.assertIn(
            response.status_code,
            (
                status.HTTP_401_UNAUTHORIZED,
                status.HTTP_403_FORBIDDEN,
            ),
        )

    def test_retrieve_user_profile(self):
        token_response = self.client.post(
            self.token_url,
            {
                "username": "test_user",
                "password": "TestPassword123!",
            },
            format="json",
        )

        self.assertEqual(
            token_response.status_code,
            status.HTTP_200_OK,
        )

        token = token_response.data["token"]

        self.client.credentials(
            HTTP_AUTHORIZATION=f"Token {token}"
        )

        response = self.client.get(self.me_url)

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )

        self.assertEqual(
            response.data["username"],
            self.user.username,
        )

        self.assertEqual(
            response.data["email"],
            self.user.email,
        )

        self.assertNotIn("password", response.data)

    def test_update_user_profile(self):
        self.client.force_authenticate(user=self.user)

        payload = {
            "first_name": "Michael",
            "last_name": "Brown",
            "email": "updated@example.com",
        }

        response = self.client.patch(
            self.me_url,
            payload,
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )

        self.user.refresh_from_db()

        self.assertEqual(
            self.user.first_name,
            payload["first_name"],
        )

        self.assertEqual(
            self.user.last_name,
            payload["last_name"],
        )

        self.assertEqual(
            self.user.email,
            payload["email"],
        )

    def update(self, instance, validated_data):
        password = validated_data.pop("password", None)

        user = super().update(instance, validated_data)

        if password:
            user.set_password(password)
            user.save()

        return user

    def test_update_user_password(self):
        self.client.force_authenticate(user=self.user)

        payload = {
            "password": "NewSecurePassword123!",
        }

        response = self.client.patch(
            self.me_url,
            payload,
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )

        self.user.refresh_from_db()

        self.assertTrue(
            self.user.check_password(payload["password"])
        )

        self.assertFalse(
            self.user.check_password("TestPassword123!")
        )

        self.assertNotIn("password", response.data)

    def test_authentication_after_password_change(self):
        self.client.force_authenticate(user=self.user)

        self.client.patch(
            self.me_url,
            {
                "password": "NewSecurePassword123!",
            },
            format="json",
        )

        self.client.force_authenticate(user=None)

        old_password_response = self.client.post(
            self.token_url,
            {
                "username": "test_user",
                "password": "TestPassword123!",
            },
            format="json",
        )

        self.assertEqual(
            old_password_response.status_code,
            status.HTTP_400_BAD_REQUEST,
        )

        new_password_response = self.client.post(
            self.token_url,
            {
                "username": "test_user",
                "password": "NewSecurePassword123!",
            },
            format="json",
        )

        self.assertEqual(
            new_password_response.status_code,
            status.HTTP_200_OK,
        )

        self.assertIn(
            "token",
            new_password_response.data,
        )
