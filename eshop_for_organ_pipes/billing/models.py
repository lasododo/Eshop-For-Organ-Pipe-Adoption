from django.conf import settings
from django.urls import reverse
from django.db import models
from django.db.models.signals import post_save, pre_save

from eshop_for_organ_pipes import constants

USER = settings.AUTH_USER_MODEL


import stripe
stripe.api_key = constants.STRIPE_SECRET_API_KEY


class BillingProfileManager(models.Manager):
    def new_or_get(self, request):
        user = request.user

        billing_profile = None
        created = False
        if user.is_authenticated:
            billing_profile, created = self.model.objects.get_or_create(user=user, email=user.email)

        return billing_profile, created


# Create your models here.
class BillingProfile(models.Model):
    user = models.OneToOneField(USER, null=True, blank=True, on_delete=models.DO_NOTHING)
    email = models.EmailField()
    active = models.BooleanField(default=True)
    update = models.DateTimeField(auto_now=True)
    timestamp = models.DateTimeField(auto_now_add=True)
    customer_id = models.CharField(max_length=120, null=True, blank=True)

    objects = BillingProfileManager()

    def __str__(self):
        return "BP " + self.email

    def charge(self, order_obj, card=None):
        return Charge.objects.do_charge(billing_profile=self, order_obj=order_obj, card=card)

    def get_cards(self):
        return self.card_set.all()

    @property
    def has_card(self):
        card_qs = self.get_cards()
        return card_qs.exists()

    @property
    def default_card(self):
        default_cards = self.get_cards().filter(active=True, default=True)
        if default_cards.exists():
            return default_cards.first()
        return None

    def set_cards_inactive(self):
        cards_qs = self.get_cards()
        cards_qs.update(active=False)
        return cards_qs.filter(active=True).count()

    def get_payment_method_url(self):
        return reverse('payment')


def user_created_receiver(sender, instance, created, *args, **kwargs):
    if created and instance.email:
        BillingProfile.objects.get_or_create(user=instance, email=instance.email)


def billing_profile_created_receiver(sender, instance, *args, **kwargs):
    if not instance.customer_id and instance.email:
        customer = stripe.Customer.create(
            email=instance.email
        )
        print(customer)
        instance.customer_id = customer.id


post_save.connect(user_created_receiver, sender=USER)
pre_save.connect(billing_profile_created_receiver, sender=BillingProfile)


class CardManager(models.Manager):
    def all(self, *args, **kwargs):
        return self.get_queryset().filter(active=True)

    def add_new(self, billing_profile, stripe_card_resp):
        if str(stripe_card_resp.object) == "card":
            new_card = self.model(
                billing_profile=billing_profile,
                stripe_id=stripe_card_resp.id,
                brand=stripe_card_resp.brand,
                country=stripe_card_resp.country,
                exp_month=stripe_card_resp.exp_month,
                exp_year=stripe_card_resp.exp_year,
                last4=stripe_card_resp.last4,
            )
            new_card.save()
            return new_card
        return None

    def add_new_using_token(self, billing_profile, token):
        if token:
            stripe_card_resp = stripe.Customer.create_source(
                billing_profile.customer_id,
                source=token,
            )

            new_card = self.model(
                billing_profile=billing_profile,
                stripe_id=stripe_card_resp.id,
                brand=stripe_card_resp.brand,
                country=stripe_card_resp.country,
                exp_month=stripe_card_resp.exp_month,
                exp_year=stripe_card_resp.exp_year,
                last4=stripe_card_resp.last4,
            )
            new_card.save()
            return new_card
        return None


class Card(models.Model):
    """
    {
      "address_city": null,
      "address_country": null,
      "address_line1": null,
      "address_line1_check": null,
      "address_line2": null,
      "address_state": null,
      "address_zip": "12345",
      "address_zip_check": "pass",
      "brand": "Visa",
      "country": "US",
      "customer": "cus_KA5eXz849VaDhu",
      "cvc_check": "pass",
      "dynamic_last4": null,
      "exp_month": 2,
      "exp_year": 2022,
      "fingerprint": "4pqx5X4WIYRlTO56",
      "funding": "credit",
      "id": "card_1JVlUEFcbVHhGAD5fGLwMj2Y",
      "last4": "4242",
      "metadata": {},
      "name": null,
      "object": "card",
      "tokenization_method": null
    }
    """
    billing_profile = models.ForeignKey(BillingProfile, on_delete=models.deletion.CASCADE)
    stripe_id = models.CharField(max_length=120)
    brand = models.CharField(max_length=120, null=True, blank=True)
    country = models.CharField(max_length=120, null=True, blank=True)
    exp_month = models.IntegerField(null=True, blank=True)
    exp_year = models.IntegerField(null=True, blank=True)
    last4 = models.CharField(max_length=4, null=True, blank=True)
    default = models.BooleanField(default=True)
    active = models.BooleanField(default=True)
    timestamp = models.DateTimeField(auto_now_add=True)

    objects = CardManager()

    def __str__(self):
        return f"{self.brand} - {self.last4}"


class ChargeManager(models.Manager):
    def do_charge(self, billing_profile, order_obj, card=None):
        if card is None:
            cards = billing_profile.card_set.filter(default=True)
            if cards.exists():
                card = cards.first()

        if card is None or billing_profile is None:
            return False, "There is no Card / Billing Profile"

        print(Charge.objects.filter(billing_profile=billing_profile).first())

        charge = stripe.Charge.create(
            amount=int(order_obj.order_total * 100),
            currency=constants.CURRENCY,
            customer=billing_profile.customer_id,
            source=card.stripe_id,
            description="My First Test Charge (created for API docs)",
        )

        new_charge = self.model(
            billing_profile=billing_profile,
            stripe_id=charge.stripe_id,
            paid=charge.paid,
            outcome=charge.outcome,
            outcome_type=charge.outcome.get("outcome_type"),
            seller_message=charge.outcome.get("seller_message"),
            risk_level=charge.outcome.get("risk_level")
        )

        new_charge.save()

        return new_charge.paid, new_charge.seller_message


class Charge(models.Model):
    billing_profile = models.ForeignKey(BillingProfile, on_delete=models.deletion.CASCADE)
    stripe_id = models.CharField(max_length=120)
    paid = models.BooleanField(default=False)
    outcome = models.TextField(null=True, blank=True)
    outcome_type = models.CharField(max_length=120, null=True, blank=True)
    seller_message = models.CharField(max_length=120, null=True, blank=True)
    risk_level = models.CharField(max_length=120, null=True, blank=True)

    objects = ChargeManager()


def new_card_post_save_receiver(sender, instance, created, *args, **kwargs):
    if instance.default:
        billing_profile = instance.billing_profile
        qs = Card.objects.filter(billing_profile=billing_profile).exclude(pk=instance.pk)
        qs.update(default=False)


post_save.connect(new_card_post_save_receiver, sender=Card)
