__author__ = 'nhan'
from rest_framework import serializers
from yyasweb.models import Auction, Bid

class AuctionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Auction
        fields = ['title', 'minPrice' , 'maxPrice', 'version', 'endDate']

class BidSerializer(serializers.ModelSerializer):
    class Meta:
        model = Bid
        fields = ['price']