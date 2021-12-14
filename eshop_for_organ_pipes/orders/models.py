import math
import random
import string

from django.db import models
from django.db.models.signals import pre_save, post_save

from Addresses.models import Address
from billing.models import BillingProfile
from carts.models import Cart

ORDER_STATUS = (
    ('created', 'Created'),
    ('paid', 'Paid'),
)

PAYMENT_TYPE = (
    ('card', 'Card'),
    ('bank', 'Bank'),
)


class OrderManager(models.Manager):
    def new_or_get(self, billing_profile, cart):
        order_qs = self.get_queryset().filter(
            billing_profile=billing_profile,
            cart=cart,
            active=True,
            status='created'
        )
        if order_qs.count() == 1:
            return order_qs.first(), False
        else:
            return self.model.objects.create(
                billing_profile=billing_profile,
                cart=cart
            ), True


class Order(models.Model):
    order_id = models.CharField(max_length=120, blank=True)
    billing_profile = models.ForeignKey(BillingProfile, on_delete=models.DO_NOTHING, null=True, blank=True)
    billing_address = models.ForeignKey(Address, related_name="billing_address", on_delete=models.DO_NOTHING, null=True, blank=True)
    cart = models.ForeignKey(Cart, on_delete=models.DO_NOTHING)
    status = models.CharField(max_length=120, default='created', choices=ORDER_STATUS)
    order_total = models.DecimalField(default=0.00, max_digits=100, decimal_places=2)
    active = models.BooleanField(default=True)
    payment_type = models.CharField(max_length=120, choices=PAYMENT_TYPE, blank=True, null=True)

    objects = OrderManager()

    def __str__(self):
        return self.order_id

    def update_total(self):
        # can be switched for Decimal + Decimal
        total = format(self.cart.total, '.2f')
        self.order_total = self.cart.total
        self.save()
        return total

    def check_done(self):
        billing_profile = self.billing_profile
        # ship_address = self.shipping_address
        bill_address = self.billing_address
        total = self.order_total
        return bill_address and billing_profile and float(total) > 0

    def mark_paid(self):
        self.status = 'paid'
        self.save()


def pre_save_create_order_id(sender, instance, *args, **kwargs):
    if not instance.order_id:
        instance.order_id = unique_order_id_generator(instance)

    qs = Order.objects.filter(cart=instance.cart).exclude(billing_profile=instance.billing_profile)
    if qs.exists():
        qs.update(active=False)


def post_save_cart_total(sender, instance, created, *args, **kwargs):
    if created:
        return

    cart_obj = instance
    cart_total = cart_obj.total
    cart_id = cart_obj.id
    qs = Order.objects.filter(cart__id=cart_id)
    if qs.count() == 1:
        order_obj = qs.first()
        order_obj.update_total()


def post_save_order(sender, instance, created, *args, **kwargs):
    if created:
        instance.update_total()


pre_save.connect(pre_save_create_order_id, sender=Order)
post_save.connect(post_save_cart_total, sender=Cart)
post_save.connect(post_save_order, sender=Order)



"""
Unique ORDER ID generator (to make sure, that 2 items with same name etc. will not crash ur app)
"""


def random_string_generator(size=10, chars=string.ascii_lowercase + string.digits):
    return ''.join(random.choice(chars) for _ in range(size))


def unique_order_id_generator(instance):
    """
    This is for a Django project and it assumes your instance
    has a model with a slug field and a title character (char) field.
    """

    order_id_new = random_string_generator().upper()

    Klass = instance.__class__

    if Klass.objects.filter(order_id=order_id_new).exists():
        return unique_order_id_generator(instance)

    return order_id_new


