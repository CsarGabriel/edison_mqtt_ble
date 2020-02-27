from django.conf.urls import url
from . import views

urlpatterns = [
    #127.0.0.1/
    url(r'^$', views.devices, name='devices'),

    #127.0.0.1/api_log_save
    url(r'^api_log_save/$', views.api_log_save, name='api_save'),

    #127.0.0.1/api_devices
    url(r'^api_devices/$', views.api_devices, name='api_devices'),

    #127.0.0.1/logs/devices
    url(r'^devices/$', views.devices, name='devices2'),

    #127.0.0.1/logs/registers
    url(r'^registers/(?P<dev_id>[0-9]+)$', views.registers, name='registers'),
    
]
