from django.conf.urls import url

from .views import (
        ProductListView, 
        ProductDetailSlugView,
        PipeGenerateView,
        SingleManualTable,
        ManualInitialView
        )

urlpatterns = [
    url(r'^$', ProductListView.as_view(), name='list'),
    url(r'^generate/$', PipeGenerateView.as_view(), name='generate'),
    url(r'^magic_table/$', SingleManualTable.as_view(), name='smt'),
    url(r'^(?P<slug>[\w-]+)/$', ProductDetailSlugView.as_view(), name='detail'),
    url(r'^magic_table/(?P<name>[\w-]+)/$', ManualInitialView.as_view(), name='table'),
]
