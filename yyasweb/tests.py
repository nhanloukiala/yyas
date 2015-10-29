from django.test import TestCase
from django.test import Client
from django.core.urlresolvers import reverse
from django.utils import timezone
from datetime import timedelta
from django.contrib.auth.models import User
from models import *
import mock
# Create your tests here.

class TestAuctionModel(TestCase):
    def setUp(self):
        self.user = CustomUser.objects.create_user(username='user1',password='123',email='user@gmail.com')
        self.user2 = CustomUser.objects.create_user(username='user2',password='123',email='user@gmail.com')
        self.user3 = CustomUser.objects.create_user(username='user3',password='123',email='user@gmail.com')

        self.tnow = timezone.datetime.now()
        self.tdelta = timedelta(days=2)
        self.tdelta1 = timedelta(days=3, hours=3)

        self.auction = Auction.objects.create(seller = self.user, minPrice = 1, endDate = self.tnow + self.tdelta1)
        self.auction.save()

        self.bid1 = Bid(price = 1.0, bidder = self.user2)
        self.bid2 = Bid(price = 2.0, bidder = self.user3)
        self.bid3 = Bid(price = 3.0, bidder = self.user2)

        self.auction.bid_set.add(self.bid1, self.bid2, self.bid3)

    def test_short_duration(self):
        #test duration
        self.auction.endDate = self.tnow + self.tdelta
        self.assertFalse(self.auction.checkShortDuration())

        self.auction.endDate = self.tnow + self.tdelta1
        self.assertTrue(self.auction.checkShortDuration())

    def test_elect_winner(self):
        #test bid
        self.assertEqual(3.0,self.auction.elect().price)
        self.assertEqual(self.user2, self.auction.elect().bidder)

        self.auction.bid_set.all().delete()
        self.assertIsNone(self.auction.elect())

    def test_get_relevant_user(self):
        print Auction.get_relevant_user_email(self.auction.pk)


