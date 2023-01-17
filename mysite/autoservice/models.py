from django.db import models


# Create your models here.
class AutomobilioModelis(models.Model):
    marke = models.CharField(verbose_name="Markė", max_length=100)
    modelis = models.CharField(verbose_name="Modelis", max_length=100)


class Automobilis(models.Model):
    valstybinis_nr = models.CharField(verbose_name="Valstybinis numeris", max_length=100)
    vin_kodas = models.CharField(verbose_name="VIN kodas", max_length=100)
    klientas = models.CharField(verbose_name="Klientas", max_length=100)
    automobilio_modelis = models.ForeignKey(to=AutomobilioModelis, on_delete=models.SET_NULL, null=True)


class Paslauga(models.Model):
    pavadinimas = models.CharField(verbose_name="Pavadinimas", max_length=100)
    kaina = models.FloatField(verbose_name="Kaina")


class Uzsakymas(models.Model):
    data = models.DateField(verbose_name="Data", auto_now_add=True)
    automobilis = models.ForeignKey(to="Automobilis", on_delete=models.CASCADE)


class UzsakymoEilute(models.Model):
    uzsakymas = models.ForeignKey(to="Uzsakymas", on_delete=models.CASCADE)
    paslauga = models.ForeignKey(to="Paslauga", on_delete=models.SET_NULL, null=True)
    kiekis = models.IntegerField(verbose_name="Kiekis")
