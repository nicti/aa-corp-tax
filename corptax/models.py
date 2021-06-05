from django.db import models

from allianceauth.corputils.models import EveCorporationInfo


class CorpTaxRate(models.Model):

    corp = models.ForeignKey(EveCorporationInfo, on_delete=models.DO_NOTHING)
    tax_rate = models.FloatField()
    date = models.DateField()

    class Meta:
        unique_together = (("corp", "date"),)


class CorpTaxOwed(models.Model):

    corp = models.ForeignKey(EveCorporationInfo, on_delete=models.DO_NOTHING)
    month = models.IntegerField()
    isk_owed = models.DecimalField(max_digits=15, decimal_places=2)  # TODO is this the best?
    paid = models.BooleanField(default=False)

    class Meta:
        unique_together = (("corp", "month"),)


class Corptax(models.Model):
    """Meta model for app permissions"""

    class Meta:
        managed = False
        default_permissions = ()
        permissions = (
            ("basic_access", "Can access this app"),
            ("admin_access", "Can edit tax rates and monitor all taxes")
        )
