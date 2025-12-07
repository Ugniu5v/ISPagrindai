from django.db import models
from users.models import User
from django.utils import timezone


class Grojarastis(models.Model):
    pavadinimas = models.CharField(max_length=255)
    aprasymas = models.TextField(blank=True, null=True)
    yra_viesas = models.BooleanField(default=True)
    sukurimo_data = models.DateTimeField(default=timezone.now)
    atnaujinimo_data = models.DateTimeField(auto_now=True)
    savininkas = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="grojarasciai"  # Naudotojas.grojarasciai
    )

    def __str__(self):
        return self.pavadinimas

    class Meta:
        verbose_name = "Grojarastis"
        verbose_name_plural = "Grojarasčiai"
        ordering = ['-sukurimo_data']


class GrojarastisDaina(models.Model):
    grojarastis = models.ForeignKey(
        Grojarastis,
        on_delete=models.CASCADE,
        related_name="dainos"        # Grojarastis.dainos
    )
    dainos_pavadinimas = models.CharField(max_length=255, blank=True)
    atlikėjo_vardas = models.CharField(max_length=255, blank=True)
    eilės_nr = models.PositiveIntegerField(default=0)

    class Meta:
        verbose_name = "GrojarastisDaina"
        verbose_name_plural = "GrojarasčioDainos"
        ordering = ['eilės_nr']
        unique_together = ['grojarastis', 'eilės_nr']

    def __str__(self):
        return f"{self.eilės_nr}. {self.dainos_pavadinimas or 'Be pavadinimo'}"


class GrojarascioVertinimas(models.Model):
    grojarastis = models.ForeignKey(
        Grojarastis,
        on_delete=models.CASCADE,
        related_name="vertinimai"
    )
    naudotojas = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="grojarasciu_vertinimai"
    )
    ivertinimas = models.FloatField()
    ivertinimo_data = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "GrojarascioVertinimas"
        verbose_name_plural = "GrojarasčioVertinimai"
        unique_together = ['grojarastis', 'naudotojas']

    def __str__(self):
        return f"{self.naudotojas} → {self.grojarastis}: {self.ivertinimas}"