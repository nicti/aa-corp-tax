import logging
from collections import defaultdict

from django.contrib.auth.decorators import login_required, permission_required
from django.shortcuts import render
from django.views import View

from corptax.models import CorpTaxOwed, CorpTaxSettings

logger = logging.getLogger(__name__)


@login_required
@permission_required("corptax.basic_access")
def index(request):
    raw_data = CorpTaxOwed.objects.all()  # TODO filter based on what they are allowed to see?
    data = [[item.corp.corporation_name, item.month.strftime('%b, %Y'), item.isk_owed, item.paid] for item in raw_data]
    return render(request, "corptax/index.html", context={'corp_tax_data': data})


@login_required
@permission_required("corptax.admin_access")
def admin(request):
    return 'Nothing yet'


class SettingsView(View):

    permission_required = 'corptax.admin_access'

    def get(self, request):
        raw_data = CorpTaxSettings.objects.all()
        data = [[item.corp.corporation_name, str(item.taxed_at * 100), item.taxed] for item in raw_data]
        return render(request, "corptax/admin.html", context={'corp_tax_data': data})

    def post(self, request):
        post_data = request.POST
        logger.info(post_data)
        return self.get(request)

    def _cleanup_post_data(self, post_data: dict):
        """
        Convert POST data where keys are in form key1.key2.key3 into nested structures
        """
        rv = defaultdict(dict)
        for key, value in post_data.items():
            keys = key.split('.')  # TODO need to account for corps with . in the name...
            if len(keys) == 1:
                continue
            rv[keys[0]][keys[1]] = value
        return rv
