from django.contrib import admin

from app.domain.models.models import(
    Apellido,
    Departamento,
    DistribucionApellidoDepartamento,
    Frases
)

admin.site.register(Apellido)
admin.site.register(Departamento)
admin.site.register(DistribucionApellidoDepartamento)
admin.site.register(Frases)
