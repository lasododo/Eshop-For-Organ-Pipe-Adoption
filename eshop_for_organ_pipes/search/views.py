from django.views.generic import ListView

from carts.models import Cart
from pipes_shop.models import Pipe, Manual, Registry, Note


class SearchProductListView(ListView):
    paginate_by = 6
    template_name = "pipes_shop/list.html"

    def get_context_data(self, **kwargs):
        context = super(SearchProductListView, self).get_context_data(**kwargs)
        cart, _ = Cart.objects.new_or_get(self.request)
        context['cart'] = cart
        context['notes'] = Note.objects.all()
        context['registries'] = Registry.objects.all()
        context['manuals'] = Manual.objects.all()
        get_copy = self.request.GET.copy()
        if get_copy.get('page'):
            get_copy.pop('page')
        context['get_copy'] = get_copy
        return context

    def get_queryset(self, *args, **kwargs):
        request = self.request
        print(request.GET)
        param_dict = request.GET
        query = Pipe.objects.all()

        # Manual Handling
        if param_dict.get('manual_opt', None) is not None:
            manual = Manual.objects.all()

            if param_dict.get('manual_opt') != "All":
                print(param_dict.get('manual_opt'))
                manual = manual.filter(name=param_dict.get('manual_opt', None))
                query = query.filter(manual=manual.first())

        if param_dict.get('manual_src', '') != '':
            manuals = Manual.objects.all().filter(name__icontains=param_dict.get('manual_src', None))
            query = query.filter(manual__in=manuals)

        # Registry Handling
        if param_dict.get('registry_opt', None) is not None:
            registry = Registry.objects.all().filter(name=param_dict.get('registry_opt', None))

            if param_dict.get('registry_opt') != "All":
                registry = registry.filter(name=param_dict.get('registry_opt', None))
                query = query.filter(registry=registry.first())

        if param_dict.get('registry_src', '') != '':
            registries = Registry.objects.all().filter(name__icontains=param_dict.get('registry_src', None))
            query = query.filter(registry__in=registries)

        # Note Handling
        if param_dict.get('note_opt', None) is not None:
            note = Note.objects.all().filter(name=param_dict.get('note_opt', None))

            if param_dict.get('note_opt') != "All":
                note = note.filter(name=param_dict.get('note_opt', None))
                query = query.filter(note=note.first())

        if param_dict.get('note_src', '') != '':
            notes = Note.objects.all().filter(name__icontains=param_dict.get('note_src', None))
            query = query.filter(note__in=notes)

        # price handling
        if param_dict.get('fromprice', None) is not None and param_dict.get('fromprice', None) != "0":
            query = query.filter(price__gte=float(param_dict['fromprice']))

        if param_dict.get('toprice', None) is not None and param_dict.get('toprice', None) != "0":
            query = query.filter(price__lte=float(param_dict['toprice']))

        if param_dict.get('show_buyable', None) is not None:
            query = query.filter(buyable=True).filter(is_reserved=False)

        if param_dict.get('show_purchased', None) is not None:
            query = query.filter(buyable=False)

        if param_dict.get('q', None) is not None:
            query = query.filter(name__icontains=param_dict['q'])

        return query
