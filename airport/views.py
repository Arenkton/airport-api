from rest_framework import mixins, viewsets
from rest_framework.permissions import IsAuthenticated

from airport.models import (
    Airport,
    Route,
    AirplaneType,
    Airplane,
    Crew,
    Flight,
    Order,
)
from airport.serializers import (
    AirportSerializer,
    RouteSerializer,
    RouteDetailSerializer,
    AirplaneTypeSerializer,
    AirplaneSerializer,
    AirplaneDetailSerializer,
    CrewSerializer,
    FlightSerializer,
    FlightDetailSerializer,
    OrderSerializer,
)


class AirportViewSet(viewsets.ModelViewSet):
    queryset = Airport.objects.all()
    serializer_class = AirportSerializer


class RouteViewSet(viewsets.ModelViewSet):
    queryset = Route.objects.all()
    serializer_class = RouteSerializer

    def get_serializer_class(self):
        if self.action in ("list", "retrieve"):
            return RouteDetailSerializer

        return RouteSerializer


class AirplaneViewSet(viewsets.ModelViewSet):
    queryset = Airplane.objects.all()
    serializer_class = AirplaneSerializer

    def get_serializer_class(self):
        if self.action in ("list", "retrieve"):
            return AirplaneDetailSerializer

        return AirplaneSerializer


class AirplaneTypeViewSet(viewsets.ModelViewSet):
    queryset = AirplaneType.objects.all()
    serializer_class = AirplaneTypeSerializer


    def get_serializer_class(self):
        if self.action in ("list", "retrieve"):
            return AirplaneDetailSerializer

        return AirplaneSerializer


class CrewViewSet(viewsets.ModelViewSet):
    queryset = Crew.objects.all()
    serializer_class = CrewSerializer


class FlightViewSet(viewsets.ModelViewSet):
    queryset = Flight.objects.select_related(
        "route__source",
        "route__destination",
        "airplane__airplane_type",
    ).prefetch_related("crew")

    serializer_class = FlightSerializer

    def get_queryset(self):
        queryset = self.queryset.all()

        source = self.request.query_params.get("source")
        destination = self.request.query_params.get("destination")
        date = self.request.query_params.get("date")

        if source:
            queryset = queryset.filter(route__source_id=source)

        if destination:
            queryset = queryset.filter(route__destination_id=destination)

        if date:
            queryset = queryset.filter(departure_time__date=date)

        return queryset

    def get_serializer_class(self):
        if self.action in ("list", "retrieve"):
            return FlightDetailSerializer

        return FlightSerializer


class OrderViewSet(
    mixins.CreateModelMixin,
    mixins.ListModelMixin,
    mixins.RetrieveModelMixin,
    viewsets.GenericViewSet,
):
    serializer_class = OrderSerializer
    permission_classes = (IsAuthenticated,)

    def get_queryset(self):
        return Order.objects.filter(
            user=self.request.user
        ).prefetch_related("tickets")
