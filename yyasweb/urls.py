__author__ = 'nhan'

from django.conf.urls import url
from . import views

urlpatterns = [
    url(r'^$', views.auction_list, name='auction_list'),
    url(r'^auction/create/$', views.create_auction, name='create_auction'),
]
