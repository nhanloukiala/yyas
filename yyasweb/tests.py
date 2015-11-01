from django.test import TestCase
from django.test import Client
from rest_framework.test import APIClient
from rest_framework.authtoken.models import Token
from django.utils.translation import activate
from models import *
import threading


# Create your tests here.

class TestAuctionModel(TestCase):
    def setUp(self):
        self.user = CustomUser.objects.create_user(username='user1', email='user@gmail.com')
        self.user.set_password('123')
        self.user.save()
        self.user2 = CustomUser.objects.create_user(username='user2', password='123', email='user@gmail.com')
        self.user3 = CustomUser.objects.create_user(username='user3', password='123', email='user@gmail.com')

        self.tnow = timezone.datetime.now()
        self.tdelta = timedelta(days=2)
        self.tdelta1 = timedelta(days=3, hours=3)

        self.auction = Auction.objects.create(seller=self.user, minPrice=1, endDate=self.tnow + self.tdelta1)
        self.auction.save()

        self.bid1 = Bid(price=1.0, bidder=self.user2)
        self.bid2 = Bid(price=2.0, bidder=self.user3)
        self.bid3 = Bid(price=3.0, bidder=self.user2)

        self.auction.bid_set.add(self.bid1, self.bid2, self.bid3)

    def test_elect_winner(self):
        # test bid
        self.assertEqual(3.0, self.auction.elect().price)
        self.assertEqual(self.user2, self.auction.elect().bidder)

        self.auction.bid_set.all().delete()
        self.assertIsNone(self.auction.elect())

    def test_internationalization(self):
        for lang, h1 in [('en', 'Bidding Site'), ('vi', '123')]:
            activate(lang)
            response = self.client.get(reverse('welcome_view'))

    def test_bidding_service(self):
        user = CustomUser.objects.filter()[0]
        token = Token.objects.create(user=user)

        client = APIClient()
        resp = client.post(reverse('bid_auction', kwargs={'pk': 0}), {'price': '200.0'})
        # not authenticated
        self.assertEqual(resp.status_code, 401)

        client.credentials(HTTP_AUTHORIZATION='Token ' + token.key)

        resp = client.post(reverse('bid_auction', kwargs={'pk': 0}), {'price': '200.0'})
        # auction not existed
        self.assertEqual(resp.status_code, 404)

        resp = client.post(reverse('bid_auction', kwargs={'pk': 1}), {'price': '200.0'})
        # successful
        self.assertEqual(resp.status_code, 200)

    # Test UC3
    def test_create_auction(self):
        response = self.client.post('/auction/create/',
                                    {'title': 'my title', 'description': 'description', 'minPrice': '100.0',
                                     'endDate': '2015-12-11 12:05'})
        # redirect to login
        self.assertEqual(response.status_code, 302)

        c = Client()
        c.login(username='user1', password='123')
        # normal case
        response = c.post('/auction/create/', {'title': 'my title', 'description': 'description', 'minPrice': '100.0',
                                               'endDate': '2015-12-11 12:05'})
        self.assertEqual(response.status_code, 200)

        # null case
        response = c.post('/auction/create/', {'title': 'my title', 'description': 'description', 'minPrice': '',
                                               'endDate': '2015-12-11 12:05'})
        self.assertContains(response, "This field is required.")

        # decimal flag case
        response = c.post('/auction/create/', {'title': 'my title', 'description': 'description', 'minPrice': '100.111',
                                               'endDate': '2015-12-11 12:05'})
        self.assertContains(response, "Ensure that there are no more than 2 decimal places.")

    # Test UC3
    # if auction end date is earlier than 72 hours from now, then it's automatically assigned to 72 hours from now.
    def test_short_duration(self):
        # test duration
        self.auction.endDate = self.tnow + self.tdelta
        self.assertFalse(self.auction.checkShortDuration())

        self.auction.endDate = self.tnow + self.tdelta1
        self.assertTrue(self.auction.checkShortDuration())

    #Test UC6, UC10
    def test_bid_view(self):
        response = self.client.post('/bid/',
                                    {'auction_id': 1, 'auction_version': 0, 'price': 100})
        #UC 6 authentication
        self.assertEqual(response.status_code, 302)

        c = Client()
        c.login(username='user2', password='123')

        # normal case, redirect back to auction page after successfully bid
        response = c.post('/bid/',
                          {'auction_id': 1, 'auction_version': 0, 'price': 100})

        self.assertEqual(response.status_code, 302)

        #UC 6 case where bid price is not bigger that previous one
        response = c.post('/bid/',
                          {'auction_id': 1, 'auction_version': 0, 'price': 100})
        self.assertContains(response, 'Bid price must be higher than the latest bid')

        # UC 10 case where auction is edited before bid is place
        auction  =Auction.objects.get(pk=1)
        auction.version += 1
        auction.save()

        response = c.post('/bid/',
                          {'auction_id': 1, 'auction_version': 0, 'price': 102})
        self.assertContains(response, settings.ERROR_CONCURRENCY_MESSAGE)
