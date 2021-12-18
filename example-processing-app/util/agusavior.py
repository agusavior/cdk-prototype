import requests
import urllib.parse

# Send a Telegram message to agusavior
def send_telegram_message(text: str):
    text = urllib.parse.quote(text)
    requests.get(f'https://chat.agusavior.info/sendMessage?text={text}')
