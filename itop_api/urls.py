from django.conf.urls import url
from .views import (vm_api)
urlpatterns = [
            url(r'^vm/$', vm_api.vm_list),
            url(r'^assets_syncitop/$', vm_api.assets_syncitop),
            url(r'^vm/(?P<id>[0-9]+)/$', vm_api.vm_detail),
    ]