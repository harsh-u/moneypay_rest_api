from datetime import timedelta
import requests
from django.conf import settings
from django.contrib.auth import get_user_model, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User, Group
from django.db import transaction
from django.shortcuts import render, redirect
from django.utils import timezone
from rest_framework import permissions
from rest_framework import status
from rest_framework import viewsets, serializers, generics
from rest_framework.authentication import SessionAuthentication, TokenAuthentication
from rest_framework.authtoken.models import Token
from rest_framework.decorators import api_view, authentication_classes, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.status import HTTP_404_NOT_FOUND, HTTP_400_BAD_REQUEST, HTTP_200_OK
from .models import Account, Balance, Transactions
from .serializers import UserSerializer, GroupSerializer, RegisterSerializer
from django.contrib.auth import login as auth_login
from django.contrib.auth import logout as user_logout
from rest_framework.authentication import SessionAuthentication, BasicAuthentication

import razorpay
from django.views.decorators.csrf import csrf_exempt
from django.http import HttpResponseBadRequest

User = get_user_model()

razorpay_client = razorpay.Client(
    auth=(settings.RAZOR_KEY_ID, settings.RAZOR_KEY_SECRET))


class CsrfExemptSessionAuthentication(SessionAuthentication):

    def enforce_csrf(self, request):
        return


def error_page(request):
    return render(request, "MoneyPay/error.html")


def index(request):
    return render(request, "MoneyPay/index.html")


def signup(request):
    return render(request, "MoneyPay/register.html")


def signin(request):
    return render(request, "MoneyPay/signin.html")


def money_transfer(request):
    return render(request, "MoneyPay/money_transfer.html")


def add_money(request):
    return render(request, "MoneyPay/add_money.html")


def add_to_razorpay(request):
    currency = 'INR'
    amount = int(request.POST.get("amount")) * 100 # Rs. 200
    # amount  = int(amount*100)

    # Create a Razorpay Order
    razorpay_order = razorpay_client.order.create(dict(amount=amount,
                                                       currency=currency,
                                                       payment_capture='0'))

    # order id of newly created order.
    razorpay_order_id = razorpay_order['id']
    callback_url = 'paymenthandler/'

    # we need to pass these details to frontend.
    context = {}
    context['razorpay_order_id'] = razorpay_order_id
    context['razorpay_merchant_key'] = settings.RAZOR_KEY_ID
    context['razorpay_amount'] = int(amount/100)
    context['currency'] = currency
    context['callback_url'] = callback_url

    return render(request, 'MoneyPay/razorpay_index.html', context=context)


@csrf_exempt
def paymenthandler(request):
    # only accept POST request.
    if request.method == "POST":
        try:

            # get the required parameters from post request.
            payment_id = request.POST.get('razorpay_payment_id', '')
            razorpay_order_id = request.POST.get('razorpay_order_id', '')
            signature = request.POST.get('razorpay_signature', '')

            params_dict = {
                'razorpay_order_id': razorpay_order_id,
                'razorpay_payment_id': payment_id,
                'razorpay_signature': signature
            }
            print(params_dict)
            # print(amount)

            # verify the payment signature.
            result = razorpay_client.utility.verify_payment_signature(
                params_dict)
            # print(result)
            if result is not None:

                amount = 20000  # Rs. 200
                try:
                    # capture the payemt
                    razorpay_client.payment.capture(payment_id, amount)

                    user = request.user
                    print(user)
                    user_account = Account.objects.filter(user=user).first()
                    print(user_account)
                    user_balance = Balance.objects.filter(account=user_account).first()
                    print(user_balance.balance)
                    money = int(amount/100)
                    user_balance.balance += money
                    print(user_balance.balance)
                    user_balance.save()

                    # render success page on successful caputre of payment
                    return render(request, 'MoneyPay/paymentsuccess.html')
                except:

                    # if there is an error while capturing payment.
                    return render(request, 'MoneyPay/paymentfail.html')
            else:

                # if signature verification fails.
                return render(request, 'MoneyPay/paymentfail.html')
        except:

            # if we don't find the required parameters in POST data
            return HttpResponseBadRequest()
    else:

        # if other than POST request is made.
        return HttpResponseBadRequest()


