from django.contrib import admin
from pommento.billing.models import StripeCustomer

admin.site.register(StripeCustomer)
