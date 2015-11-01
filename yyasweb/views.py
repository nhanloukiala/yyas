from django.shortcuts import render
from django.contrib.auth import login, authenticate
from django.http import *
from django.contrib import messages
from rest_framework.authtoken.models import Token
from django.core.urlresolvers import reverse
from django.contrib.auth.decorators import login_required
from django.contrib.auth.decorators import user_passes_test
from forms import *
import currencies as curr
from django.utils.translation import activate
import emails
import pdb

@login_required
def get_token(request):
    token, result = Token.objects.get_or_create(user=request.user)
    return render(request,'token.html',{'token':token.key})

def change_language(request):
    request.session['language'] = request.GET['language']

    if request.user.is_authenticated():
        request.user.preferedLanguage = request.GET['language']
        request.user.save()

    return HttpResponseRedirect(request.GET['next'])

def change_currency(request):
    currency = request.GET['currency']
    request.session[settings.TEMP_CURRENCY] = currency
    return HttpResponseRedirect(request.GET['next'])


def welcome_view(request, auction=Auction.listAuction()):
    activate(get_current_language(request))
    auction = Auction.excludeBanned(auction)

    displayRate = get_display_rate(request)

    dropDownHTML = curr.dropDownElementHelper(reverse('currency_change'), request.path)

    if request.user.is_authenticated():
        return render(request, 'auction/auction_list.html',
                      {'username': request.user.username, 'auctions': auction, 'dropdown': dropDownHTML,
                       'displayRate': displayRate})
    else:
        return render(request, 'auction/auction_list.html',
                      {'auctions': auction, 'dropdown': dropDownHTML, 'displayRate': displayRate})


@login_required
@user_passes_test(lambda u: u.is_staff)
def ban_auction(request):
    if request.POST['auction_id']:
        pk = request.POST['auction_id']
        if Auction.ban(pk):
            return HttpResponseRedirect(reverse('auction_detail', kwargs={'pk': pk}))
        else:
            messages.error(request, "The auction you banned is no longer existed")
            return HttpResponseRedirect(reverse('auction_detail', kwargs={'pk': pk}))


@login_required
@user_passes_test(lambda u: u.is_staff)
def unban_auction(request, pk):
    Auction.unban(pk)
    return HttpResponseRedirect(reverse('auction_detail', kwargs={'pk': pk}))


def auction_detail(request, pk, bidform=BidForm()):
    activate(get_current_language(request))
    auction = Auction.objects.get(pk=pk)
    bids = auction.bid_set.all()

    displayRate = get_display_rate(request)

    dropDownHTML = curr.dropDownElementHelper(reverse('currency_change'), request.path)

    if request.user.is_authenticated():
        is_owner = Auction.isOwner(auction.pk, request.user.pk)
    else:
        is_owner = False

    if not bids:
        maxBidPrice = auction.minPrice
    else:
        maxbid = max(bids, key=lambda b: b.price)
        maxBidPrice = maxbid.price

    if auction.isResolved():
        winner =  auction.get_highest_bid()
    else:
        winner = None
    return render(request, 'auction/auction_detail.html',
                  {'auction': auction, 'form': bidform, 'bids': bids.order_by('-price'), 'maxbid': maxBidPrice, 'is_owner': is_owner,
                   'dropdown': dropDownHTML, 'displayRate': displayRate, 'winner' : winner})

def login_view(request):
    activate(get_current_language(request))
    username = request.POST['username']
    password = request.POST['password']
    user = authenticate(username=username, password=password)
    if user is not None:
        if user.is_active:
            login(request, user)
            # init current
            request.session[settings.TEMP_CURRENCY] = "EUR"
            return HttpResponseRedirect(reverse('welcome_view'))
        else:
            messages.error(request, "User is blocked")
            return HttpResponseRedirect(reverse('welcome_view'))
    else:
        messages.error(request, "Wrong username or password")
        return HttpResponseRedirect(reverse('welcome_view'))


@login_required
def place_bid(request):
    form = BidForm(request.POST)
    auction_id = request.POST['auction_id']
    if form.is_valid():
        bid = form.save(commit=False)
        bid.auction = Auction.objects.get(pk=auction_id)
        if bid.auction.version == int(request.POST['auction_version']): #check if the auction has been modified before the user place bid
            try:
                bid_result = Bid.create(auction=bid.auction, price=bid.price, bidder=request.user)
                bid_result.notifyEmail()
                return HttpResponseRedirect(reverse('auction_detail',kwargs={'pk':auction_id}))
            except Exception,e:
                messages.error(request, str(e))
        else: #if auction has been modified, prompt error message
            messages.error(request, settings.ERROR_CONCURRENCY_MESSAGE)
    return auction_detail(request, pk=auction_id, bidform=form)


def search(request):
    activate(get_current_language(request))
    if 'str' in request.GET:
        str = request.GET['str']
        auctions = Auction.search(str)
        auctions = Auction.excludeBanned(auctions)
        return welcome_view(request, auctions)

@login_required
# this view is used for both create and edit
def create_auction(request, form=AuctionForm()):
    if request.method == "GET":
        form = form
        if form.id is not None:
            form.fields['endDate'].widget.attrs['readonly'] = True
        return render(request, 'auction/create.html', {'form': form, 'id': form.id, 'version': form.version})
    elif request.method == "POST":
        form = AuctionForm(request.POST)
        if form.is_valid():
            if 'id' in request.POST:  # editing an existing auction
                auction = Auction.objects.get(pk=form.data['id'])
                auction.version += 1 #update a new version
                form = AuctionForm(request.POST or None, instance=auction)
                form.save()
                return auction_detail(request, form.data['id'], bidform=BidForm())
            else:  # create a new auction
                auction = form.save(commit=False)
                auction.seller = request.user
                auction.state = AuctionState.active
                auction.maxPrice = auction.minPrice
                auction.checkShortDuration()
                auction.save()
                return welcome_view(request)
        return render(request, 'auction/create.html', {'form': form})

@login_required
def edit_auction(request, pk):
    if Auction.isOwner(pk, request.user.pk):
        auction = Auction.objects.get(pk=pk)
        form = AuctionForm(instance=auction, initial={'auction': auction, 'id': pk})
        form.id = pk
        form.version = auction.version
        return create_auction(request, form)
    else:
        return HttpResponseForbidden()

def resolve_auction(request, pk):
    Auction.resolve(pk=pk)
    return HttpResponseRedirect(reverse('welcome_view'))


def get_display_rate(request):
    # EUR2TEMP = EUR * USD2TEMP / USD2EURO
    if settings.TEMP_CURRENCY not in request.session:
        request.session[settings.TEMP_CURRENCY] = settings.BASE_CURRENCY
    return curr.getCurrencyDict().get(request.session[settings.TEMP_CURRENCY]) / curr.getCurrencyDict().get(
        settings.BASE_CURRENCY)

def get_current_language(request):
    if 'language' not in request.session and request.user.is_authenticated():
        return request.user.preferedLanguage
    elif 'language' not in request.session:
        return settings.DEFAULT_LANGUAGE
    else:
        return request.session['language']