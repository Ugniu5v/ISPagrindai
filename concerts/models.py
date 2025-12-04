from django.db import models
from users.models import User

class Vieta(models.Model):
    pavadinimas = models.TextField()
    adresas = models.TextField()
    miestas = models.TextField()
    salis = models.TextField()
    platuma = models.FloatField(default=0)
    ilguma = models.FloatField(default=0)
    laiko_zona = models.TextField()

    def __str__(self):
        return self.pavadinimas


class Koncertas(models.Model):
    class Zanras(models.TextChoices):
        # DB value | Display label
        POPMUZIKA = "popmuzika", "Pop muzika"
        ROKAS = "rokas", "Rokas"
        METALAS = "metalas", "Metalas"
        DZIASAS = "dziasas", "Džiazas"
        BLIUZAS = "bliuzas", "Bliuzas"
        KLASIKA = "klasika", "Klasika"
        ELEKTRONIKA = "elektronika", "Elektronika"
        REPAS = "repas", "Repas"
        RNB = "rnb", "R&B"
        KANTRI = "kantri", "Kantri"
        FOLK = "folk", "Folk"
        REGIS = "regis", "Regis"
        ALTERNATYVA = "alternatyva", "Alternatyva"
        DISCO = "disco", "Disco"
        DANCE = "dance", "Dance"
        AMBIENT = "ambient", "Ambient"
        EKSPERIMENTINE = "eksperimentine", "Eksperimentinė"
        INSTRUMENTINE = "instrumentine", "Instrumentinė"
        OPERA = "opera", "Opera"
        PASAULIO_MUZIKA = "pasaulio_muzika", "Pasaulio muzika"
        TREP = "trep", "Trep"
        TECHNO = "techno", "Techno"
        HOUSE = "house", "House"

    pavadinimas = models.TextField()
    pradzios_data = models.DateField(blank=True, null=True)
    pabaigos_data = models.DateField(blank=True, null=True)
    bilietu_url = models.TextField()
    aprasymas = models.TextField()
    sukurimo_data = models.DateField(blank=True, null=True)
    atnaujinimo_data = models.DateField(blank=True, null=True)
    yra_atsauktas = models.BooleanField(default=False)
    zmoniu_talpa = models.IntegerField()
    zanras = models.CharField(choices=Zanras.choices, default=Zanras.POPMUZIKA, max_length=255)
    yra_viesas = models.BooleanField(default=True)
    rekomendacijos_ivertis = models.FloatField(default=0)
    vieta = models.ForeignKey(Vieta, on_delete=models.SET_NULL, null=True, blank=True,related_name="koncertai",)

    def __str__(self):
        return self.pavadinimas


class KoncertoDalyvis(models.Model):

    class DalyvavimoBusena(models.TextChoices):
        DALYVAUJA = "dalyvauja", "Dalyvauja"
        DOMINA = "domina", "Domina"
        ISSAUGOTA = "isaugota", "Isaugota"

    vartotojas = models.ForeignKey(User, on_delete=models.CASCADE, related_name="koncertu_dalyviai")
    koncertas = models.ForeignKey(Koncertas, on_delete=models.CASCADE, related_name="dalyviai")
    dalyvavimo_busena = models.CharField(choices=DalyvavimoBusena.choices, max_length=50, default=DalyvavimoBusena.DOMINA)

    class Meta:
        unique_together = ["vartotojas", "koncertas"]

    def __str__(self):
        return f"{self.vartotojas.username} - {self.koncertas.pavadinimas} ({self.dalyvavimo_busena})"
