from django.conf import settings
from django.contrib.auth import authenticate, get_user_model, login, logout
from django.contrib.auth.decorators import login_required
from django.db import IntegrityError
from django.shortcuts import redirect, render
from django.views.decorators.cache import never_cache
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_GET, require_http_methods, require_POST
from pommento.auth.forms import (
    LoginForm,
    RegisterForm,
    UpdatePasswordForm,
    UpdateUserForm,
)
from pommento.auth.utils import validate_google_id_token
from pommento.billing.utils import create_subscription_for_user

from django.core.exceptions import ObjectDoesNotExist
from pangea.config import PangeaConfig
from pangea.services import Audit


config = PangeaConfig(domain=settings.PANGEA_DOMAIN)
audit = Audit(settings.PANGEA_TOKEN, config=config)

@never_cache
@require_http_methods(["GET", "POST"])
@login_required
def account_settings_view(request):
    context = {
        "current_tab": "account",
    }

    form = UpdateUserForm(
        request.POST
        or {
            "name": request.user.name,
        },
        initial={
            "name": request.user.name,
        },
    )
    context["form"] = form

    if request.method == "POST":
        if form.is_valid():
            if form.has_changed():
                for attr in form.changed_data:
                    setattr(request.user, attr, form.cleaned_data[attr])
                request.user.save()

            return redirect("pommento-auth:account-settings")

    return render(request, "auth/pages/account_settings.html", context)


@never_cache
@require_GET
@login_required
def email_settings_view(request):
    context = {
        "current_tab": "email",
    }

    return render(request, "auth/pages/email_settings.html", context)


def security_settings_view(request):
    context = {
        "current_tab": "security",
    }

    form = UpdatePasswordForm(request.POST or None)
    context["form"] = form

    if request.method == "POST":
        if form.is_valid():
            if request.user.check_password(form.cleaned_data["password"]):
                request.user.set_password(form.cleaned_data["new_password"])
                request.user.save()

                return redirect("pommento-auth:security-settings")
            else:
                form.add_error(None, "Password incorrecto.")

    return render(request, "auth/pages/security_settings.html", context)


@never_cache
@require_http_methods(["GET", "POST"])
def login_view(request):
    context = {}

    form = LoginForm(request.POST or None)
    context["form"] = form

    if request.method == "POST":
        if form.is_valid():
            username=form.cleaned_data.get("email")
            
            try:
                exist =  get_user_model().objects.get(email=username)
                if exist and exist.google_id is None:
                    user = authenticate(
                        request,
                        username=form.cleaned_data.get("email", None),
                        password=form.cleaned_data.get("password", None),
                    )
                    if user is not None:
                        login(request, user)
                        audit.log("User: " +request.user.name+ " logged into the app")
                        return redirect("pommento-core:site-list")
                    else:
                        form.add_error(None, "Incorrect email address or password.")
                else:
                    form.add_error(
                        None,
                        "You registered using your Google Account. Please use Sign In with Google to sign in.",
                    )
            except ObjectDoesNotExist:
                form.add_error(
                    None,
                    "User not registered",
                )
                

    return render(request, "auth/pages/login.html", context)


@never_cache
@require_http_methods(["GET", "POST"])
def register_view(request):
    context = {}
    context["google_oauth_client_id"] = settings.GOOGLE_OAUTH_CLIENT_ID

    form = RegisterForm(request.POST or None)
    context["form"] = form

    if request.method == "POST":
        if form.is_valid():
            try:
                user = get_user_model().objects.create(
                    name=form.cleaned_data.get("name", None),
                    email=form.cleaned_data.get("email", None),
                )

                user.set_password(form.cleaned_data["password"])
                user.save()
                

                login(request, user)
                audit.log("User: " +request.user.name+ " Regiestered and logged into the app")
                return redirect("pommento-core:site-list")
            except IntegrityError as e:
                form.add_error(
                    None, "User Already exist"
                )

    return render(request, "auth/pages/register.html", context)


@never_cache
@login_required(redirect_field_name=None)
def logout_view(request):
    logout(request)
    return redirect("pommento-auth:login")


@require_POST
@csrf_exempt
def signin_with_google_view(request):
    next = request.POST.get("next", None)

    try:
        idinfo = validate_google_id_token(request)
    except Exception as e:
        if next is None:
            return redirect("pommento-auth:register")
        return redirect(next)

    user, created = get_user_model().objects.get_or_create(
        email=idinfo["email"],
    )

    if created:
        user.name = idinfo["name"]
        user.set_unusable_password()


    user.google_id = idinfo["sub"]
    user.save()

    login(request, user)
    audit.log("User: " +request.user.name+ " logged in using google into the app")
    return redirect("pommento-core:site-list")
