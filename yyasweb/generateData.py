__author__ = 'nhan'
from models import *
import random as r
import decimal
from datetime import timedelta
import time
from django.utils import timezone

def generateRandomData():
    for x in range(50):
        user = CustomUser.objects.create(username="user" + str(x), email="user" + str(x) + "@gmail.com",
                                         preferedLanguage=r.choice(['en', 'vi']))
        user.set_password("123456")
        user.save()

    for x in range(50):
        #random pick an user
        user = CustomUser.objects.order_by('?').first()

        #create auction
        auction = Auction()
        auction.title = "Title no " + str(x)
        auction.description = "Description"
        auction.seller = user
        auction.state = AuctionState.active
        auction.endDate = timezone.datetime.now() + timedelta(days=r.randint(0,28),minutes=r.randint(0,60))
        auction.minPrice = round(decimal.Decimal(str(r.random())),2)
        auction.maxPrice = auction.minPrice
        auction.checkShortDuration()
        auction.save()


    for auction in Auction.objects.all():
        try:
            #random pick an user
            user = CustomUser.objects.order_by('?').first()
            for x in range(1,5):
                Bid.create(auction=auction, price= round(auction.get_highest_bid().price + decimal.Decimal(str(r.random())),2), bidder=user)
        except Exception,e:
            print str(e)
