from django.db import models


ORIGEN_DATOS = [
    ('REAL', 'Real'),
    ('IA', 'IA')
]

class Apellido(models.Model):
    apellido = models.CharField(max_length=30, unique=True)
    origen = models.CharField(max_length=4, choices=ORIGEN_DATOS, default='REAL')
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.apellido}"

    class Meta:
        db_table = "apellido"
        verbose_name = "Apellido"
        verbose_name_plural = "Apellidos"

    
class Departamento(models.Model):
    nombre = models.CharField(max_length=50, unique=True)

    def __str__(self):
        return self.nombre

    class Meta:
        db_table = "departamento"
        verbose_name = "Departamento"
        verbose_name_plural = "Departamentos"
        ordering = ["nombre"]


class DistribucionApellidoDepartamento(models.Model):
    apellido = models.ForeignKey(Apellido, on_delete=models.CASCADE, related_name="distribuciones")
    departamento = models.ForeignKey(Departamento, on_delete=models.CASCADE, related_name="apellido_distribuciones")
    porcentaje = models.DecimalField(max_digits=5, decimal_places=2)
    ranking = models.PositiveIntegerField()
    origen = models.CharField(max_length=4, choices=ORIGEN_DATOS, default='REAL')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.apellido} - {self.departamento} - ({self.porcentaje}%)"

    class Meta:
        db_table = "distribucion_apellido_departamento"
        verbose_name = "Distribucion Apellido"
        verbose_name_plural = "Distribuciones Apellidos"
        ordering = ["ranking"]


class Frases(models.Model):
    CATEGORIAS = [
        ('PERSONALIDAD', 'Personalidad'),
        ('SABOR', 'Sabor')
    ]
    categoria = models.CharField(max_length=15, choices=CATEGORIAS)
    frase = models.TextField()
    origen = models.CharField(max_length=4, choices=ORIGEN_DATOS, default='REAL')
    apellido = models.ForeignKey(Apellido, on_delete=models.CASCADE, related_name="frases")
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.categoria} - {self.frase[:30]}..."

    class Meta:
        db_table = "frases"
        verbose_name = "Frase"
        verbose_name_plural = "Frases"
        ordering = ["categoria"]

