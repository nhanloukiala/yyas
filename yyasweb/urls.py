__author__ = 'nhan'

from django.conf.urls import url
from . import views
from django.views.generic.edit import CreateView
from .forms import *
from yyasweb import rest_views

urlpatterns = [
    url(r'^$', views.welcome_view, name='welcome_view'),
    url(r'^auction/create/$', views.create_auction, name='create_auction'),
    url(r'^auction/(?P<pk>\d+)/$', views.auction_detail, name='auction_detail'),
    url(r'^login/$', views.login_view, name='custom_login'),
    url(r'^bid/$', views.place_bid, name='place_bid'),
    url(r'^register/', CreateView.as_view(
            template_name='registration/register.html',
            form_class=CustomUserCreationForm,
            success_url='/'
    ), name='register'),
    url(r'^auction/edit/(?P<pk>\d+)$', views.edit_auction, name='auction_edit'),
    url(r'^auction/search/', views.search, name='search'),
    url(r'^auction/ban/$', views.ban_auction, name='ban_auction'),
    url(r'^auction/unban/(?P<pk>\d+)$', views.unban_auction, name='unban_auction'),
    url(r'^currency/$', views.change_currency, name ='currency_change'),
    url(r'^lang/$', views.change_language, name='language_change'),
    url(r'^token/$', views.get_token, name='get_token'),
    url(r'^api/getauction/$', rest_views.get_auction_list, name='get_auction'),
    url(r'^api/getauction/(?P<page>\d+)/$', rest_views.get_auction_list, name='get_auction'),
    url(r'^api/bid/(?P<pk>\d+)/$', rest_views.bid_list, name = 'bid_auction')
]
