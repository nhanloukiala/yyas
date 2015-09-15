from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.http import *
from .models import *
import pdb


# Create your views here.

def auction_list(request):
    if request.user.is_authenticated():
        return render(request, 'auction/index.html',
                      {'username': request.user.username, 'auctions': Auction.listAuction()})
    else:
        return render(request, 'auction/index.html')


def create_auction(request):
    if request.method == "GET":
        form = AuctionForm()
        return render(request, 'auction/create.html', {'form': form})
    elif request.method == "POST":
        form = AuctionForm(request.POST)
        if form.is_valid():
            auction = form.save(commit=False)
            auction.seller = request.user
            auction.state = AuctionState.active
            auction.maxPrice = auction.minPrice
            auction.save()
            return HttpResponse(str(auction))
        raise Http404("Fail")
