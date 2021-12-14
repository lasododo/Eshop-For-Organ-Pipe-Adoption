from django.conf import settings
from django.db import models
from django.db.models.signals import pre_save, m2m_changed
from django.utils import timezone

from pipes_shop.models import Pipe
from accounts.models import User as AccUser


User = settings.AUTH_USER_MODEL


class CartManager(models.Manager):
    def new_or_get(self, request):
        cart_id = request.session.get("cart_id", None)
        qs = self.get_queryset().filter(id=cart_id)

        if qs.count() == 1:
            cart = qs.first()

            if request.user.is_authenticated and cart.user is None:
                cart.user = request.user
                cart.save()

            return cart, False
        else:
            if request.user.is_authenticated:
                qs2 = self.get_queryset().filter(user_id=request.user.id)

                if qs2.exists():
                    print(qs2.last().user_id)
                    cart = qs2.last()
                    return cart, False

            cart = self.new(user=request.user)
            request.session['cart_id'] = cart.id
            return cart, True

    def new(self, user=None):
        user_obj = None
        if user is not None and user.is_authenticated:
            user_obj = user
        return self.model.objects.create(user=user_obj)


class Cart(models.Model):
    user = models.ForeignKey(User, null=True, blank=True, on_delete=models.CASCADE)
    pipes = models.ManyToManyField(Pipe, blank=True)
    total = models.DecimalField(default=0.00, max_digits=100, decimal_places=2)
    sub_total = models.DecimalField(default=0.00, max_digits=100, decimal_places=2)
    updated = models.DateTimeField(auto_now=True)
    timestamp = models.DateTimeField(auto_now_add=True)
    # active = models.BooleanField(default=True)

    objects = CartManager()

    def is_reserved_by_me(self):
        pipes = self.pipes.all().filter(is_reserved=True).filter(buyable=True)
        for pipe in pipes:
            print(f"{pipe.name} -> {pipe.buyer} -> {self.user}")
            if pipe.buyer.id != self.user.id:
                return False
        return self.pipes.all().filter(is_reserved=True).filter(buyable=False).count() == 0

    def reserve(self):
        pipes = self.pipes.all()
        for pipe in pipes:
            if pipe.buyer != self.user and pipe.buyer is not None:
                raise Exception(f"Something fishy is going on here ... {pipe.name} {pipe.buyer} {self.user}")
            pipe.buyer = self.user
            pipe.is_reserved = True
            pipe.save()
        return True

    def get_reserved_by_someone_else(self):
        return self.pipes.all().filter(is_reserved=True).exclude(buyer=self.user)

    def already_purchased(self):
        return self.pipes.all().filter(is_reserved=True).filter(buyable=False)

    def remove_reserved(self):
        to_remove_reserved = self.get_reserved_by_someone_else()
        for item in to_remove_reserved:
            self.pipes.remove(item)
        to_remove_purchased = self.already_purchased()
        for item in to_remove_purchased:
            self.pipes.remove(item)
        # print(self.pipes.all().filter(Q(pipes__buyer=None) | Q(pipes__buyer=self.user)))

    def mark_bought(self, context, billing_profile=None):
        self.user.send_email(context)
        # uncomment this if you want to receive emails about all purchases
        # for user in self.get_admins():
        #     user.send_email(context, fail_silence=True)
        for pipe in self.pipes.all():
            if billing_profile is not None:
                pipe.buyer = billing_profile.user
            pipe.buyable = False
            pipe.time_bought = timezone.now()
            pipe.save()
        self.user = None
        self.save()

    def get_admins(self):
        return AccUser.objects.filter(admin=True)

    def mark_reserved(self, context):
        self.user.send_email(context)
        for user in self.get_admins():
            user.send_email(context, fail_silence=True)
        self.user = None
        self.save()

    def __str__(self):
        return str(self.id)


def m2mc_hanged_cart_receiver(sender, instance, action, *args, **kwargs):
    if "post" in action:
        pipes = instance.pipes.all()
        total = 0

        for item in pipes:
            total += item.price

        if instance.sub_total != total:
            instance.sub_total = total
            instance.save()


def pre_save_cart_receiver(sender, instance, *args, **kwargs):
    instance.total = instance.sub_total
    # if instance.sub_total > 0:
    #     instance.total = Decimal(instance.sub_total) * Decimal(1.2)
    # else:
    #    instance.total = instance.sub_total


m2m_changed.connect(m2mc_hanged_cart_receiver, sender=Cart.pipes.through)
pre_save.connect(pre_save_cart_receiver, sender=Cart)
