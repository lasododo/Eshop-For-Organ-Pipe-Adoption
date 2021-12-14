from django.shortcuts import redirect
from django.utils.http import is_safe_url

from .forms import AddressForm
from .models import Address

from billing.models import BillingProfile


def checkout_address_create_view(request):
    form = AddressForm(request.POST or None)
    next_jump = request.GET.get('next')
    next_post_jump = request.POST.get('next')
    redirect_path = next_jump or next_post_jump or None
    if form.is_valid():
        instance = form.save(commit=False)
        billing_profile, billing_profile_created = BillingProfile.objects.new_or_get(request=request)
        if billing_profile is not None:
            address_type = request.POST.get('address_type', 'billing')  # for future when shipping is implemented.

            instance.billing_profile = billing_profile
            instance.address_type = address_type
            instance.save()
            request.session[address_type + "_address_id"] = instance.id

        if is_safe_url(redirect_path, request.get_host()):
            return redirect(redirect_path)
    return redirect("cart:checkout")


def checkout_address_use_view(request):
    if not request.user.is_authenticated:
        return redirect("cart:checkout")

    next_jump = request.GET.get('next')
    next_post_jump = request.POST.get('next')
    redirect_path = next_jump or next_post_jump or None

    if request.method == "POST":
        ship_address = request.POST.get('billing_address', None)
        address_type = request.POST.get('address_type', 'billing')
        billing_profile, billing_profile_created = BillingProfile.objects.new_or_get(request=request)
        if ship_address is not None:
            qs = Address.objects.filter(billing_profile=billing_profile, id=ship_address)
            if qs.exists():
                request.session[address_type + "_address_id"] = ship_address
            if is_safe_url(redirect_path, request.get_host()):
                return redirect(redirect_path)
    return redirect("cart:checkout")
