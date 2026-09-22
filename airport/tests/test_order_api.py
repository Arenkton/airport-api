from django.contrib.auth import get_user_model
from django.urls import reverse

from rest_framework import status
from rest_framework.test import APITestCase

from airport.models import (
    Airport,
    Route,
    AirplaneType,
    Airplane,
    Flight,
    Order,
    Ticket,
)


class OrderApiTests(APITestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_user(
            username="test_user",
            password="TestPassword123!",
        )

        self.other_user = get_user_model().objects.create_user(
            username="other_user",
            password="TestPassword123!",
        )

        self.source = Airport.objects.create(
            name="Krakow Airport",
            closest_big_city="Krakow",
        )

        self.destination = Airport.objects.create(
            name="Warsaw Chopin Airport",
            closest_big_city="Warsaw",
        )

        self.route = Route.objects.create(
            source=self.source,
            destination=self.destination,
            distance=295,
        )

        self.airplane_type = AirplaneType.objects.create(
            name="Boeing",
        )

        self.airplane = Airplane.objects.create(
            name="Boeing 737",
            rows=30,
            seats_in_row=6,
            airplane_type=self.airplane_type,
        )

        self.flight = Flight.objects.create(
            route=self.route,
            airplane=self.airplane,
            departure_time="2026-10-01T10:00:00Z",
            arrival_time="2026-10-01T11:00:00Z",
        )

        self.order_url = reverse("order-list")

    def test_user_can_create_order(self):
        self.client.force_authenticate(user=self.user)

        payload = {
            "tickets": [
                {
                    "row": 5,
                    "seat": 3,
                    "flight": self.flight.id,
                },
                {
                    "row": 5,
                    "seat": 4,
                    "flight": self.flight.id,
                },
            ]
        }

        response = self.client.post(
            self.order_url,
            payload,
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_201_CREATED,
        )

        self.assertEqual(Order.objects.count(), 1)
        self.assertEqual(Ticket.objects.count(), 2)

        order = Order.objects.first()

        self.assertEqual(order.user, self.user)
        self.assertEqual(order.tickets.count(), 2)

    def get_queryset(self):
        return Order.objects.filter(
            user=self.request.user
        ).prefetch_related("tickets")

    def test_user_cannot_access_other_users_order(self):
        other_order = Order.objects.create(
            user=self.other_user,
        )

        self.client.force_authenticate(user=self.user)

        url = reverse(
            "order-detail",
            args=[other_order.id],
        )

        response = self.client.get(url)

        self.assertEqual(
            response.status_code,
            status.HTTP_404_NOT_FOUND,
        )

    def test_unauthenticated_user_cannot_create_order(self):
        payload = {
            "tickets": [
                {
                    "row": 5,
                    "seat": 3,
                    "flight": self.flight.id,
                }
            ]
        }

        response = self.client.post(
            self.order_url,
            payload,
            format="json",
        )

        self.assertIn(
            response.status_code,
            (
                status.HTTP_401_UNAUTHORIZED,
                status.HTTP_403_FORBIDDEN,
            ),
        )

        self.assertEqual(Order.objects.count(), 0)
        self.assertEqual(Ticket.objects.count(), 0)
