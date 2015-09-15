from django.test import TestCase
from django.test import Client
from django.core.urlresolvers import reverse
# Create your tests here.

c = Client()
response = c.post(reverse('login'), {'username':'nhan', 'password':'conchimnon'})
print response.status_code

response = c.get(reverse('auction_list'))

response = c.post(reverse('create_auction'), {'title':'123', 'minPrice':'123', 'description':'1232', 'endDate':'2015-09-12'})

