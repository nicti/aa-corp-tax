from django.contrib.auth.decorators import login_required, permission_required
from django.shortcuts import render


@login_required
@permission_required("corptax.basic_access")
def index(request):
    context = {"text": "Hello, World!"}
    return render(request, "corptax/index.html", context)


@login_required
@permission_required("corptax.admin_access")
def admin(request):
    return 'Nothing yet'
