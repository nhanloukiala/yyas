from django.db import models
from django.db.models import Max
# Create your models here.
from django.utils import timezone
from datetime import timedelta
from django.contrib.auth.models import AbstractUser
from YYAS import settings
import pdb
import emails


class CustomUser(AbstractUser):
    address = models.CharField(max_length=100)


class AuctionState:
    active = 'active'
    banned = 'banned'
    resolved = 'resolved'


class Auction(models.Model):
    epsilon = 0.01

    seller = models.ForeignKey(settings.AUTH_USER_MODEL)
    title = models.CharField(max_length=200)
    minPrice = models.DecimalField(max_digits=10, decimal_places=2)
    maxPrice = models.DecimalField(max_digits=10, decimal_places=2, default=10.0)
    maxBidId = models.CharField(max_length=20, default='')
    description = models.TextField()
    startDate = models.DateTimeField(default=timezone.now())
    endDate = models.DateTimeField(null=False)
    status = models.CharField(max_length=50, default=AuctionState.active)

    def __str__(self):
        return "Seller : %s - Title : %s - minPrice : %s - maxPrice : %s - startDate : %s" % (
            self.seller.username, self.title, self.minPrice, self.maxPrice, str(self.startDate))

    @staticmethod
    def batch_resolve():
        resolvedAuctions = Auction.objects.filter(enddate__lt=timezone.now()).exclude(status=AuctionState.banned)
        for auction in resolvedAuctions:
            auction.resolve()

    def checkShortDuration(self):
        tdelta = timedelta(days=settings.TIME_GAP)
        if self.endDate and self.endDate >= timezone.datetime.now() + tdelta:
            return True
        else:
            self.endDate = timezone.datetime.now() + tdelta
            return False

    def elect(self):
        if self.status == AuctionState.active and Auction.objects.get(pk=self.pk).bid_set.count() > 0:
            return Auction.objects.get(pk=self.pk).bid_set.order_by('-price')[0]
        else:
            return None

    @staticmethod
    def get_relevant_user_email(pk):
        userList = []
        if pk is None:
            return userList

        listBid = Auction.objects.get(pk=pk).bid_set.all()

        for bid in listBid:
            userList.append(bid.bidder.email)

        return userList

    @staticmethod
    def get_seller_email(pk):
        return Auction.objects.get(pk=pk).seller.email

    @property
    def isActive(self):
        return self.status == AuctionState.active

    @property
    def isBanned(self):
        return self.status == AuctionState.banned

    @staticmethod
    def search(str):
        return Auction.objects.filter(title__icontains=str)

    @staticmethod
    def exists(pk):
        return Auction.objects.filter(pk=pk).count() > 0

    @classmethod
    def excludeBanned(self, auctions):
        return auctions.exclude(status=AuctionState.banned)

    @classmethod
    def create(self, seller, description, title, minPrice, end):
        start = timezone.now()
        if end <= start + timedelta(days=3):
            end = start + timedelta(days=3)

        auc = Auction(seller=seller, description=description, title=title, minPrice=minPrice, maxPrice=minPrice,
                      startDate=start,
                      endDate=end, status=AuctionState.active)
        auc.save()

    @classmethod
    def listAuction(self):
        return Auction.objects.all()

    @staticmethod
    def get(pk):
        return Auction.objects.get(pk=pk)

    @classmethod
    def delete(self, pk):
        Auction.objects.get(pk=pk).delete()

    @classmethod
    def edit(self, pk, description):
        auc = Auction.objects.get(pk=pk)
        auc.description = description
        auc.save()

    @classmethod
    def ban(self, pk):
        if not self.exists(pk):
            return False
        try:
            auc = Auction.objects.get(pk=pk)
            auc.status = AuctionState.banned
            auc.save()

            aucStr = str(auc)
            emails.sendMail(settings.BAN_BIDDER_HEADER, settings.BAN_CONTENT % aucStr,
                            Auction.get_relevant_user_email(auc.pk))
            emails.sendMail(settings.BAN_HEADER, settings.BAN_CONTENT % aucStr, Auction.get_seller_email(auc.pk))

            return True
        except:
            return False

    @classmethod
    def unban(self, pk):
        auc = Auction.objects.get(pk=pk)
        if auc.endDate >= timezone.now():
            auc.status = AuctionState.active
        else:
            auc.status = AuctionState.banned
        auc.save()

    @classmethod
    def resolve(self, pk=None):
        if pk is None:
            pk = self.pk

        auc = Auction.objects.get(pk=pk)
        auc.status = AuctionState.resolved
        auc.save()

        aucStr = str(auc)
        emails.sendMail(settings.RESOLVE_BIDDER_HEADER, settings.RESOLVE_CONTENT % aucStr,
                        Auction.get_relevant_user_email(auc.pk))
        emails.sendMail(settings.RESOLVE_HEADER, settings.RESOLVE_CONTENT % aucStr, Auction.get_seller_email(auc.pk))

    @staticmethod
    def isOwner(pk, userpk):
        return Auction.objects.filter(pk=pk).get().seller.pk == userpk

    def get_highest_bid(self, pk):
        bid = max(self.bid_set, key=lambda b: b.price)
        return bid


class Bid(models.Model):
    auction = models.ForeignKey(Auction)
    time = models.DateTimeField(default=timezone.now())
    price = models.DecimalField(max_digits=10, decimal_places=2)
    bidder = models.ForeignKey(settings.AUTH_USER_MODEL)

    def create(self, auction, bidder, price):
        auc = Bid(auction=auction, bidder=bidder, price=price, )

    def __str__(self):
        return

    def list(self):
        return Bid.objects.all()
