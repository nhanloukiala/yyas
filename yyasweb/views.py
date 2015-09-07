from django.shortcuts import render
from django.contrib.auth.decorators import login_required
# Create your views here.

@login_required()
def auction_list(request):
    if request.user.is_authenticated():
        return render(request, 'auction/index.html', {'username': request.user.username})

