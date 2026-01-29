from django.urls import path

from app.api.views.views import ApellidoView


urlpatterns = [
    path("apellido/", ApellidoView.as_view(), name="apellido"),
]