@login_required
def logout(request):
    request.user.auth_token.delete()
    user_logout(request)
    return redirect('/moneypay/home/')


def user_transaction(request):
    print(request.user)
    user = request.user
    account = Account.objects.get(user=user)
    transactions = Transactions.objects.filter(receiver=account)
    data = {
        "transactions": transactions,
    }
    return render(request, "MoneyPay/user_transaction.html", data)


def send_money(request):
    sender = request.user.phone_number
    receiver = request.POST.get("phone_number")
    amount = request.POST.get("amount")
    amount = int(amount)
    currency = request.POST.get("currency")

    data = {
        "sender": sender,
        "receiver": receiver,
        "amount": amount,
        "currency": currency
    }

    user = User.objects.get(phone_number=sender)
    token = Token.objects.get(user=user)

    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Token {token}"
    }
    url = "http://localhost:8000/moneypay/transfer/"
    response = requests.post(url, json=data, headers=headers)
    if response.status_code == 200:
        return render(request, "MoneyPay/success.html")
    elif response.status_code == 400:
        return render(request, "MoneyPay/error.html")
    else:
        return render(request, "MoneyPay/error.html")


def profile(request):
    # print(request.user)
    return render(request, "MoneyPay/user_profile.html")


def user_registration(request):
    phone_number = request.POST.get("phone_number")
    email = request.POST.get("email")
    first_name = request.POST.get("first_name")
    last_name = request.POST.get("last_name")
    password = request.POST.get("password")
    password2 = request.POST.get("password2")

    data = {
        "phone_number": phone_number,
        "email": email,
        "first_name": first_name,
        "last_name": last_name,
        "password": password,
        "password2": password2
    }
    print(data)
    headers = {"Content-Type": "application/json"}
    url = "http://localhost:8000/moneypay/register/"
    response = requests.post(url, json=data, headers=headers)
    if response.status_code == 201:
        return redirect('/moneypay/signin/')
    else:
        return render(request, "MoneyPay/error.html")


def user_profile(request):
    phone_number = request.POST.get("phone_number")
    password = request.POST.get("password")
    # print(phone_number)
    # print(password)
    data = {"phone_number": phone_number, "password": password}
    headers = {"Content-Type": "application/json"}
    url = "http://localhost:8000/moneypay/login/"
    response = requests.post(url, json=data, headers=headers)
    # print(response.status_code)

    user = User.objects.get(phone_number=phone_number)
    account = Account.objects.filter(user=user).first()
    balance = Balance.objects.filter(account=account)[0]
    # print(user)
    # print(account)
    # print(balance)

    # print(balance.balance)
    auth_login(request, user)
    # print(request.user)

    data = {'user': user, 'balance': balance}
    print(balance)
    print(balance.balance)

    if response.status_code == 200:
        # return render(request, "MoneyPay/user_profile.html", data)
        # TODO balance is not reflecting into the templates
        return redirect('/moneypay/profile/', data)
    else:
        return render(request, "MoneyPay/error.html")


class RegisterView(generics.CreateAPIView):
    queryset = User.objects.all()
    permission_classes = (AllowAny,)
    serializer_class = RegisterSerializer


class UserloginSerializer(serializers.Serializer):
    phone_number = serializers.CharField(required=True)
    password = serializers.CharField(required=True)


class UserViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows users to be viewed or edited.
    """

    queryset = User.objects.all().order_by('-date_joined')
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAuthenticated]


class GroupViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows groups to be viewed or edited.
    """
    queryset = Group.objects.all()
    serializer_class = GroupSerializer
    permission_classes = [permissions.IsAuthenticated]


# def transfer_detail():
#     return None


