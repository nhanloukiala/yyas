__author__ = 'nhan'

from django.conf.urls import url
from . import views

urlpatterns = [
    url(r'^$', views.auction_list, name = 'auction_list'),
]