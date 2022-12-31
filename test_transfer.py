import requests
import random


def test_transaction():
    account = []
    print(account)
    users = [
        {
            "mobile": "1111111111",
            "token": "df125d368f7229868a5b01b594d1407ee5434943",
        },
        {
            "mobile": "9999999999",
            "token": "eedcd0fd3031ae9a45d98948137d566bc3f3884f",
        },
    ]

    for i in range(500):
        print(i)
        sender = random.choice(users)
        receiver = random.choice(users)
        data = {
            "sender": sender['mobile'],
            "receiver": receiver['mobile'],
            "amount": 2,
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
