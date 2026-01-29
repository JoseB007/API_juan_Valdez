from django.db import models


class Apellido(models.Model):
    apellido = models.CharField(max_length=30)
    ranking = models.IntegerField()
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.apellido} - {self.ranking}"

    class Meta:
        db_table = "apellido"
        verbose_name = "Apellido"
        verbose_name_plural = "Apellidos"
        ordering = ["ranking"]