from django.conf.urls import url

from .views import (
        cart_home,
        cart_update,
        checkout_home,
        checkout_done_view,
        bank_payment,
        delete_shipping_and_billing
        )

urlpatterns = [
    url(r'^$', cart_home, name='home'),
    url(r'^checkout/$', checkout_home, name='checkout'),
    url(r'^checkout/bank_payment$', bank_payment, name='bank_payment'),
    url(r'^checkout/success/$', checkout_done_view, name='success'),
    url(r'^checkout/clear/$', delete_shipping_and_billing, name='clear'),
    url(r'^update/$', cart_update, name='update')
]
