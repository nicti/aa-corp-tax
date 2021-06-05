from django.db import models

from allianceauth.corputils.models import EveCorporationInfo


class CorpTaxRate(models.Model):
    """Represents the daily tax rate for each corp we are aware of"""

    corp = models.ForeignKey(EveCorporationInfo, on_delete=models.DO_NOTHING)
    tax_rate = models.FloatField()
    date = models.DateField()

    class Meta:
        unique_together = (("corp", "date"),)


class CorpTaxOwed(models.Model):
    """The amount of tax a corp owes alliance based on income and their tax rate"""
    corp = models.ForeignKey(EveCorporationInfo, on_delete=models.DO_NOTHING)
    month = models.IntegerField()
    isk_owed = models.DecimalField(max_digits=15, decimal_places=2)  # TODO is this the best?
    paid = models.BooleanField(default=False)
    last_updated = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = (("corp", "month"),)


class CorpTaxSettings(models.Model):
    """The settings to represent which corp are taxed at which amount"""
    corp = models.ForeignKey(EveCorporationInfo, on_delete=models.DO_NOTHING, primary_key=True)
    tax_rate = models.FloatField(null=True)
    taxed = models.BooleanField()
    last_updated = models.DateTimeField(auto_now=True)


class Corptax(models.Model):
    """Meta model for app permissions"""

    class Meta:
        managed = False
        default_permissions = ()
        permissions = (
            ("basic_access", "Can access this app"),
            ("admin_access", "Can edit tax rates and monitor all taxes")
        )
