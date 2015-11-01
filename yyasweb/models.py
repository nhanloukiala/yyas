from django.db import models
from decimal import *
# Create your models here.
from django.utils import timezone
from datetime import timedelta
from django.contrib.auth.models import AbstractUser
from YYAS import settings
from django.core.urlresolvers import reverse
import uuid
import pdb
from django.core.mail import send_mail


class CustomUser(AbstractUser):
    address = models.CharField(max_length=100)
    preferedLanguage = models.CharField(max_length=10, default='en')

    @classmethod
    def update_language(self, lang):
        self.preferedLanguage = lang
        self.save()


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
    startDate = models.DateTimeField(default=timezone.datetime.now())
    endDate = models.DateTimeField(null=False)
    status = models.CharField(max_length=50, default=AuctionState.active)
    version = models.IntegerField(default=0)

    def __str__(self):
        return "Seller : %s - Title : %s - minPrice : %s - maxPrice : %s - startDate : %s" % (
            self.seller.username, self.title, self.minPrice, self.maxPrice, str(self.startDate))

    @staticmethod
    def batch_resolve():
        resolvedAuctions = Auction.objects.filter(endDate__lt=timezone.datetime.now()).exclude(
            status=AuctionState.banned)
        for auction in resolvedAuctions:
            Auction.resolve(auction.pk)

    def isResolved(self):
        return self.status == AuctionState.resolved

    def checkShortDuration(self):
        tdelta = timedelta(days=settings.TIME_GAP)
        if self.endDate and self.endDate.replace(tzinfo=None) >= timezone.datetime.now() + tdelta:
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
    def get_winner(pk):
        auction = Auction.objects.get(pk=pk)
        if auction.status != AuctionState.resolved:
            return None
        else:
            return auction.get_highest_bid()

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

    # @classmethod
    # def create(self, seller, description, title, minPrice, end):
    #     start = timezone.now()
    #     if end <= start + timedelta(days=3):
    #         end = start + timedelta(days=3)
    #
    #     auc = Auction(seller=seller, description=description, title=title, minPrice=minPrice, maxPrice=minPrice,
    #                   startDate=start,
    #                   endDate=end, status=AuctionState.active)
    #     auc.save()

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
        auc = Auction.objects.get(pk=pk)
        auc.status = AuctionState.banned
        auc.save()

        aucStr = str(auc)

        send_mail(settings.BAN_BIDDER_HEADER, settings.BAN_CONTENT % aucStr, settings.EMAIL_HOST_USER,
                  Auction.get_relevant_user_email(auc.pk))
        send_mail(settings.BAN_HEADER, settings.BAN_CONTENT % aucStr, settings.EMAIL_HOST_USER,
                  [Auction.get_seller_email(auc.pk)])

        return True

    @classmethod
    def unban(self, pk):
        auc = Auction.objects.get(pk=pk)
        if auc.endDate >= timezone.now():
            auc.status = AuctionState.active
        else:
            auc.status = AuctionState.banned
        auc.save()

    @staticmethod
    def resolve(pk):
        auc = Auction.objects.get(pk=pk)
        auc.status = AuctionState.resolved
        auc.save()

        aucStr = str(auc)

        #send mail, duplicate code but too lazy at this rate to extract method :D
        send_mail(settings.RESOLVE_BIDDER_HEADER, settings.RESOLVE_CONTENT % aucStr, settings.EMAIL_HOST_USER,
                  Auction.get_relevant_user_email(auc.pk))
        send_mail(settings.RESOLVE_HEADER, settings.RESOLVE_CONTENT % aucStr, settings.EMAIL_HOST_USER,
                  [Auction.get_seller_email(auc.pk)])

    @staticmethod
    def isOwner(pk, userpk):
        return Auction.objects.filter(pk=pk).get().seller.pk == userpk

    def get_highest_bid(self, pk=None):
        if self.bid_set.all().count() > 0:
            bid = max(self.bid_set.all(), key=lambda b: b.price)
            return bid
        else:
            return Bid(price=0)


class Bid(models.Model):
    auction = models.ForeignKey(Auction)
    time = models.DateTimeField(default=timezone.now())
    price = models.DecimalField(max_digits=10, decimal_places=2)
    bidder = models.ForeignKey(settings.AUTH_USER_MODEL)

    def __unicode__(self):
        return unicode(self.price) or u''

    @staticmethod
    def create(auction, bidder, price):
        if auction.endDate.replace(tzinfo=None) <= timezone.datetime.now():
            Auction.resolve(auction.pk)
            raise Exception("Auction has dued. Better luck next time.")
        if price <= auction.get_highest_bid().price:
            raise Exception("Bid price must be higher than the latest bid")

        if auction.status in [AuctionState.banned, AuctionState.resolved]:
            raise Exception("Auction has been banned or resolved")
        if auction.seller == bidder:
            raise Exception("Owner cannot bid on his own auction")

        # soft dealine
        if auction.endDate.replace(tzinfo=None) <= timezone.datetime.now() + timedelta(minutes=5):
            auction.endDate += timedelta(minutes=5)
            auction.save()

        bid = Bid(auction=auction, bidder=bidder, price=price, )
        bid.save()

        return bid

    def __str__(self):
        return

    def notifyEmail(self):
        send_mail(settings.BID_HEADER, settings.BID_CONTENT, settings.EMAIL_HOST_USER,
                  Auction.get_relevant_user_email(self.auction.pk))
        send_mail(settings.BID_HEADER, settings.BID_CONTENT, settings.EMAIL_HOST_USER,
                  [Auction.get_seller_email(self.auction.pk)])

    def list(self):
        return Bid.objects.all()


class CustomToken(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL)
    link = models.CharField(max_length=100, default=reverse('welcome_view'))
    checked = models.BooleanField(default=False)
    tokenValue = models.CharField(max_length=64, null=False)
    created = models.DateTimeField(default=timezone.datetime.now())

    @staticmethod
    def create(user, link):
        token = CustomToken()
        token.user = user
        token.link = link
        token.tokenValue = uuid.uuid4()
        token.save()

        return token.tokenValue

    @staticmethod
    def retrieve(tokenString):
        try:
            token = CustomToken.objects.get(tokenValue=tokenString)
            if not token.checked:
                token.checked = True
                token.save()
                return token.user, token.link
            else:
                return None
        except:
            return None
