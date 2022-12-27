import datetime
import time
from datetime import timedelta
from django.utils import timezone
from django.conf import settings
from django.contrib.auth import get_user_model, login, authenticate
from django.shortcuts import render
from django.contrib.auth.models import User, Group
from rest_framework import viewsets, serializers
from rest_framework import permissions
from django.contrib.auth.decorators import login_required
from rest_framework.authentication import SessionAuthentication, BasicAuthentication, TokenAuthentication
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.status import HTTP_404_NOT_FOUND, HTTP_400_BAD_REQUEST, HTTP_200_OK
from rest_framework.views import APIView
from .models import Account, Balance, Transactions
from .serializers import UserSerializer, GroupSerializer
from rest_framework import status
from rest_framework.decorators import api_view, authentication_classes, permission_classes
from rest_framework.response import Response
import re
from rest_framework.authtoken.models import Token


# from snippets.models import Snippet
# from snippets.serializers import SnippetSerializer


def index(request):
    return render(request, "MoneyPay/index.html")


class UserloginSerializer(serializers.Serializer):
    username = serializers.CharField(required=True)
    password = serializers.CharField(required=True)


class UserViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows users to be viewed or edited.
    """
    user = get_user_model()
    queryset = user.objects.all().order_by('-date_joined')
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
@permission_classes((AllowAny,))  # here we specify permission by default we set IsAuthenticated
def login(request):
    if request.method == 'POST':
        User = get_user_model()
        login_serializer = UserloginSerializer(data=request.data)
        # print(login_serializer)
        if not login_serializer.is_valid():
            return Response(login_serializer.errors, status=HTTP_400_BAD_REQUEST)

        # print(login_serializer.data)
        user_name = login_serializer.data['username']
        password = login_serializer.data['password']
        print(user_name)
        print(password)
        user = User.objects.get(username=user_name)
        print(user, user.check_password(password))

        if not user or not user.check_password(password):
            return Response({'detail': 'Invalid Credentials or activate account'}, status=HTTP_404_NOT_FOUND)

        # TOKEN STUFF
        token, _ = Token.objects.get_or_create(user=user)
        print(token)
        # token_expire_handler will check, if the token is expired it will generate new one
        is_expired, token = token_expire_handler(token)

        user_serialized = UserSerializer(user)

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
        print("INSIDE POST")
        print("Iam here", request.user)
        sender = request.data.get("sender")
        receiver = request.data.get("receiver")
        amount = request.data.get("amount")
        currency = request.data.get("currency")

        user = get_user_model()

        print(sender)
        user_sender = user.objects.get(phone_number=sender)

        # token = Token.objects.create(user=user_sender)
        # print(token.key)

        if not (user_sender == request.user or request.user.is_superuser):
            return Response("You are not authorized to make this transaction")
        user_receiver = user.objects.get(phone_number=receiver)
        if not user_sender and user_receiver:
            return Response("user not exist")
        else:
            print(user_sender)
            print(user_receiver)
            account_sender = Account.objects.filter(user=user_sender).first()
            account_receiver = Account.objects.filter(user=user_receiver).first()
            print("accounts", account_sender, account_receiver)
            if account_sender is None or account_receiver is None:
                return Response("Users account does not exist")
            else:
                exists = Balance.objects.filter(account=account_sender).exists()
                if not exists:
                    balance = Balance(account=account_sender, balance=0.00, currency="INR")
                    balance.save()
                else:
                    balance = Balance.objects.filter(account=account_sender).first()
                if balance.balance < int(amount):
                    return Response("Insufficient Balance")
                else:
                    amount = int(amount)

                    exists = Balance.objects.filter(account=account_sender).exists()
                    if not exists:
                        balance = Balance(account=account_sender, balance=0.00, currency="INR")
                        balance.save()
                    else:
                        Transactions(sender=account_sender, receiver=account_receiver, amount=amount).save()
                        sender_account = Balance.objects.filter(account=account_sender).first()
                        sender_account.balance -= amount
                        sender_account.save()

                        Transactions(sender=account_receiver, receiver=account_sender, amount=-1 * amount).save()
                        exists = Balance.objects.filter(account=account_receiver).exists()
                        if not exists:
                            balance = Balance(account=account_receiver, balance=0.00, currency="INR")
                            balance.save()
                        receiver_account = Balance.objects.filter(account=account_receiver).first()
                        receiver_account.balance += amount
                        receiver_account.save()

                        print("I am here")
                        new_balance_sender = Balance.objects.filter(account=account_sender).first().balance
                        new_balance_receiver = Balance.objects.filter(account=account_receiver).first().balance
                        print(new_balance_sender)
                        print(new_balance_receiver)

                        return Response("valid till Now")
    return Response("InValid request")


@api_view(['GET', 'POST'])
def snippet_list(request):
    """
    List all code snippets, or create a new snippet.
    """
    if request.method == 'GET':
        print("I am in Get")
        user = get_user_model()
        users = user.objects.all().order_by('-date_joined')
        serializer = UserSerializer(users, many=True)
        return Response(serializer.data)

    elif request.method == 'POST':
        print(request.data)
        is_valid = check_user_data(request.data)
        if not is_valid:
            return Response("Not a valid user", status=status.HTTP_400_BAD_REQUEST)
        serializer = UserSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


def check_user_data(user_data):
    username = user_data.get("username")
    regex = '[a-zA-z0-9]$'
    if len(username) > 4:
        if re.search(regex, username):
            return True
        else:
            print("Not in correct format")
            return False
    print("username length is too small")
    return False
