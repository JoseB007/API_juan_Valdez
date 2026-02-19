from django.urls import path

from app.api.views.apellido_views import ApellidoView
from app.api.views.compartir_views import CompartirView


urlpatterns = [
    path("apellido/", ApellidoView.as_view(), name="apellido"),
    path("apellido/<str:apellido>/", ApellidoView.as_view(), name="apellido_poll"),
    path("compartir/", CompartirView.as_view(), name="compartir"),
]