from django.apps import apps


def get_stripe_customer_model():
    return apps.get_model("pommento_billing.StripeCustomer")
