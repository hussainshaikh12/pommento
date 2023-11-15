import stripe
from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.http.response import HttpResponse, JsonResponse
from django.shortcuts import redirect, render
from django.views.decorators.cache import never_cache
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_GET, require_http_methods, require_POST
from pommento.billing.forms import UpdateBillingInformationForm
from pommento.model_loaders import get_stripe_customer_model
from .models import StripeCustomer
from django.contrib.auth import get_user_model

@login_required
def success(request):
    return render(request, "billing/pages/success.html")

@login_required
def cancel(request):
    return render(request, "billing/pages/cancel.html")

@never_cache
@require_http_methods(["GET", "POST"])
@login_required
def billing_settings_view(request):
    context = {
        "current_tab": "billing",
    }

    try:
        # Retrieve the subscription & product
        stripe_customer = StripeCustomer.objects.get(user=request.user.id)
        stripe.api_key = settings.STRIPE_SECRET_KEY
        subscription = stripe.Subscription.retrieve(stripe_customer.stripe_subscription_id)
        product = stripe.Product.retrieve(subscription.plan.product)
        # current_period_end = stripe.Subscription.retrieve(stripe_customer.stripe_subscription_id)

        # Feel free to fetch any additional data from "subscription" or "product"
        # https://stripe.com/docs/api/subscriptions/object
        # https://stripe.com/docs/api/products/object

        print ("subscription " + subscription.id)
        context['subscription'] = subscription
        context['product'] = product
        return render(request, "billing/pages/billing_settings.html", context)
    except StripeCustomer.DoesNotExist:
        print(request.user.id)
        print("Does not exist")
        return render(request, "billing/pages/billing_settings.html", context)


@csrf_exempt
@require_GET
@login_required
def create_subscribe_checkout_view(request):
    domain_url = request.build_absolute_uri("/")[:-1]
    success = request.GET.get("success", None)
    cancel = request.GET.get("cancel", None)
    stripe.api_key = settings.STRIPE_SECRET_KEY

    try:
        checkout_session = stripe.checkout.Session.create(
            client_reference_id = request.user.id if request.user.is_authenticated else None,
            success_url=domain_url +success+ "success?session_id={CHECKOUT_SESSION_ID}",
            cancel_url=domain_url +cancel+"cancel",
            payment_method_types= ["card"],
            mode = "subscription",
            line_items=[
                {
                    "price": settings.STRIPE_PRICE_ID,
                }
            ]
        )

        return JsonResponse({"checkout_session_id": checkout_session["id"]})
    except Exception as e:
        return JsonResponse({"error": str(e)})


@require_POST
@login_required
def cancel_subscription_view(request):
    success = request.GET.get("success", None)

    stripe.api_key = settings.STRIPE_SECRET_KEY

    stripe.Subscription.modify(
        request.user.stripe_customer.stripe_subscription_id,
        cancel_at_period_end=True,
    )

    return redirect(success + "?" + "subcription_cancel_success=true")


@require_POST
@login_required
def reactivate_subscription_view(request):
    """
    Reactivate canceled subscription which hasn't reached
    the end of the billing period.

    Note: If the cancellation has already been processed and the
    subscription is no longer active, a new subscription is
    needed for the customer. For this case, use the `create_subscribe_checkout_view`
    endpoint.
    """
    success = request.GET.get("success", None)

    stripe.api_key = settings.STRIPE_SECRET_KEY

    stripe_customer = request.user.stripe_customer

    subscription = stripe.Subscription.retrieve(stripe_customer.stripe_subscription_id)

    if subscription.status.canceled:
        new_subscription = stripe.Subscription.create(
            customer=stripe_customer.stripe_customer_id,
            items=[{"price": settings.STRIPE_PRICE_ID}],
            automatic_tax={"enabled": True},
        )
        stripe_customer.stripe_subscription_id = new_subscription.id
        stripe_customer.save(update_fields=["stripe_subscription_id"])
    else:
        stripe.Subscription.modify(
            subscription.id,
            cancel_at_period_end=False,
            proration_behavior="create_prorations",
            items=[
                {
                    "id": subscription["items"]["data"][0].id,
                    "price": settings.STRIPE_PRICE_ID,
                }
            ],
        )

    return redirect(success + "?" + "subcription_reactivated_success=true")


from django.contrib.auth.models import User
from django.http.response import JsonResponse, HttpResponse
from .models import StripeCustomer


@csrf_exempt
def stripe_webhook_view(request):
    stripe.api_key = settings.STRIPE_SECRET_KEY
    endpoint_secret = settings.STRIPE_WEBHOOK_SECRET
    payload = request.body
    sig_header = request.META["HTTP_STRIPE_SIGNATURE"]
    event = None

    try:
        event = stripe.Webhook.construct_event(
            payload, sig_header, endpoint_secret
        )
    except ValueError as e:
        # Invalid payload
        return HttpResponse(status=400)
    except stripe.error.SignatureVerificationError as e:
        # Invalid signature
        return HttpResponse(status=400)

    # handle the checkout.session.completed event
    if event["type"] == "checkout.session.completed":
        session = event["data"]["object"]

        # Fetch all the required data from session
        client_reference_id = session.get('client_reference_id')
        stripe_customer_id = session.get('customer')
        stripe_subscription_id = session.get("subscription")
        User = get_user_model()
        user = User.objects.get(id=client_reference_id)
        StripeCustomer.objects.create(
            user=user,
            stripe_customer_id=stripe_customer_id,
            stripe_subscription_id=stripe_subscription_id,
        )
        print(user.name + " just subscrbed.")

    return HttpResponse(status=200)