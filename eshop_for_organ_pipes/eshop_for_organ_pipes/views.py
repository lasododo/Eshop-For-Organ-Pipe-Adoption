from django.db.models import Sum
from django.shortcuts import render
from django.views.generic import ListView


from pipes_shop.models import Pipe


class HomePageView(ListView):
    template_name = "home_page.html"

    def get_context_data(self, **kwargs):
        context = super(HomePageView, self).get_context_data(**kwargs)
        price = Pipe.objects.all().filter(buyable=False).aggregate(Sum('price')).get('price__sum', "Error")

        if price is None:
            price = "0"

        context['price'] = price
        return context

    def get_queryset(self, *args, **kwargs):
        request = self.request
        return Pipe.objects.all()


def my_custom_404(request, exception):
    context = {
        "title": "About Page",
        "content": " Welcome to the about page."
    }
    return render(request, "errors/404.html", context, status=404)
