__author__ = 'nhan'
from models import *
from django.forms import ModelForm, DateTimeInput, Select, DecimalField
from django.contrib.auth.forms import UserCreationForm, UserChangeForm
from YYAS import settings


class AuctionForm(ModelForm):
    id = None
    version = None
    class Meta:
        model = Auction
        fields = ('title', 'minPrice', 'description', 'endDate',)
        exclude = ('startDate',)
        labels = {'endDate': 'End Date ' + settings.DATETIME_INPUT_FORMAT}
        widgets = {'endDate': DateTimeInput(format=settings.DATETIME_INPUT_FORMAT), }


class BidForm(ModelForm):
    class Meta:
        model = Bid
        fields = ('price',)

class CustomUserCreationForm(UserCreationForm):


    def __init__(self, *args, **kargs):
        super(CustomUserCreationForm, self).__init__(*args, **kargs)

    class Meta:
        model = CustomUser
        fields = ("username", "email", "address", "preferedLanguage")
        widgets = {'preferedLanguage': Select(choices=settings.LANGUAGE_CHOICES)}


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
