from django.conf.urls import include, url
from django.contrib import admin
from beam import views

urlpatterns = [
    # Examples:
     
    # url(r'^blog/', include('blog.urls')),

	url(r'^$', views.list_ssid , {'name' : 'all'}, name='list_ssid'),
 	url(r'^beam/', include('beam.urls')),
    url(r'^admin/', include(admin.site.urls)),
]
