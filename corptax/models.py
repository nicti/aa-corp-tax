from django.db import models

from allianceauth.corputils.models import EveCorporationInfo


class CorpTaxRate(models.Model):
    """Represents the daily tax rate for each corp we are aware of"""

    corp = models.ForeignKey(EveCorporationInfo, on_delete=models.DO_NOTHING)
    tax_rate = models.FloatField()
    date = models.DateField()

    objects = models.Manager()

    def __str__(self):
        return f'{self.corp.corporation_name} had a tax rate of {self.tax_rate} on {self.date}'

    class Meta:
        unique_together = (("corp", "date"),)


class CorpTaxOwed(models.Model):
    """The amount of tax a corp owes alliance based on income and their tax rate"""
    corp = models.ForeignKey(EveCorporationInfo, on_delete=models.DO_NOTHING)
    month = models.DateField()
    isk_owed = models.DecimalField(max_digits=15, decimal_places=2)  # TODO is this the best?
    paid = models.BooleanField(default=False)
    last_updated = models.DateTimeField(auto_now=True)

    objects = models.Manager()

    def __str__(self):
        return f'{self.corp.corporation_name} owes {self.isk_owed} for month of {self.month}. Paid? {self.paid}'

    class Meta:
        unique_together = (("corp", "month"),)


class CorpTaxSettings(models.Model):
    """The settings to represent which corp are taxed at which amount"""
    corp = models.ForeignKey(EveCorporationInfo, on_delete=models.DO_NOTHING, primary_key=True)
    taxed_at = models.FloatField(null=True)
    taxed = models.BooleanField()
    last_updated = models.DateTimeField(auto_now=True)

    objects = models.Manager()

    def __str__(self):
        if self.taxed:
            return f'{self.corp.corporation_name} taxed at {self.taxed_at}'
        return f'{self.corp.corporation_name} is not taxed'


class Corptax(models.Model):
    """Meta model for app permissions"""

    class Meta:
        managed = False
        default_permissions = ()
        permissions = (
            ("basic_access", "Can access this app"),
            ("admin_access", "Can edit tax rates and monitor all taxes")
        )
