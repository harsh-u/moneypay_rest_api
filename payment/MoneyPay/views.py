import datetime
import time
from datetime import timedelta
from django.utils import timezone
from django.conf import settings
from django.contrib.auth import get_user_model, login, authenticate
from django.shortcuts import render
from django.contrib.auth.models import User, Group
from rest_framework import viewsets, serializers, generics
from rest_framework import permissions
from django.contrib.auth.decorators import login_required
from rest_framework.authentication import SessionAuthentication, BasicAuthentication, TokenAuthentication
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.status import HTTP_404_NOT_FOUND, HTTP_400_BAD_REQUEST, HTTP_200_OK
from rest_framework.views import APIView
from .models import Account, Balance, Transactions
from .serializers import UserSerializer, GroupSerializer, RegisterSerializer
from rest_framework import status
from rest_framework.decorators import api_view, authentication_classes, permission_classes
from rest_framework.response import Response
import re
from rest_framework.authtoken.models import Token

# from snippets.models import Snippet
# from snippets.serializers import SnippetSerializer
User = get_user_model()


def index(request):
    return render(request, "MoneyPay/index.html")


class RegisterView(generics.CreateAPIView):
    queryset = User.objects.all()
    permission_classes = (AllowAny,)
    serializer_class = RegisterSerializer


class UserloginSerializer(serializers.Serializer):
    username = serializers.CharField(required=True)
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
def register(request):
    if request.method == 'POST':
        serializer = RegisterSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            phone_number = serializer.data['phone_number']
            user = User.objects.get(phone_number=phone_number)
            account = Account(user=user, current_status='Active')
            account.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    return Response("Invalid Request")


@api_view(['GET', 'POST'])
@permission_classes((AllowAny,))  # here we specify permission by default we set IsAuthenticated
def login(request):
    if request.method == 'POST':
        login_serializer = UserloginSerializer(data=request.data)

        if not login_serializer.is_valid():
            return Response(login_serializer.errors, status=HTTP_400_BAD_REQUEST)

        # print(login_serializer.data)
        user_name = login_serializer.data['username']
        password = login_serializer.data['password']

        user = User.objects.get(username=user_name)

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

                        # new_balance_sender = Balance.objects.filter(account=account_sender).first().balance
                        # new_balance_receiver = Balance.objects.filter(account=account_receiver).first().balance

                        return Response("valid till Now")
    return Response("InValid request")
