__author__ = 'nhan'

from django.conf.urls import url
from . import views

urlpatterns = [
    url(r'^$', views.welcome_view, name='welcome_view'),
    url(r'^auction/create/$', views.create_auction, name='create_auction'),
    url(r'^auction/(?P<pk>\d+)/$', views.auction_detail, name='auction_detail'),
    url(r'^login/$', views.login_view, name='custom_login'),
    url(r'^bid/$', views.place_bid, name='place_bid')
]