def expires_in(token):
    # print(token.created)
    # print(datetime.datetime.now())
    # print(int(time.time()))

    time_elapsed = timezone.now() - token.created
    left_time = timedelta(seconds=settings.TOKEN_EXPIRED_AFTER_SECONDS) - time_elapsed
    return left_time


# token checker if token expired or not
def is_token_expired(token):
    return expires_in(token) < timedelta(seconds=0)


# if token is expired new token will be established
# If token is expired then it will be removed
# and new one with different key will be created
def token_expire_handler(token):
    is_expired = is_token_expired(token)
    if is_expired:
        token.delete()
        token = Token.objects.create(user=token.user)
    return is_expired, token


@api_view(['GET', 'POST'])
@permission_classes([])
@authentication_classes([CsrfExemptSessionAuthentication])
def register(request):
    if request.method == 'POST':
        serializer = RegisterSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            phone_number = serializer.data['phone_number']
            user = User.objects.get(phone_number=phone_number)
            account = Account(user=user, current_status='Active')
            account.save()
            balance = Balance(account=account, balance=0.00, currency='INR')
            balance.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    return Response("Invalid Request")


@api_view(['GET', 'POST'])
@permission_classes((AllowAny,))  # here we specify permission by default we set IsAuthenticated
@authentication_classes([CsrfExemptSessionAuthentication])
def login(request):
    if request.method == 'POST':
        login_serializer = UserloginSerializer(data=request.data)

        if not login_serializer.is_valid():
            return Response(login_serializer.errors, status=HTTP_400_BAD_REQUEST)

        # print(login_serializer.data)
        phone_number = login_serializer.data['phone_number']
        password = login_serializer.data['password']

        user = User.objects.get(phone_number=phone_number)

        if not user or not user.check_password(password):
            return Response({'detail': 'Invalid Credentials or activate account'}, status=HTTP_404_NOT_FOUND)

        # TOKEN STUFF
        token, _ = Token.objects.get_or_create(user=user)
        print(token)
        # token_expire_handler will check, if the token is expired it will generate new one
        is_expired, token = token_expire_handler(token)

        user_serialized = UserSerializer(user)
        # return render(request, "MoneyPay/user_profile.html")

        return Response({
            'user': user_serialized.data,
            'expires_in': expires_in(token),
            'token': token.key
        }, status=HTTP_200_OK)
    return Response("Invalid Request")


@api_view(['Get', 'POST'])
@authentication_classes([SessionAuthentication, TokenAuthentication])
def transfer(request):
    if request.method == 'POST':
        # print(request.user)

        sender = request.data.get("sender")
        receiver = request.data.get("receiver")
        amount = request.data.get("amount")
        currency = request.data.get("currency")

        user_sender = User.objects.get(phone_number=sender)

        if not (user_sender == request.user or request.user.is_superuser):
            return Response("You are not authorized to make this transaction")
        user_receiver = User.objects.get(phone_number=receiver)
        if not user_sender and user_receiver:
            return Response("user not exist")
        else:

            account_sender = Account.objects.filter(user=user_sender).first()
            account_receiver = Account.objects.filter(user=user_receiver).first()
            if account_sender == account_receiver:
                return Response("You can not send money to yourself")
            if account_sender is None or account_receiver is None:
                return Response("Users account does not exist")
            else:

                with  transaction.atomic():
                    sender_balance = Balance.objects.select_for_update().get(account=account_sender)
                    receiver_balance = Balance.objects.select_for_update().get(account=account_receiver)
                    print(account_receiver, account_sender)
                    if sender_balance.balance > amount:
                        sender_balance.balance -= amount
                        receiver_balance.balance += amount
                        receiver_balance.save()
                        sender_balance.save()
                        Transactions(sender=account_sender, receiver=account_receiver, amount=amount).save()
                        Transactions(sender=account_receiver, receiver=account_sender, amount=-1 * amount).save()
                        return Response(status=HTTP_200_OK)
                    else:
                        error = "Insufficient Balance"
                        return Response({
                            "error": error
                        }, status=HTTP_404_NOT_FOUND)

    return Response("Invalid Request")
