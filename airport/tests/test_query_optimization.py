from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model

from rest_framework import status
from rest_framework.test import APIClient
from datetime import datetime, timezone

from django.db import connection
from django.test.utils import CaptureQueriesContext

from airport.models import (
    Airport,
    Route,
    AirplaneType,
    Airplane,
    Crew,
    Flight,
    Order,
    Ticket,
)

class RouteQueryOptimizationTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.url = reverse("route-list")

        source = Airport.objects.create(
            name="Krakow Airport",
            closest_big_city="Krakow",
        )

        for index in range(5):
            destination = Airport.objects.create(
                name=f"Airport {index}",
                closest_big_city=f"City {index}",
            )

            Route.objects.create(
                source=source,
                destination=destination,
                distance=100 + index,
            )

    def test_routes_list_query_count(self):
        with self.assertNumQueries(2):
            response = self.client.get(self.url)

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )

        self.assertEqual(
            response.data["count"],
            5,
        )

        self.assertEqual(
            len(response.data["results"]),
            5,
        )


class AirplaneQueryOptimizationTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.url = reverse("airplane-list")

        airplane_type = AirplaneType.objects.create(
            name="Boeing",
        )

        for index in range(5):
            Airplane.objects.create(
                name=f"Boeing 737-{index}",
                rows=30,
                seats_in_row=6,
                airplane_type=airplane_type,
            )

    def test_airplanes_list_query_count(self):
        with self.assertNumQueries(2):
            response = self.client.get(self.url)

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )

        self.assertEqual(
            response.data["count"],
            5,
        )

        self.assertEqual(
            len(response.data["results"]),
            5,
        )


class FlightQueryOptimizationTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.url = reverse("flight-list")

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

        self.crew_member = Crew.objects.create(
            first_name="John",
            last_name="Smith",
        )

    def create_flight(self, day):
        flight = Flight.objects.create(
            route=self.route,
            airplane=self.airplane,
            departure_time=datetime(
                2026, 10, day, 10, 0,
                tzinfo=timezone.utc,
            ),
            arrival_time=datetime(
                2026, 10, day, 12, 0,
                tzinfo=timezone.utc,
            ),
        )

        flight.crew.add(self.crew_member)

        return flight

    def test_flight_list_query_count(self):
        self.create_flight(day=1)

        with CaptureQueriesContext(connection) as first_queries:
            first_response = self.client.get(self.url)

        self.assertEqual(
            first_response.status_code,
            status.HTTP_200_OK,
        )

        self.assertEqual(
            first_response.data["count"],
            1,
        )

        for day in range(2, 6):
            self.create_flight(day=day)

        with CaptureQueriesContext(connection) as second_queries:
            second_response = self.client.get(self.url)

        self.assertEqual(
            second_response.status_code,
            status.HTTP_200_OK,
        )

        self.assertEqual(
            second_response.data["count"],
            5,
        )

        self.assertEqual(
            len(second_response.data["results"]),
            5,
        )

        self.assertEqual(
            len(first_queries),
            len(second_queries),
        )


class OrderQueryOptimizationTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.url = reverse("order-list")

        self.user = get_user_model().objects.create_user(
            username="test_user",
            password="TestPassword123!",
        )

        self.client.force_authenticate(user=self.user)

        source = Airport.objects.create(
            name="Krakow Airport",
            closest_big_city="Krakow",
        )

        destination = Airport.objects.create(
            name="Warsaw Chopin Airport",
            closest_big_city="Warsaw",
        )

        route = Route.objects.create(
            source=source,
            destination=destination,
            distance=295,
        )

        airplane_type = AirplaneType.objects.create(
            name="Boeing",
        )

        airplane = Airplane.objects.create(
            name="Boeing 737",
            rows=30,
            seats_in_row=6,
            airplane_type=airplane_type,
        )

        self.flight = Flight.objects.create(
            route=route,
            airplane=airplane,
            departure_time=datetime(
                2026, 10, 1, 10, 0,
                tzinfo=timezone.utc,
            ),
            arrival_time=datetime(
                2026, 10, 1, 12, 0,
                tzinfo=timezone.utc,
            ),
        )

    def create_order(self, row):
        order = Order.objects.create(
            user=self.user,
        )

        for seat in (1, 2):
            Ticket.objects.create(
                order=order,
                flight=self.flight,
                row=row,
                seat=seat,
            )

        return order

    def test_order_list_query_count(self):
        self.create_order(row=1)

        with CaptureQueriesContext(connection) as first_queries:
            first_response = self.client.get(self.url)

        self.assertEqual(
            first_response.status_code,
            status.HTTP_200_OK,
        )

        self.assertEqual(
            first_response.data["count"],
            1,
        )

        self.assertEqual(
            len(first_response.data["results"][0]["tickets"]),
            2,
        )

        for row in range(2, 6):
            self.create_order(row=row)

        with CaptureQueriesContext(connection) as second_queries:
            second_response = self.client.get(self.url)

        self.assertEqual(
            second_response.status_code,
            status.HTTP_200_OK,
        )

        self.assertEqual(
            second_response.data["count"],
            5,
        )

        for order in second_response.data["results"]:
            self.assertEqual(
                len(order["tickets"]),
                2,
            )

        self.assertEqual(
            len(first_queries),
            len(second_queries),
        )
