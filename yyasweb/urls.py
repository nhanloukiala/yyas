__author__ = 'nhan'

from django.conf.urls import url
from . import views
from django.views.generic.edit import CreateView
from .forms import *

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
]
