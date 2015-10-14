__author__ = 'nhan'
from models import *
from django.forms import ModelForm
from django.contrib.auth.forms import UserCreationForm, UserChangeForm

class AuctionForm(ModelForm):
    id = None
    class Meta:
        model = Auction
        fields = ('title', 'minPrice', 'description', 'endDate',)
        exclude = ('startDate',)

class BidForm(ModelForm):
    class Meta:
        model = Bid
        fields = ('price',)

class CustomUserCreationForm(UserCreationForm):
    def __init__(self, *args, **kargs):
        super(CustomUserCreationForm, self).__init__(*args, **kargs)

    class Meta:
        model = CustomUser
        fields = ("username", "email", "address")

class CustomUserChangeForm(UserChangeForm):
    """A form for updating users. Includes all the fields on
    the user, but replaces the password field with admin's
    password hash display field.
    """
    def __init__(self, *args, **kargs):
        super(CustomUserChangeForm, self).__init__(*args, **kargs)

    class Meta:
        model = CustomUser
        fields = '__all__'