from django.test import TestCase
from django.urls import reverse

from rest_framework import status
from rest_framework.test import APIClient

from airport.models import (
    Airport,
    Route,
    AirplaneType,
    Airplane,
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
