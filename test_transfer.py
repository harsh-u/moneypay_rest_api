import requests
import random


def test_transaction():
    account = []
    print(account)
    users = [
        {
            "mobile": "0000000000",
            "token": "8e841bc0a20ac17ed26558d8b8a1333601b781a1",
        },
        {
            "mobile": "1111111111",
            "token": "16fd1c5701102839e83dcbd568121801b31170a3",
        },
        {
            "mobile": "2222222222",
            "token": "6acbe194fe1d2cfa2de9b59fb516069deb91300d",
        },
        {
            "mobile": "3333333333",
            "token": "4dea6b8504567634d73a68ce901bdb4b51de18d5",
        },
        {
            "mobile": "4444444444",
            "token": "f58cf8327be9cda997a39fda0994d7fc564899b3",
        },
        {
            "mobile": "5555555555",
            "token": "21fce67a4935078f6952917368d6c3245ca597b6",
        },
        {
            "mobile": "6666666666",
            "token": "0fd771a057d59b8bec05439c915c1e13a1c27ec8",
        },
        {
            "mobile": "7777777777",
            "token": "a8f378b65530202cbf1093c0d123b475cf642c9e",
        },
        {
            "mobile": "8888888888",
            "token": "0481b293473aea97ff5e068590cdea038077e864",
        },
        {
            "mobile": "9999999999",
            "token": "f29c4e39dcc9b32fd1c2f8034efd019f04acdd68",
        },

    ]

    for i in range(500):
        print(i)
        sender = random.choice(users)
        receiver = random.choice(users)
        data = {
            "sender": sender['mobile'],
            "receiver": receiver['mobile'],
            "amount": 500,
            "currency": "INR"
        }
        header = {
            "Authorization": f"Token {sender['token']}",
            "Content-Type": "application/json"
        }
        response = requests.request(method="post", json=data, url="http://localhost:8000/moneypay/transfer/",
                                    headers=header)
        print(sender)
        print(receiver)
        print(response.status_code, response.text)


test_transaction()
