from django.http import JsonResponse
from django.shortcuts import render, redirect

from accounts.forms import LoginForm
from Addresses.models import Address
from Addresses.forms import AddressForm
from billing.models import BillingProfile
from orders.models import Order
from pipes_shop.models import Pipe
from .models import Cart

from django.conf import settings
import stripe

stripe.api_key = settings.STRIPE_SECRET_API_KEY
STRIPE_PUB_KEY = settings.STRIPE_PUB_KEY


def cart_detail_api(request):
    print("api call!")
    cart, _ = Cart.objects.new_or_get(request)
    request.session['cart_items'] = cart.pipes.count()
    pipes = [
        {
            "id": x.id,
            "name": x.name,
            "price": x.price,
            "registry": x.registry.name,
            "manual": x.manual.name,
            "note": x.note.name,
            "url": x.get_absolute_url()
        } for x in cart.pipes.all().order_by('name')
    ]
    cart_data = {
        "pipes": pipes,
        "subtotal": cart.sub_total,
        "total": cart.total
    }
    return JsonResponse(cart_data)


def cart_home(request):
    cart, _ = Cart.objects.new_or_get(request)
    request.session['cart_items'] = cart.pipes.count()
    request.session['cart_id'] = cart.id
    return render(request, "carts/home.html", {"cart": cart})


def bank_payment(request):
    cart, _ = Cart.objects.new_or_get(request)
    billing_profile, _ = BillingProfile.objects.new_or_get(request=request)
    order, _ = Order.objects.new_or_get(billing_profile=billing_profile, cart=cart)
    order.payment_type = 'bank'
    order.save()
    return redirect('cart:checkout')


def cart_update(request):
    prod_id = request.POST.get('pipe_id')

    if prod_id is None:
        print("User is playing tricky once again ....")
        return redirect("cart:home")

    pipe = Pipe.objects.get(id=prod_id)
    cart, _ = Cart.objects.new_or_get(request)
    product_added = True
    pipes = list(cart.pipes.all())
    if pipe in pipes:
        cart.pipes.remove(pipe)
        product_added = False
    else:
        cart.pipes.add(pipe)

    if request.is_ajax():
        print("Ajax!")
        json_data = {
            "added": product_added,
            "removed": not product_added,
            "cartItemCount": cart.pipes.count()
        }
        return JsonResponse(json_data)
    print("Redirecting .... cart_update")
    return redirect("cart:home")


def delete_shipping_and_billing(request):
    cart, cart_was_created = Cart.objects.new_or_get(request)
    billing_profile, _ = BillingProfile.objects.new_or_get(request=request)
    order, _ = Order.objects.new_or_get(billing_profile=billing_profile, cart=cart)

    if order is not None:

        if order.billing_address is not None:
            order.billing_address = None
            order.payment_type = None

        order.save()

    return redirect("cart:home")


def checkout_home(request):
    login_form = LoginForm()
    address_form = AddressForm()

    cart, cart_was_created = Cart.objects.new_or_get(request)

    if cart_was_created or cart.pipes.count() == 0:
        return redirect("cart:home")

    if cart.user is None:
        context = {
            "object": None,
            "billing_profile": None,
            "login_form": login_form,
            "address_form": None,
            "address_qs": None,
            "has_card": None,
            "publish_key": STRIPE_PUB_KEY,
        }
        return render(request, "carts/checkout.html", context)

    if not cart.is_reserved_by_me():
        from itertools import chain
        reserved_pipes = list(cart.get_reserved_by_someone_else())
        purchased = list(cart.already_purchased())
        reserved = list(chain(reserved_pipes, purchased))
        print(reserved)
        context = {
            "pipes": reserved,
        }
        cart.remove_reserved()
        print(reserved)
        return render(request, "carts/checkout-error.html", context)

    cart.reserve()

    order = None

    billing_address_id = request.session.get("billing_address_id", None)
    # shipping_address_id = request.session.get("shipping_address_id", None)

    billing_profile, billing_profile_created = BillingProfile.objects.new_or_get(request=request)
    address_qs = None
    has_card = False

    # print(billing_profile, billing_address_id, shipping_address_id)

    if billing_profile is not None:
        if request.user.is_authenticated:
            address_qs = Address.objects.filter(billing_profile=billing_profile)
        # shipping_add_qs = address_qs.filter(address_type='shipping')
        # billing_add_qs = address_qs.filter(address_type='billing')

        order, _ = Order.objects.new_or_get(billing_profile=billing_profile, cart=cart)

        # if shipping_address_id:
        #     order.shipping_address = Address.objects.get(id=shipping_address_id)
        #     del request.session["shipping_address_id"]

        if billing_address_id:
            order.billing_address = Address.objects.get(id=billing_address_id)
            del request.session["billing_address_id"]

        if billing_address_id:  # or shipping_address_id:
            order.save()

        has_card = billing_profile.has_card

    context = {
        "object": order,
        "billing_profile": billing_profile,
        "login_form": login_form,
        "address_form": address_form,
        "address_qs": address_qs,
        "has_card": has_card,
        "publish_key": STRIPE_PUB_KEY,
    }

    if request.method == "POST":
        # "some check that order is done"
        is_prepared = order.check_done()
        if is_prepared:
            if order.payment_type == "card":
                print("Card")
                was_charged, charge_msg = billing_profile.charge(order_obj=order)
                if was_charged:
                    order.mark_paid()
                    request.session['cart_items'] = 0
                    cart_id = request.session['cart_id']
                    Cart.objects.get(id=cart_id).mark_bought(context.copy(), billing_profile=billing_profile)
                    del request.session['cart_id']
                    if not billing_profile.user:
                        billing_profile.set_cards_inactive()
                    return redirect('cart:success')
                else:
                    return render(request, "carts/payment-fail.html", {'message': charge_msg})
            else:
                print("Bank")
                request.session['cart_items'] = 0
                cart_id = request.session['cart_id']
                Cart.objects.get(id=cart_id).mark_reserved(context.copy())
                del request.session['cart_id']
                return redirect('cart:home')

    return render(request, "carts/checkout.html", context)


def checkout_done_view(request):
    return render(request, "carts/checkout-done.html", {})
