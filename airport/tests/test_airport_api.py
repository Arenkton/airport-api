from django.contrib.auth import get_user_model
from django.urls import reverse

from rest_framework import status
from rest_framework.test import APITestCase

from airport.models import Airport


class PublicAirportApiTests(APITestCase):
    def setUp(self):
        self.list_url = reverse("airport-list")

    def test_unauthenticated_user_can_list_airports(self):
        Airport.objects.create(
            name="Krakow Airport",
            closest_big_city="Krakow",
        )

        response = self.client.get(self.list_url)

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )
        self.assertEqual(response.data["count"], 1)

        self.assertEqual(
            len(response.data["results"]),
            1,
        )

    def test_unauthenticated_user_cannot_create_airport(self):
        payload = {
            "name": "Warsaw Chopin Airport",
            "closest_big_city": "Warsaw",
        }

        response = self.client.post(
            self.list_url,
            payload,
        )

        self.assertIn(
            response.status_code,
            (
                status.HTTP_401_UNAUTHORIZED,
                status.HTTP_403_FORBIDDEN,
            ),
        )

        self.assertFalse(
            Airport.objects.filter(
                name="Warsaw Chopin Airport",
            ).exists()
        )


class PrivateAirportApiTests(APITestCase):
    def setUp(self):
        self.list_url = reverse("airport-list")

        self.user = get_user_model().objects.create_user(
            username="regular_user",
            password="TestPassword123!",
        )

        self.admin_user = get_user_model().objects.create_superuser(
            username="admin_user",
            email="admin@example.com",
            password="TestPassword123!",
        )

    def test_regular_user_cannot_create_airport(self):
        self.client.force_authenticate(user=self.user)

        payload = {
            "name": "Warsaw Chopin Airport",
            "closest_big_city": "Warsaw",
        }

        response = self.client.post(
            self.list_url,
            payload,
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_403_FORBIDDEN,
        )

        self.assertEqual(Airport.objects.count(), 0)

    def test_admin_user_can_create_airport(self):
        self.client.force_authenticate(
            user=self.admin_user
        )

        payload = {
            "name": "Warsaw Chopin Airport",
            "closest_big_city": "Warsaw",
        }

        response = self.client.post(
            self.list_url,
            payload,
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_201_CREATED,
        )

        self.assertTrue(
            Airport.objects.filter(
                name="Warsaw Chopin Airport",
            ).exists()
        )
