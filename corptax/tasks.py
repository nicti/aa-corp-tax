from calendar import monthrange
from datetime import datetime, timedelta, date, timezone
from functools import lru_cache
from typing import Optional, Union

import requests
from django.db import models
from celery import shared_task

from allianceauth.services.hooks import get_extension_logger
from allianceauth.corputils.models import EveCorporationInfo
from corptax.models import CorpTaxRate, CorpTaxSettings, CorpTaxOwed
from corptools.models import CorporationWalletJournalEntry

logger = get_extension_logger(__name__)
CORP_URL = 'https://esi.evetech.net/latest/corporations/{corp_id}/?datasource=tranquility'


@shared_task
def update_tax_rate():
    today = datetime.today().date()
    for corp in EveCorporationInfo.objects.all():
        corp_name = corp.corporation_name
        corp_id = corp.corporation_id
        logger.info(f'Processing tax rate for {corp_name}')
        url = CORP_URL.format(corp_id=corp_id)
        response = requests.get(url)
        if response.status_code != 200:
            logger.error(f'Problem requesting corp info from CCP for corp {corp_id} {corp_name}')
        else:
            corp_data = response.json()
            tax_rate = corp_data.get('tax_rate')
            if tax_rate is None:
                logger.error(f'Problem with data returned by ccp for {corp_name}: {corp_data}')
                continue
            corp_tax_rate, created = CorpTaxRate.objects.update_or_create(corp=corp, date=today, defaults={'tax_rate': tax_rate})
            logger.info(f'Saved tax rate for {corp_name} on {today} as {tax_rate}')


@shared_task
def update_corps_in_corp_settings():
    """Update the corp list in CorpTaxSettings"""
    for corp in EveCorporationInfo.objects.all():
        settings = CorpTaxSettings.objects.filter(corp=corp)
        if not settings:
            corp_name = corp.corporation_name
            logger.info(f'Creating entry in CorpTaxSettings for {corp_name}')
            settings = CorpTaxSettings(corp=corp, taxed_at=None, taxed=False)
            settings.save()
            logger.info(f'Successfully created entry in CorpTaxSettings for {corp_name}')


@lru_cache
def _get_corp_tax_rate_for_day(corp: EveCorporationInfo, day: Union[datetime, date], strict: bool = False) -> float:
    """
    Returns the tax rate of the corp on this day. If `strict` is set to False and no tax rate is found for the given day
    then the nearest tax rate known will be used. If no tax rate is found, None is returned
    """
    corp_tax_rate = CorpTaxRate.objects.filter(corp=corp, date=day)
    if len(corp_tax_rate) == 1:
        return corp_tax_rate[0].tax_rate
    elif len(corp_tax_rate) > 1:
        msg = f'Multiple entries found for {corp.corporation_name} on {day}!'
        logger.error(msg)
        raise SystemError(msg)
    elif not strict:
        # Look for tax rate of nearest day
        closest_greater = CorpTaxRate.objects.filter(date__gt=day).order_by('date')
        closest_less = CorpTaxRate.objects.filter(date__lt=day).order_by('-date')

        closest_greater_diff = None
        closest_less_diff = None
        if len(closest_greater) > 0:
            closest_greater_diff = closest_greater[0].date - day
        if len(closest_less) > 0:
            closest_less_diff = day - closest_less[0].date

        if closest_greater_diff and closest_less_diff:
            # Take the closest date, if tied then take the lesser date
            return closest_greater[0].tax_rate if closest_greater_diff < closest_less_diff else closest_less[0].tax_rate
        elif closest_less_diff is None:
            return closest_greater[0].tax_rate
        elif closest_greater_diff is None:
            return closest_less[0].tax_rate
        else:
            logger.error(f'No tax rates found ever for {corp.corporation_name}')


@shared_task
def update_tax_owed(month: int, year: Optional[int] = None):
    _get_corp_tax_rate_for_day.cache_clear()  # Clear the cache so that DB updates are handled
    month = datetime(year=datetime.today().year if year is None else year, month=month, day=1, tzinfo=timezone.utc)
    end_of_month = month + timedelta(days=monthrange(month.year, month.month)[1])
    for corp_settings in CorpTaxSettings.objects.filter(taxed=True, taxed_at__isnull=False):
        logger.info(f'Processing tax owed for corp {corp_settings.corp.corporation_name}')
        corp_id = corp_settings.corp.corporation_id
        total_owed = 0
        for wallet_entry in CorporationWalletJournalEntry.objects.filter(
                tax_receiver_id=corp_id,
                ref_type='bounty_prizes',
                date__gte=month,
                date__lt=end_of_month
        ).order_by('date'):
            tax_rate = _get_corp_tax_rate_for_day(corp_settings.corp, wallet_entry.date.date())
            share_of_tax_owed_to_alliance = min(1.0, corp_settings.taxed_at/tax_rate)
            total_owed += float(wallet_entry.amount) * share_of_tax_owed_to_alliance

        corp_tax_owed, created = CorpTaxOwed.objects.update_or_create(corp=corp_settings.corp, month=month, defaults={'isk_owed': total_owed})
        logger.info(corp_tax_owed)


@shared_task
def update_tax_owed_current_month():
    now = datetime.now().date()
    current_month = now.month
    current_year = now.year
    update_tax_owed(current_month, current_year)
