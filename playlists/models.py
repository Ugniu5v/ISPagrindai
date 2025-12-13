from django.db import models
from users.models import User
from django.utils import timezone
from music.models import Daina


class Grojarastis(models.Model):
    pavadinimas = models.CharField(max_length=255)
    aprasymas = models.TextField(blank=True, null=True)
    yra_viesas = models.BooleanField(default=True)
    sukurimo_data = models.DateTimeField(default=timezone.now)
    atnaujinimo_data = models.DateTimeField(auto_now=True)
    savininkas = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="grojarasciai"
    )

    def __str__(self):
        return self.pavadinimas

    class Meta:
        verbose_name = "Grojarastis"
        verbose_name_plural = "Grojarasciai"
        ordering = ['-sukurimo_data']


class GrojarastisDaina(models.Model):
    grojarastis = models.ForeignKey(
        Grojarastis,
        on_delete=models.CASCADE,
        related_name="dainos"
    )
    daina = models.ForeignKey(
        Daina,
        on_delete=models.CASCADE,
        related_name="playlist_entries"
    )
    eiles_nr = models.PositiveIntegerField()
    prideta_data = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("grojarastis", "eiles_nr")
        ordering = ["eiles_nr"]


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
        verbose_name_plural = "GrojarascioVertinimai"
        unique_together = ['grojarastis', 'naudotojas']

    def __str__(self):
        return f"{self.naudotojas} → {self.grojarastis}: {self.ivertinimas}"