from django.shortcuts import render
from django.contrib.auth import login, authenticate
from django.http import *
from django.core.urlresolvers import reverse
from django.contrib.auth.decorators import login_required
from django.contrib.auth.decorators import user_passes_test
from forms import *
import pdb

def welcome_view(request, auction = Auction.listAuction()):
    auction = Auction.excludeBanned(auction)
    if request.user.is_authenticated():
        return render(request, 'auction/auction_list.html',
                      {'username': request.user.username, 'auctions': auction})
    else:
        return render(request, 'auction/auction_list.html', {'auctions' : auction})

@login_required
@user_passes_test(lambda u: u.is_staff)
def ban_auction(request):
    if request.POST['auction_id']:
        pk = request.POST['auction_id']
        if Auction.ban(pk):
            return HttpResponseRedirect(reverse('auction_detail', kwargs={'pk': pk}))
        else:
            # tbd
            return HttpResponse('error happened')

@login_required
@user_passes_test(lambda u:u.is_staff)
def unban_auction(request, pk):
    Auction.unban(pk)
    return HttpResponseRedirect(reverse('auction_detail', kwargs={'pk': pk}))

def auction_detail(request, pk, bidform=BidForm()):
    auction = Auction.objects.get(pk=pk)
    bids = auction.bid_set.all()

    if not bids:
        maxBidPrice = auction.minPrice
    else:
        maxbid = max(bids, key=lambda b: b.price)
        maxBidPrice = maxbid.price

    return render(request, 'auction/auction_detail.html',
                  {'auction': auction, 'form': bidform, 'bids': bids, 'maxbid': maxBidPrice})


def login_view(request):
    username = request.POST['username']
    password = request.POST['password']
    user = authenticate(username=username, password=password)
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
    auction_id = request.POST['auction_id']
    if form.is_valid():
        bid = form.save(commit=False)
        bid.auction = Auction.objects.get(pk=auction_id)
        bid.bidder = request.user
        bid.save()
        return auction_detail(request, pk=auction_id)
    return auction_detail(request, pk=auction_id, bidform=form)

def search(request):
    if 'str' in request.GET:
        str = request.GET['str']
        auctions = Auction.search(str)
        auctions = Auction.excludeBanned(auctions)
        return welcome_view(request, auctions)

def create_auction(request, form=AuctionForm()):
    if request.method == "GET":
        form = form
        return render(request, 'auction/create.html', {'form': form, 'id' : form.id})
    elif request.method == "POST":
        form = AuctionForm(request.POST)
        if form.is_valid():
            if 'id' in request.POST:
                auction = Auction.objects.get(pk = form.data['id'])
                form = AuctionForm(request.POST, instance=auction)
                form.save()
                pdb.set_trace()
                return auction_detail(request, form.data['id'], bidform=BidForm())
            else:
                auction = form.save(commit=False)
                auction.seller = request.user
                auction.state = AuctionState.active
                auction.maxPrice = auction.minPrice
                auction.save()
                return welcome_view(request)
        return render(request, 'auction/create.html', {'form': form})


def edit_auction(request, pk):
    if request.method == "GET":
        auction = Auction.objects.get(pk=pk)
        form = AuctionForm(instance=auction, initial={'auction': auction, 'id': pk})
        form.id = 3
        return create_auction(request, form)


def resolve_auction(request, pk):
    Auction.resolve(pk=pk)
    return HttpResponseRedirect(reverse('welcome_view'))

def unban_auction(request, pk):
    Auction.unban(pk=pk)
    return HttpResponseRedirect(reverse('welcome_view'))
