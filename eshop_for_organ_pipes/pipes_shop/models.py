import random
import string

from django.db import models
from django.db.models.signals import pre_save
from django.urls import reverse
from django.utils.text import slugify

from accounts.models import User


class Registry(models.Model):
    name = models.CharField(max_length=120)
    shortcut = models.CharField(max_length=10)

    def __str__(self):
        return self.name

    def __unicode__(self):
        return self.name


class NoteManager(models.Manager):
    def get_queryset(self):
        return PipeQuerySet(self.model, using=self._db)

    def all(self):
        return self.get_queryset()

    def get_by_name(self, name):
        qs = self.get_queryset().filter(name=name)
        if qs.count() == 1:
            return qs.first()
        return None


class Note(models.Model):
    name = models.CharField(max_length=120)
    shortcut = models.CharField(max_length=10)

    def __str__(self):
        return self.name

    def __unicode__(self):
        return self.name


class Manual(models.Model):
    name = models.CharField(max_length=120, unique=True)
    registries = models.ManyToManyField(Registry, blank=True)
    notes = models.ManyToManyField(Note, blank=True)

    def __str__(self):
        return self.name

    def __unicode__(self):
        return self.name

    def get_absolute_url(self):
        # return "/pipes_shop/{slug}/".format(slug=self.slug)
        return reverse("pipes_shop:table", kwargs={"name": self.name})

    def get_percentage_inner(self):
        all_price = dict()
        all_price['price'] = 0
        all_price['price_purchased'] = 0

        for pipe in Pipe.objects.filter(manual=self):
            if not pipe.buyable:
                all_price['price_purchased'] += pipe.price
            all_price['price'] += pipe.price
        return float(all_price['price_purchased'] / all_price['price']) * 100

    def get_fill_portion(self):
        return 220 - (self.get_percentage_inner() * (220 / 100))

    def get_percentage(self):
        return "{:.2f}".format(self.get_percentage_inner())


class PipeQuerySet(models.query.QuerySet):
    def active(self):
        return self.filter(active=True)

    def buyable(self):
        return self.filter(buyable=True)

    def featured(self):
        return self.filter(featured=True, active=True)


class PipeManager(models.Manager):
    def get_queryset(self):
        return PipeQuerySet(self.model, using=self._db)

    def all(self):
        return self.get_queryset()

    def buyable(self):
        return self.get_queryset().buyable()

    def active(self):
        return self.get_queryset().active()

    def get_by_id(self, id):
        qs = self.get_queryset().filter(id=id)  # Pipe.objects == self.get_queryset() -> basically gets all pipes
        if qs.count() == 1:
            return qs.first()
        return None


class Pipe(models.Model):
    name = models.CharField(max_length=120)
    slug = models.SlugField(unique=True)                                            #  to distinguish what detail view we want to open
    registry = models.ForeignKey(Registry, on_delete=models.CASCADE)                # Back-end will automatically assign it from Registry Model
    note = models.ForeignKey(Note, on_delete=models.CASCADE)
    manual = models.ForeignKey(Manual, on_delete=models.CASCADE)
    price = models.DecimalField(decimal_places=2, max_digits=20, default=0.00)
    buyer = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    offline_buyer = models.CharField(max_length=120, blank=True, null=True)
    time_bought = models.DateTimeField(auto_now_add=False, blank=True, null=True)
    active = models.BooleanField(default=True)
    buyable = models.BooleanField(default=True)
    is_reserved = models.BooleanField(default=False)
    reservation_date = models.DateTimeField(auto_now_add=False, blank=True, null=True)

    objects = PipeManager()

    def get_absolute_url(self):
        # return "/pipes_shop/{slug}/".format(slug=self.slug)
        return reverse("pipes_shop:detail", kwargs={"slug": self.slug})

    def get_color_combo(self):
        if self.price < 1000:
            return "mediumorchid", "186,85,211", "text-white"
        if self.price < 5000:
            return "mediumpurple", "147,112,219", "text-white"
        if self.price < 25000:
            return "Coral", "255,127,80", "text-white"
        if self.price < 100000:
            return "mediumvioletred", "199,21,133", "text-white"
        return "mediumseagreen", "60,179,113", "text-white"

    def get_color(self):
        color, _, _ = self.get_color_combo()
        return color

    def get_color_rgb(self):
        _, color, _ = self.get_color_combo()
        return color

    def get_color_text(self):
        _, _, color = self.get_color_combo()
        return color

    def __str__(self):
        return self.name

    def __unicode__(self):
        return self.name


"""
Unique slug generator (to make sure, that 2 items with same name etc. will not crash ur app)
####  From tutorial mentioned in README.md  #####
"""


def random_string_generator(size=10, chars=string.ascii_lowercase + string.digits):
    return ''.join(random.choice(chars) for _ in range(size))


def unique_slug_generator(instance, new_slug=None):
    """
    This is for a Django project and it assumes your instance
    has a model with a slug field and a title character (char) field.
    """
    if new_slug is not None:
        slug = new_slug
    else:
        slug = slugify(instance.name)

    Klass = instance.__class__
    qs_exists = Klass.objects.filter(slug=slug).exists()
    if qs_exists:
        new_slug = "{slug}-{randstr}".format(
                    slug=slug,
                    randstr=random_string_generator(size=4)
                )
        return unique_slug_generator(instance, new_slug=new_slug)
    return slug


def product_pre_save_receiver(sender, instance, *args, **kwargs):
    if not instance.slug:
        instance.slug = unique_slug_generator(instance)


pre_save.connect(product_pre_save_receiver, sender=Pipe)

