"""eshop_for_organ_pipes URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.10/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.conf.urls import url, include
    2. Add a URL to urlpatterns:  url(r'^blog/', include('blog.urls'))
"""
from django.conf import settings
from django.conf.urls.static import static
from django.views.static import serve

from django.conf.urls import url, include
from django.contrib import admin
from django.contrib.auth.views import LogoutView
from .views import HomePageView
from accounts.views import RegisterView, LoginView
from Addresses.views import checkout_address_create_view, checkout_address_use_view
from billing.views import payment_method_view, payment_method_create_view
from carts.views import cart_detail_api


handler404 = 'eshop_for_organ_pipes.views.my_custom_404'
# handler500 = 'eshop_for_organ_pipes.views.my_custom_404'
# handler403 = 'eshop_for_organ_pipes.views.my_custom_404'
# handler400 = 'eshop_for_organ_pipes.views.my_custom_404'


urlpatterns = [
    url(r'^media/(?P<path>.*)$', serve,{'document_root': settings.MEDIA_ROOT}),
    url(r'^static/(?P<path>.*)$', serve,{'document_root': settings.STATIC_ROOT}),
    url(r'^$', HomePageView.as_view(), name='home'),
    url(r'^checkout/address/create/$', checkout_address_create_view, name='checkout_address_create_view'),
    url(r'^checkout/address/use/$', checkout_address_use_view, name='checkout_address_use_view'),
    url(r'^login/$', LoginView.as_view(), name='login'),
    url(r'^logout/$', LogoutView.as_view(), name='logout'),
    url(r'^billing/payment/$', payment_method_view, name='payment'),
    url(r'^billing/payment/create/$', payment_method_create_view, name='payment-api'),
    url(r'^register/$', RegisterView.as_view(), name='register'),
    url(r'^pipes_shop/', include(("pipes_shop.urls", 'pipes_shop'), namespace='pipes_shop')),
    url(r'^api/cart/$', cart_detail_api, name='cart_detail_api'),
    url(r'^cart/', include(("carts.urls", 'cart'), namespace='cart')),
    url(r'^search/', include(("search.urls", 'search'), namespace='search')),
    url(r'^files/', include(("file_handler.urls", 'file_handler'), namespace='files')),
    url(r'^admin/', admin.site.urls),
]


if settings.DEBUG:
    urlpatterns = urlpatterns + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    urlpatterns = urlpatterns + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)


"""
    url(r'^$', home_page, name='home'),
    url(r'^about/$', about_page, name='about'),
    url(r'^contact/$', contact_page, name='contact'),
    url(r'^login/$', login_page, name='login'),
    url(r'^register/$', register_page, name='register'),
    url(r'^bootstrap/$', TemplateView.as_view(template_name='bootstrap/example.html')),
    url(r'^products/', include("products.urls", namespace='products')),
"""