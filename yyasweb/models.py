from django.db import models

# Create your models here.
from django.utils import timezone
from datetime import datetime, timedelta
from django.forms import ModelForm


class Auction(models.Model):
    epsilon = 0.01

    seller = models.ForeignKey('auth.User')
    title = models.CharField(max_length=200)
    minPrice = models.DecimalField(max_digits=10, decimal_places=2)
    maxPrice = models.DecimalField(max_digits=10, decimal_places=2)
    maxBidId = models.CharField(max_length=20, default='')
    description = models.TextField()
    startDate = models.DateTimeField(timezone.now())
    endDate = models.DateTimeField(null=False)
    status = models.CharField(max_length=50)

    def __str__(self):
        return "Seller : %s - Title : %s - minPrice : %s - maxPrice : %s - startDate : %s" % (
            self.seller.username, self.title, self.minPrice, self.maxPrice, str(self.startDate))

    @staticmethod
    def create(self, seller, description, title, minPrice, end):
        start = timezone.now()
        if end <= start + timedelta(days=3):
            end = start + timedelta(days=3)

        auc = Auction(seller=seller, description=description, title=title, minPrice=minPrice, maxPrice=minPrice,
                      startDate=start,
                      endDate=end, status=AuctionState.active)

        auc.save()

    @staticmethod
    def listAuction():
        return Auction.objects.all()

    @staticmethod
    def delete(self, pk):
        Auction.objects.get(pk=pk).delete()

    @staticmethod
    def edit(self, pk, description):
        auc = Auction.objects.get(pk=pk)
        auc.description = description
        auc.save()


class Bid(models.Model):
    auction = models.ForeignKey(Auction)
    time = models.DateTimeField(timezone.now())
    price = models.DecimalField(max_digits=10, decimal_places=2)
    bidder = models.ForeignKey('auth.User')

    def create(self, auction, bidder, price):
        auc = Bid(auction=auction, bidder=bidder, price=price, )

    def __str__(self):
        return

    def list(self):
        return Bid.objects.all()


class AuctionState:
    active = 'active'
    banned = 'banned'
    resolved = 'resolved'


class AuctionForm(ModelForm):
    class Meta:
        model = Auction
        fields = ('title', 'minPrice', 'description', 'endDate',)
