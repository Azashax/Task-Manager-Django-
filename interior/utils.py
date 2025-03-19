import requests


def request_telegram_bot(data, username):
    url = f"https://api.telegram.org/bot6350257283:AAEjPsy5WenJHduA1q27qwHB-igFGCj5xGo/sendMessage"
    params = {
        'chat_id': '5956847167',
        'text': "A",
    }
    requests.post(url, params=params)
    return True

