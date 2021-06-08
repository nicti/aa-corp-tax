from django.contrib.auth.decorators import login_required, permission_required
from django.shortcuts import render

from corptax.models import CorpTaxOwed


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


@login_required
@permission_required("corptax.admin_access")
def settings(request):
    return 'Nothing yet'
