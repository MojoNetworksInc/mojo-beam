from django.conf.urls import include, url
from beam import views

urlpatterns = [           
    url(r'^list/(?P<name>\w+)/$', views.list_ssid , name='list_ssid'),        
    url(r'^login/$', views._login, name='login'),  
    url(r'^logout/$', views._logout, name='logout'),  
    url(r'^ssid/new$', views.ssids_modify, name='ssids_modify'),  
    url(r'^ssid/approve/(?P<id>\d+)/$', views.approve_ssid_request, name='approve_ssid_request'),  
    url(r'^ssid/reject/(?P<id>\d+)/$', views.reject_ssid_request, name='reject_ssid_request'), 
    url(r'^ssid/on/(?P<id>\d+)/$', views.on_ssid_request, name='on_ssid_request'),  
    url(r'^ssid/off/(?P<id>\d+)/$', views.off_ssid_request, name='off_ssid_request'),  

]
