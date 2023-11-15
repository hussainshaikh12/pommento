from django.db import IntegrityError
from django.shortcuts import get_object_or_404, render
from django.views.decorators.http import require_GET
from .utils import get_client_ip, pnagea_services

@require_GET
def index_view(request):
    return render(request, "pages/index.html")

from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.http.response import HttpResponse, JsonResponse
from django.shortcuts import redirect, render
from django.views.decorators.cache import never_cache
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_GET, require_http_methods, require_POST
from .models import *
from .forms import SiteForm, CommetForm

from pommento.billing.models import StripeCustomer

@require_http_methods(["GET", "POST"])
@login_required
def site_list_view(request):
    context = {
        "current_tab": "site",
        "sites": Site.objects.filter(user=request.user)
    }

    form = SiteForm(
        request.POST or None,
        initial={
            "title": None,
        },
    )
    context["form"] = form

    if request.method == "POST":
        if form.is_valid():
            title = form.cleaned_data["title"]
            stripe_customer = len(StripeCustomer.objects.filter(user=request.user.id))
            site_count = len(Site.objects.filter(user=request.user))
            if site_count == 0:
                site = Site.objects.create(user=request.user,title=title)
            elif site_count and stripe_customer:
                site = Site.objects.create(user=request.user,title=title)
            else:
                context['billing_error'] = 'Switch to pro membership to create more than one site' 
            return render(request, "core/pages/index.html", context)

    return render(request, "core/pages/index.html", context)

@require_http_methods(["GET", "POST"])
@login_required
def comment_list_view(request, id):
    site = get_object_or_404(Site, id=id, user=request.user)
    page = Page.objects.filter(site=site)
    context = {
        "current_tab": "site",
        "comments": Comment.objects.filter(page__in=page)
    }
    
    return render(request, "core/pages/comments.html", context)

@require_http_methods(["GET"])
@login_required
def comment_status(request, id, status):
    comment = get_object_or_404(Comment, id=id)
    page = Page.objects.get(id = comment.page.id)
    site = Site.objects.get(page=page)
    if site.user == request.user:
        if status == 'accept':
            comment.status = True
            comment.save()
        if status == 'delete':
            comment.delete()
        return redirect('pommento-core:comment-list', id=site.id)
    return redirect("pommento-core:site-list")

from django.views.decorators.clickjacking import xframe_options_exempt
from django.utils.decorators import method_decorator



@require_http_methods(["GET", "POST"])
@csrf_exempt
def comment_widget(request):
    context = {}
    form = CommetForm(
        request.POST or None
    )
    context["form"] = form
    
    if request.method == "POST":
        page_id = request.POST.get("page_id")
        if form.is_valid():
            name = form.cleaned_data["name"]
            email = form.cleaned_data["email"]
            comment = form.cleaned_data["comment"]

            page = Page.objects.get(slug=page_id)
            ip = get_client_ip(request)
            new_comment = Comment.objects.create(name=name, email=email, body=comment, ip=ip, page=page)  
            pnagea_services(new_comment)
            comments = Comment.objects.filter(page = page.id, status=True)
            context["comments"] = comments
            return render(request, "core/partials/comment-list.html", context)
        return render(request, "core/partials/comment-list.html", context)
            
    site_id = request.GET.get("site_id", None)
    page_slug = request.GET.get("page_id", None)
    site = get_object_or_404(Site, id=site_id)
    request.session['site_id'] = site_id
    request.session['page_id'] = page_slug
    page,created = Page.objects.get_or_create(slug=page_slug, site=site)
    context['page_id'] = page.slug
    comments = Comment.objects.filter(page = page.id, status=True)
    context["comments"] = comments
    return render(request, "core/pages/comment_widget.html", context)