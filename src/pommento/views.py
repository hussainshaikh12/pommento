from django.shortcuts import render
from django.views.decorators.http import require_GET
from django.contrib.auth.decorators import login_required

@require_GET
def index_view(request):
    return render(request, "pages/index.html")

