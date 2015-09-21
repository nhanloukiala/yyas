from django.shortcuts import render
from django.contrib.auth import login, authenticate
from django.http import *
from .models import *
from django.core.urlresolvers import reverse
from django.contrib.auth.decorators import login_required
import pdb


# Create your views here.

def welcome_view(request):
    if request.user.is_authenticated():
        return render(request, 'auction/auction_list.html',
                      {'username': request.user.username, 'auctions': Auction.listAuction()})
    else:
        return render(request, 'auction/auction_list.html')


def auction_detail(request, pk):
    auction = Auction.objects.get(pk=pk)
    return render(request, 'auction/auction_detail.html',{'auction' : auction, 'form': BidForm()})

def login_view(request):
    username = request.POST['username']
    password = request.POST['password']
    user = authenticate(username=username, password=password)
    # pdb.set_trace()
    if user is not None:
        if user.is_active:
            login(request, user)
            return HttpResponseRedirect(reverse('welcome_view'))
        else:
            return HttpResponse('user blocked')
    else:
        return Http404()

@login_required
def place_bid(request):
    form = BidForm(request.POST)
    if form.is_valid():
        bid = form.save(commit=False)
        pdb.set_trace()
        bid.auction = Auction.objects.get(pk=request.POST['auction_id'])
        bid.bidder = request.user
        bid.save()
    return HttpResponseRedirect(reverse('welcome_view'))

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
            return HttpResponseRedirect(reverse('welcome_page'))
        return render(request, 'auction/create.html', {'form': form})
