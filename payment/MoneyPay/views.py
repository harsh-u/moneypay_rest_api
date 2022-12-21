from django.contrib.auth import get_user_model
from django.shortcuts import render
from django.contrib.auth.models import User, Group
from rest_framework import viewsets
from rest_framework import permissions

from .models import Account, Balance
from .serializers import UserSerializer, GroupSerializer
from rest_framework import status
from rest_framework.decorators import api_view
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
def transfer(request):
    if request.method == 'GET':
        print("I am in Get")
        return Response("Not a valid request", status=status.HTTP_400_BAD_REQUEST)

    elif request.method == 'POST':
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
                balance_sender = Balance.objects.filter(account=account_sender).first().get_balance()
                balance_receiver = Balance.objects.filter(account=account_receiver).first().get_balance()
                if balance_sender < int(amount):
                    return Response("Insufficient Balance")
                else:
                    print(balance_sender)
                    print(balance_receiver)
                    amt_credited = Balance(account=account_receiver, amt_credit=amount, amt_debit=0, currency="INR")
                    amt_debited = Balance(account=account_sender, amt_credit=0, amt_debit=amount, currency="INR")
                    amt_credited.save()
                    amt_debited.save()

                    new_balance_sender = Balance.objects.filter(account=account_sender).first().get_balance()
                    new_balance_receiver = Balance.objects.filter(account=account_receiver).first().get_balance()
                    print(new_balance_sender)
                    print(new_balance_receiver)

                    return Response("valid till Now")

        # print(sender)
        # print(receiver)
        # print(amount)
        # print(currency)
        return Response("Valid request")
