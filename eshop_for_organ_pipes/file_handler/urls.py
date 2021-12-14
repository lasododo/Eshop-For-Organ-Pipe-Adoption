from django.conf.urls import url

from .views import upload_file, generate_xlsx_page, generate_xlsx, download_file

urlpatterns = [
    url(r'^$', upload_file, name='upload'),
    url(r'^generate/$', generate_xlsx_page, name='generate'),
    url(r'^download/$', download_file, name='download'),
    url(r'^generate/generating$', generate_xlsx)
]

