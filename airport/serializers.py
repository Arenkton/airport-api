from rest_framework import serializers

from django.db import IntegrityError, transaction
from django.utils import timezone

from drf_spectacular.utils import extend_schema_field
from drf_spectacular.types import OpenApiTypes

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


class AirportSerializer(serializers.ModelSerializer):
    class Meta:
        model = Airport
        fields = (
            "id",
            "name",
            "closest_big_city",
        )


class RouteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Route
        fields = (
            "id",
            "source",
            "destination",
            "distance",
        )

    def validate(self, attrs):
        source = attrs.get(
            "source",
            getattr(self.instance, "source", None),
        )
        destination = attrs.get(
            "destination",
            getattr(self.instance, "destination", None),
        )

        if source == destination:
            raise serializers.ValidationError(
                {
                    "destination": (
                        "Source and destination airports "
                        "must be different."
                    )
                }
            )

        return attrs


class RouteDetailSerializer(RouteSerializer):
    source = AirportSerializer(read_only=True)
    destination = AirportSerializer(read_only=True)


class AirplaneTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = AirplaneType
        fields = (
            "id",
            "name",
        )


class AirplaneSerializer(serializers.ModelSerializer):
    class Meta:
        model = Airplane
        fields = (
            "id",
            "name",
            "rows",
            "seats_in_row",
            "airplane_type",
        )


class AirplaneDetailSerializer(AirplaneSerializer):
    airplane_type = AirplaneTypeSerializer(read_only=True)


class CrewSerializer(serializers.ModelSerializer):
    class Meta:
        model = Crew
        fields = (
            "id",
            "first_name",
            "last_name",
        )


class FlightSerializer(serializers.ModelSerializer):
    class Meta:
        model = Flight
        fields = (
            "id",
            "route",
            "airplane",
            "crew",
            "departure_time",
            "arrival_time",
        )

    def validate(self, attrs):
        departure_time = attrs.get(
            "departure_time",
            getattr(self.instance, "departure_time", None),
        )
        arrival_time = attrs.get(
            "arrival_time",
            getattr(self.instance, "arrival_time", None),
        )

        if (
            departure_time is not None
            and arrival_time is not None
            and arrival_time <= departure_time
        ):
            raise serializers.ValidationError(
                {
                    "arrival_time": (
                        "Arrival time must be later "
                        "than departure time."
                    )
                }
            )

        return attrs


class FlightDetailSerializer(FlightSerializer):
    route = RouteDetailSerializer(read_only=True)
    airplane = AirplaneDetailSerializer(read_only=True)
    crew = CrewSerializer(many=True, read_only=True)

    available_seats = serializers.SerializerMethodField()

    class Meta(FlightSerializer.Meta):
        fields = FlightSerializer.Meta.fields + (
            "available_seats",
        )

    @extend_schema_field(OpenApiTypes.INT)
    def get_available_seats(self, obj):
        total_seats = (
            obj.airplane.rows * obj.airplane.seats_in_row
        )

        return total_seats - obj.booked_seats


class FlightFilterSerializer(serializers.Serializer):
    source = serializers.IntegerField(
        min_value=1,
        required=False,
    )
    destination = serializers.IntegerField(
        min_value=1,
        required=False,
    )
    date = serializers.DateField(required=False)


class TicketSerializer(serializers.ModelSerializer):
    row = serializers.IntegerField(min_value=1)
    seat = serializers.IntegerField(min_value=1)

    class Meta:
        model = Ticket
        fields = (
            "id",
            "row",
            "seat",
            "flight",
        )
        read_only_fields = ("id",)

    def validate(self, attrs):
        flight = attrs["flight"]
        row = attrs["row"]
        seat = attrs["seat"]

        airplane = flight.airplane

        if row > airplane.rows:
            raise serializers.ValidationError(
                {
                    "row": (
                        f"Row must be between 1 and "
                        f"{airplane.rows}."
                    )
                }
            )

        if seat > airplane.seats_in_row:
            raise serializers.ValidationError(
                {
                    "seat": (
                        f"Seat must be between 1 and "
                        f"{airplane.seats_in_row}."
                    )
                }
            )
        if Ticket.objects.filter(
                flight=flight,
                row=row,
                seat=seat,
        ).exists():
            raise serializers.ValidationError(
                {
                    "seat": "This seat is already booked for this flight."
                }
            )
        if flight.departure_time <= timezone.now():
            raise serializers.ValidationError(
                {"flight": "Cannot book a flight that has already departed."}
            )
        return attrs


class OrderSerializer(serializers.ModelSerializer):
    tickets = TicketSerializer(many=True, allow_empty=False)

    class Meta:
        model = Order
        fields = (
            "id",
            "created_at",
            "tickets",
        )
        read_only_fields = ("id", "created_at")

    def validate_tickets(self, tickets):
        booked_seats = set()

        for ticket in tickets:
            seat_key = (
                ticket["flight"].pk,
                ticket["row"],
                ticket["seat"],
            )

            if seat_key in booked_seats:
                raise serializers.ValidationError(
                    "Duplicate seats in the same order are not allowed."
                )

            booked_seats.add(seat_key)

        return tickets

    def create(self, validated_data):
        tickets_data = validated_data.pop("tickets")

        try:
            with transaction.atomic():
                order = Order.objects.create(
                    user=self.context["request"].user,
                )

                for ticket_data in tickets_data:
                    Ticket.objects.create(
                        order=order,
                        **ticket_data,
                    )

                return order

        except IntegrityError:
            raise serializers.ValidationError(
                {
                    "tickets": (
                        "One or more selected seats are already booked."
                    )
                }
            )


class OrderFlightSerializer(serializers.ModelSerializer):
    source = serializers.CharField(
        source="route.source.name",
        read_only=True,
    )
    destination = serializers.CharField(
        source="route.destination.name",
        read_only=True,
    )

    class Meta:
        model = Flight
        fields = (
            "source",
            "destination",
            "departure_time",
        )


class TicketReadSerializer(serializers.ModelSerializer):
    flight_details = OrderFlightSerializer(
        source="flight",
        read_only=True,
    )

    class Meta:
        model = Ticket
        fields = (
            "id",
            "row",
            "seat",
            "flight",
            "flight_details",
        )


class OrderReadSerializer(serializers.ModelSerializer):
    tickets = TicketReadSerializer(
        many=True,
        read_only=True,
    )

    class Meta:
        model = Order
        fields = (
            "id",
            "created_at",
            "tickets",
        )
