from datetime import datetime

import requests
from celery import shared_task

from allianceauth.services.hooks import get_extension_logger
from allianceauth.corputils.models import EveCorporationInfo
from corptax.models import CorpTaxRate, CorpTaxSettings, CorpTaxOwed

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
            settings = CorpTaxSettings(corp=corp, tax_rate=None, taxed=False)
            settings.save()
            logger.info(f'Successfully created entry in CorpTaxSettings for {corp_name}')

# TODO write task to periodically recalculate tax owed
