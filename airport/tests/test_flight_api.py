from datetime import datetime, timezone

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


class FlightApiTests(APITestCase):
    def setUp(self):
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

        self.reverse_route = Route.objects.create(
            source=self.destination,
            destination=self.source,
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
            departure_time=datetime(
                2026, 10, 1, 10, 0,
                tzinfo=timezone.utc,
            ),
            arrival_time=datetime(
                2026, 10, 1, 11, 0,
                tzinfo=timezone.utc,
            ),
        )

        self.other_flight = Flight.objects.create(
            route=self.reverse_route,
            airplane=self.airplane,
            departure_time=datetime(
                2026, 10, 2, 10, 0,
                tzinfo=timezone.utc,
            ),
            arrival_time=datetime(
                2026, 10, 2, 11, 0,
                tzinfo=timezone.utc,
            ),
        )

        self.list_url = reverse("flight-list")
    def test_filter_flights_by_source(self):
        response = self.client.get(
            self.list_url,
            {"source": self.source.id},
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )

        self.assertEqual(len(response.data), 1)

        self.assertEqual(
            response.data[0]["id"],
            self.flight.id,
        )
    def test_filter_flights_by_destination(self):
        response = self.client.get(
            self.list_url,
            {"destination": self.source.id},
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )

        self.assertEqual(len(response.data), 1)

        self.assertEqual(
            response.data[0]["id"],
            self.other_flight.id,
        )
    def test_filter_flights_by_date(self):
        response = self.client.get(
            self.list_url,
            {"date": "2026-10-01"},
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )

        self.assertEqual(len(response.data), 1)

        self.assertEqual(
            response.data[0]["id"],
            self.flight.id,
        )
    def test_available_seats_count(self):
        user = get_user_model().objects.create_user(
            username="test_user",
            password="TestPassword123!",
        )

        order = Order.objects.create(user=user)

        Ticket.objects.create(
            order=order,
            flight=self.flight,
            row=5,
            seat=3,
        )

        url = reverse(
            "flight-detail",
            args=[self.flight.id],
        )

        response = self.client.get(url)

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )

        self.assertEqual(
            response.data["available_seats"],
            179,
        )
