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
            print(f"웹사이트 오류: {response.status_code}")
            return None
    except requests.RequestException as e:
        print(f"HTTP Request 오류: {e}")
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
    
    last_class = ["ipx_add_to_cart","product-form__submit","buyBtn","button","hidden"]
    current_class = check_button_class(url)

    if current_class != last_class and current_class != None :
        send_slack_message(client, channel_id, f"클래스 변경: {last_class}")
        send_slack_message(client, channel_id, url)

url = "https://linefriendssquare.com/products/newjeans-x-murakami-metal-keyring?variant=44376599560391"

wait_time = random.randint(0, 60)
time.sleep(wait_time)
monitor_changes(url)
