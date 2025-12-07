from django.db import models


class Daina(models.Model):
    class Zanras(models.TextChoices):
        POPMUZIKA = "popmuzika", "Pop muzika"
        ROKAS = "rokas", "Rokas"
        METALAS = "metalas", "Metalas"
        DZIASAS = "dziasas", "Dziazas"
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
        EKSPERIMENTINE = "eksperimentine", "Eksperimentine"
        INSTRUMENTINE = "instrumentine", "Instrumentine"
        OPERA = "opera", "Opera"
        PASAULIO_MUZIKA = "pasaulio_muzika", "Pasaulio muzika"
        TREP = "trep", "Trep"
        TECHNO = "techno", "Techno"
        HOUSE = "house", "House"

    pavadinimas = models.CharField(max_length=255)
    trukme_sekundes = models.IntegerField()
    zanras = models.CharField(choices=Zanras.choices, max_length=50, default=Zanras.POPMUZIKA)
    isleidimo_data = models.DateField(blank=True, null=True)
    paleidimu_kiekis = models.IntegerField(default=0)
    zodziai = models.TextField(blank=True)
    failas_url = models.TextField()
    virselis_url = models.TextField(blank=True)
    aprasymas = models.TextField(blank=True)
    ikelimo_data = models.DateField(auto_now_add=True)
    yra_viesa = models.BooleanField(default=True)

    def __str__(self):
        return self.pavadinimas


class DainosKlausymas(models.Model):
    daina = models.ForeignKey(Daina, on_delete=models.CASCADE, related_name="klausymai")
    trukme_procentais = models.FloatField()
    klausymo_data = models.DateField(auto_now_add=True)

    def __str__(self):
        return f"{self.daina} ({self.klausymo_data})"


class DainosVertinimas(models.Model):
    daina = models.ForeignKey(Daina, on_delete=models.CASCADE, related_name="vertinimai")
    ivertinimas = models.FloatField()
    ivertinimo_data = models.DateField(auto_now_add=True)

    def __str__(self):
        return f"{self.daina} - {self.ivertinimas}"
