from django.db import models

# Create your models here.
from django.utils import timezone

class Auction(models.Model):
    epsilon = 0.01

    seller = models.ForeignKey('auth.User')
    title = models.CharField(max_length=200)
    minPrice = models.DecimalField(max_digits=10, decimal_places=2)
    maxPrice = models.DecimalField(max_digits=10, decimal_places=2)
    maxBid = models.DateTimeField()
    description = models.TextField()
    startDate = models.DateTimeField(timezone.now())
    endDate = models.DateTimeField(null=False)
    status = models.CharField(max_length=50)

class Bid(models.Model):
    auction = models.ForeignKey(Auction)
    time = models.DateTimeField(timezone.now())
    price = models.DecimalField(max_digits=10, decimal_places=2)
    bidder = models.ForeignKey('auth.User')


