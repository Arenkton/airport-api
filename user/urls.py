from django.urls import path

from user.views import UserCreateView, CreateTokenView


urlpatterns = [
    path(
        "register/",
        UserCreateView.as_view(),
        name="register",
    ),
    path(
        "token/",
        CreateTokenView.as_view(),
        name="token",
    ),
]
