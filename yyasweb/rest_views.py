__author__ = 'nhan'
from yyasweb.models import Auction
from yyasweb.serializers import AuctionSerializer, BidSerializer
from rest_framework.decorators import api_view, renderer_classes, authentication_classes, permission_classes
from rest_framework.authentication import BasicAuthentication, SessionAuthentication, TokenAuthentication
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.renderers import JSONRenderer
from rest_framework.parsers import JSONParser
from django.views.decorators.csrf import csrf_exempt
from rest_framework import viewsets
from django.http import HttpResponse
from rest_framework import serializers
import pdb



# class JSONResponse(HttpResponse):
#     """
#     This class is copied from the lecturer's sample
#     """
#
#     def __init__(self, data, **kwargs):
#         content = JSONRenderer().render(data)
#         kwargs['content_type'] = 'application/json'
#         super(JSONResponse, self).__init__(content, **kwargs)


itemPerPage = 10


@csrf_exempt
@api_view(['GET'])
@renderer_classes([JSONRenderer, ])
def get_auction_list(request):
    try:
        if 'str' not in request.GET:
            auctions = Auction.objects.all()
        else:
            auctions = Auction.excludeBanned(Auction.search(request.GET['str']))

        serializer = AuctionSerializer(auctions, many=True)
        return Response(serializer.data)
    except:
        return Response("data you requested is not available")


@api_view(['POST'])
@authentication_classes([BasicAuthentication, SessionAuthentication, TokenAuthentication])
@permission_classes([IsAuthenticated])
def bid_list(request, pk):
    # pdb.set_trace()

    data = request.data
    serializer = BidSerializer(data=data)

    try:
        auction = Auction.objects.get(pk=pk)
    except:
        return Response("auction not found", status=404)

    # pdb.set_trace()
    if serializer.is_valid():
        serializer.save(auction = auction, bidder = request.user)
        return Response(serializer.data, status=200)
    else:
        return Response(serializer.errors, status=404)
