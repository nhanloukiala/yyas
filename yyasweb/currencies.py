import urllib2
import json
from decimal import Decimal
from YYAS import settings
from django.core.urlresolvers import reverse

__author__ = 'nhan'


def getCurrencyDict():
    data = json.load(urllib2.urlopen(settings.CURRENCY_FETCH_URL), parse_float=Decimal)

    ldata = data.get('rates')

    for k in ldata:
        newk = str(k)
        ldata[newk] = ldata.pop(k)

    return ldata


# list of currency that goes to top of the list
priorCurrency = ['USD', 'EUR', 'CAD', 'HKD', 'AUD', 'JPY']


def dropDownElementHelper(submitURL, nextURL):
    data = getCurrencyDict()
    tag = '<li><a href="%s?currency=%s&next=%s">%s</a></li>'

    result = ''

    # build dropdown list with priority
    for curr in priorCurrency:
        result += tag % (submitURL, curr, nextURL, curr)

    # build the rest of dropdown list
    for k in data:
        if k not in priorCurrency:
            result += tag % (submitURL, k, nextURL, k)

    return result
