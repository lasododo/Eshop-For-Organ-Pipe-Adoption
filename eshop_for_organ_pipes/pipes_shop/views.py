from django.db.models import Sum
from django.http import Http404
from django.utils import timezone
from django.views.generic import ListView, DetailView, TemplateView

from billing.models import BillingProfile
from .generators import generate_file_like
from .models import Pipe, Registry, Note, Manual

from carts.models import Cart


def generate_dic_for_table_differently(notes_list):
    pipe_list = list(Pipe.objects.all().order_by('registry__name', 'note__name'))
    registry_list = list(Registry.objects.all().order_by('name'))
    all_of_them = dict()

    for cat in registry_list:
        all_of_them[cat] = dict()
        for note in notes_list:
            all_of_them[cat][note] = dict()
            all_of_them[cat][note]["val"] = "-"
            all_of_them[cat][note]["pipe"] = None

    for pipe in pipe_list:
        all_of_them[pipe.registry][pipe.note]["val"] = "X"
        all_of_them[pipe.registry][pipe.note]["pipe"] = pipe

    return all_of_them


def generate_dic_for_table_new(request, manual, registries, notes):
    pipe_list = list(Pipe.objects.all().filter(manual=manual).order_by('registry__name', 'note__name'))
    all_of_them = dict()
    all_price = dict()
    all_price['price'] = 0
    all_price['price_purchased'] = 0

    for cat in list(registries):
        all_of_them[cat] = dict()
        for note in list(notes):
            all_of_them[cat][note] = dict()
            all_of_them[cat][note]["val"] = "-"
            all_of_them[cat][note]["pipe"] = None

    # import random

    # fill = random.randint(0, 10)
    # ignore = random.randint(0, 50)
    for pipe in pipe_list:

        all_of_them[pipe.registry][pipe.note]["val"] = "X"
        all_of_them[pipe.registry][pipe.note]["pipe"] = pipe

        # if pipe.buyable and False:  # Development purposes only
        #    if fill > 0:
        #        bp, _ = BillingProfile.objects.new_or_get(request=request)
        #        pipe.buyer = bp.user
        #        pipe.buyable = False
        #        pipe.time_bought = timezone.now()
        #        pipe.save()
        #        fill -= 1
        #    else:
        #        if ignore > 0:
        #            ignore -= 1
        #        else:
        #            fill = random.randint(0, 10)
        #            ignore = random.randint(0, 10)

        if not pipe.buyable:
            all_price['price_purchased'] += pipe.price
        all_price['price'] += pipe.price

    return all_price, all_of_them


def fill_context(request, context, manual):
    registries = manual.registries.all().order_by('name')
    notes = manual.notes.all()
    context['note'] = notes
    context['manual'] = manual
    context['manuals'] = Manual.objects.all()
    all_price, all_rows = generate_dic_for_table_new(request, manual, registries, notes)
    context['tab'] = all_rows
    percentage_pipes = float(all_price['price_purchased'] / all_price['price']) * 100
    # a special way to count the percentage, since 220 = 0% and 0 = 100%
    context['circle_val'] = 220 - (percentage_pipes * (220 / 100))
    context['percentage'] = "{:.2f}".format(percentage_pipes)

    price = Pipe.objects.all().filter(buyable=False).aggregate(Sum('price')).get('price__sum', "Error")
    if price is None:
        price = "0"
    context['manual_all_price'] = price
    return context


class ProductListView(ListView):
    paginate_by = 6
    template_name = "pipes_shop/list.html"

    def get_context_data(self, **kwargs):
        context = super(ProductListView, self).get_context_data(**kwargs)
        cart, _ = Cart.objects.new_or_get(self.request)
        context['cart'] = cart
        context['notes'] = Note.objects.all()
        context['registries'] = Registry.objects.all()
        context['manuals'] = Manual.objects.all()
        return context

    def get_queryset(self, *args, **kwargs):
        return Pipe.objects.all().order_by('name')


class SingleManualTable(TemplateView):
    template_name = "pipes_shop/manual_table.html"

    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(**kwargs)
        cart, _ = Cart.objects.new_or_get(self.request)
        context['cart'] = cart
        manuals = Manual.objects.all()

        if not manuals.exists() or manuals.count() == 0:
            raise Http404("There is no Manual")

        manual = manuals.first()
        return fill_context(self.request, context, manual)


class ManualInitialView(DetailView):
    queryset = Manual.objects.all()
    template_name = "pipes_shop/manual_table.html"

    def get_context_data(self, **kwargs):
        context = super(ManualInitialView, self).get_context_data(**kwargs)
        cart, _ = Cart.objects.new_or_get(self.request)
        context['cart'] = cart

        manual = context['manual']

        if manual is None:
            raise Http404("Not found..")

        return fill_context(self.request, context, manual)

    def get_object(self, *args, **kwargs):
        name = self.kwargs.get('name')
        try:
            manual = Manual.objects.all().filter(name=name).first()

            if manual is None:
                raise Http404("Not found..")

        except Manual.DoesNotExist:
            raise Http404("Not found..")
        except Exception:
            raise Http404("Something went wrong, please contact the website admin")
        return manual


class PipeGenerateView(ListView):
    paginate_by = 6
    template_name = "pipes_shop/list.html"

    def get_context_data(self, **kwargs):
        context = super(PipeGenerateView, self).get_context_data(**kwargs)
        cart, _ = Cart.objects.new_or_get(self.request)
        context['notes'] = Note.objects.all()
        context['registries'] = Registry.objects.all()
        context['manuals'] = Manual.objects.all()
        context['cart'] = cart
        return context

    def get_queryset(self, *args, **kwargs):
        if not self.request.user.is_admin:
            raise Http404("Not found..")

        generate_file_like()
        return Pipe.objects.all()


class ProductDetailSlugView(DetailView):
    queryset = Pipe.objects.all()
    template_name = "pipes_shop/detail.html"

    def get_context_data(self, **kwargs):
        context = super(ProductDetailSlugView, self).get_context_data(**kwargs)
        cart, _ = Cart.objects.new_or_get(self.request)
        context['cart'] = cart
        return context

    def get_object(self, *args, **kwargs):
        slug = self.kwargs.get('slug')
        try:
            instance = Pipe.objects.get(slug=slug, active=True)
        except Pipe.DoesNotExist:
            raise Http404("Not found..")
        except Pipe.MultipleObjectsReturned:
            qs = Pipe.objects.filter(slug=slug, active=True)
            instance = qs.first()
        except Exception:
            raise Http404("Something went wrong, please contact the website admin")
        return instance
