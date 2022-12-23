from django.contrib.auth import get_user_model, login
from django.shortcuts import render
from django.contrib.auth.models import User, Group
from rest_framework import viewsets
from rest_framework import permissions
from django.contrib.auth.decorators import login_required
from rest_framework.authentication import SessionAuthentication, BasicAuthentication
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView
from .models import Account, Balance, Transactions
from .serializers import UserSerializer, GroupSerializer
from rest_framework import status
from rest_framework.decorators import api_view, authentication_classes, permission_classes
from rest_framework.response import Response
import re


# from snippets.models import Snippet
# from snippets.serializers import SnippetSerializer


def index(request):
    return render(request, "MoneyPay/index.html")


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


@api_view(['GET', 'POST'])
@authentication_classes([SessionAuthentication, BasicAuthentication])
@permission_classes([IsAuthenticated])
def transfer(self, request):
    if request.method == 'POST':
        print("INSIDE POST")
        sender = request.data.get("sender")
        receiver = request.data.get("receiver")
        amount = request.data.get("amount")
        currency = request.data.get("currency")

        user = get_user_model()

        user_sender = user.objects.get(phone_number=sender)
        user_receiver = user.objects.get(phone_number=receiver)
        if not user_sender and user_receiver:
            return Response("user not exist")
        else:
            print(user_sender)
            print(user_receiver)
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

                        print("I am here")
                        new_balance_sender = Balance.objects.filter(account=account_sender).first().balance
                        new_balance_receiver = Balance.objects.filter(account=account_receiver).first().balance
                        print(new_balance_sender)
                        print(new_balance_receiver)

                        return Response("valid till Now")
    return Response("InValid request")
