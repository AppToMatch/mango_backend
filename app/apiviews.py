from django.http import JsonResponse
from rest_framework.views import APIView
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from general.apiviews import getsender, getfilters, getkeys
from .models import *
from .serializers import *
from django.contrib.auth.models import AnonymousUser, User
from rest_framework import generics,viewsets,status
from app import serializers, views
from paystackapi.paystack import Paystack
from paystackapi.transaction import Transaction
from paystackapi.verification import Verification
paystack_secret_key = "sk_test_e6c40e9e83237dbb32096831467c6e6193a970cb"
paystack = Paystack(secret_key=paystack_secret_key)



def verifypayment(reference,):
    notconnected = True
    while notconnected:
        try:
            verification_response = Transaction.verify(reference=reference)
            notconnected = False
        except Exception:
            pass
    if verification_response['status']:
        return True
    else:
        return False


