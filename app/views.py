import imp
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import login, authenticate
from django.shortcuts import render, redirect
from django.core.exceptions import ObjectDoesNotExist

from random import random
from django.contrib.auth.hashers import check_password, make_password
from django.contrib import auth
from django.contrib.auth.models import User
from django.utils.http import urlsafe_base64_decode
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode
from django.template.loader import render_to_string
import smtplib
import socket
from django.shortcuts import get_object_or_404
from django.views.generic.edit import FormView
from django.contrib import messages
from django.http import HttpResponse
from django.views import View
from django.views.generic.base import TemplateView
from django.http import HttpResponseRedirect
import os
import base64
from django.forms import ModelForm
from django.conf import settings
from django import forms
import datetime
from django.contrib.auth.decorators import login_required
from random import random
from django.core.paginator import Paginator,PageNotAnInteger,EmptyPage
from django.template import loader
from django.http import JsonResponse
from django.urls import reverse_lazy
from django.core.mail import send_mail
from ipware import get_client_ip
import geoip2.database
import requests
import json
from paystackapi.paystack import Paystack
from paystackapi.transaction import Transaction
from paystackapi.verification import Verification
paystack_secret_key = "sk_test_e6c40e9e83237dbb32096831467c6e6193a970cb"
paystack = Paystack(secret_key=paystack_secret_key)
from app import models as cmodels



def customers_list(request):
    customers = cmodels.Customer.objects.all()
    data = {"results": list(customers.values("user",))}
    return JsonResponse(data)


def customer_detail(request,id):
    customers = cmodels.Customer.objects.get(user_id=id)
    data = {"results": list(customers.values("user",))}
    return JsonResponse(data)




