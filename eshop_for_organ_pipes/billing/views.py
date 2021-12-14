from django.conf import settings
from django.http import JsonResponse, HttpResponse
from django.shortcuts import render, redirect
from django.utils.http import is_safe_url

import stripe

from billing.models import BillingProfile, Card
from carts.models import Cart

from orders.models import Order

stripe.api_key = settings.STRIPE_SECRET_API_KEY
STRIPE_PUB_KEY = settings.STRIPE_PUB_KEY


def payment_method_view(request):

    billing_profile, billing_profile_created = BillingProfile.objects.new_or_get(request=request)

    if not billing_profile:
        return redirect("/cart")

    next_url = None
    next_jump = request.GET.get('next')

    if is_safe_url(next_jump, request.get_host()):
        next_url = next_jump

    return render(request, 'billing/payment-method.html', {
        "publish_key": STRIPE_PUB_KEY,
        "next_url": next_url
    })


def payment_method_create_view(request):
    print(request.method == "POST", request.is_ajax())
    if request.method == "POST" and request.is_ajax():
        billing_profile, billing_profile_created = BillingProfile.objects.new_or_get(request=request)

        if not billing_profile:
            return HttpResponse({"message": "User not found"}, status=404)

        token = request.POST.get("token")

        if token is None:
            return HttpResponse({"message": "There is no Token"}, status=404)

        new_card_obj = Card.objects.add_new_using_token(billing_profile=billing_profile, token=token)
        cart, _ = Cart.objects.new_or_get(request)
        order, _ = Order.objects.new_or_get(billing_profile=billing_profile, cart=cart)
        order.payment_type = 'card'
        order.save()

        return JsonResponse({"message": "Done"})
    return HttpResponse("error", status=401)
