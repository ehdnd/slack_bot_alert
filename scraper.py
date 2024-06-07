import requests
import random
import time
from bs4 import BeautifulSoup
from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError
import os

def check_button_class(url):
    try:
        response = requests.get(
            url,
            headers={
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, Gecko) Chrome/120.0.0.0 Whale/3.24.223.18 Safari/537.36"
            })
        if response.status_code == 200:
            soup = BeautifulSoup(response.content, "html.parser")
            button = soup.find('button', class_='ipx_add_to_cart')
        
            return button['class'] if button else None
        else:
            print(f"HTTP request returned status code {response.status_code}")
            return None
    except requests.RequestException as e:
        print(f"HTTP request error occurred: {e}")
        return None

def send_slack_message(client, channel, text):
    try:
        client.chat_postMessage(
            channel=channel,
            text=text
        )
    except SlackApiError as e:
        print(f"Slack API error occurred: {e.response['error']}")

def validate_url(url):
    try:
        response = requests.head(url)
        return response.status_code == 200
    except requests.RequestException as e:
        print(f"URL validation error occurred: {e}")
        return False

def monitor_changes(url):
    if not validate_url(url):
        print("Invalid URL provided. Exiting...")
        return

    slack_token = os.getenv("SLACK_TOKEN")  # 환경 변수에서 Slack 토큰 불러오기
    client = WebClient(token=slack_token)
    channel_id = os.getenv("CHANNEL_ID")  # 환경 변수에서 채널 ID 불러오기
    

    last_class_file = "last_class.txt"

    def get_last_class():
        try:
            with open('last_class.txt', 'r') as file:
                # 파일에서 읽은 문자열을 리스트로 변환
                last_class = file.read().split(',')
                return last_class
        except FileNotFoundError:
            return [ipx_add_to_cart,product-form__submit,buyBtn,button,hidden]

    def set_last_class(current_class):
        with open('last_class.txt', 'w') as file:
            # 리스트를 문자열로 변환하여 파일에 쓰기
            class_name_str = ','.join(current_class)
            file.write(class_name_str)

    last_class = get_last_class()
    current_class = check_button_class(url)

    if current_class is None:
        send_slack_message(client, channel_id, "Button not found or HTTP error.")
    elif last_class is None:
        send_slack_message(client, channel_id, f"Initial class state: {current_class}")
    elif last_class != current_class:
        send_slack_message(client, channel_id, f"Class change detected: {last_class} -> {current_class}")
        send_slack_message(client, channel_id, url)

    set_last_class(current_class)

url = "https://linefriendssquare.com/products/bunini-mini-costume-keyring-gray?variant=44274476024007"

wait_time = random.randint(0, 900)
time.sleep(wait_time)
monitor_changes(url)
