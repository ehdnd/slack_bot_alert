import requests
import time
import random
from bs4 import BeautifulSoup
from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError
import os
from dotenv import load_dotenv

# .env 파일에서 환경 변수 불러오기
load_dotenv()

def check_button_class(url):
    try:
        response = requests.get(
            url,
            headers={
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Whale/3.24.223.18 Safari/537.36"
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

# def send_slack_message(client, channel, text):
#     try:
#         client.chat_postMessage(
#             channel=channel,
#             text=f"@channel {text}"
#         )
#     except SlackApiError as e:
#         print(f"@channel Slack API error occurred: {e.response['error']}")

# def send_slack_message(client, channel, text):
#     try:
#         message_blocks = [
#             {
#                 "type": "section",
#                 "text": {
#                     "type": "mrkdwn",
#                     "text": f"<!channel> {text}"
#                 }
#             }
#         ]
#         client.chat_postMessage(
#             channel=channel,
#             text=f"<!channel> {text}",  # 'text' 필드 추가
#             blocks=message_blocks
#         )
#     except SlackApiError as e:
#         # 에러 메시지와 응답 본문 출력
#         print(f"Slack API error occurred: {e.response['error']}")
#         print(f"Response body: {e.response['body']}")


def validate_url(url):
    try:
        response = requests.head(url)
        return response.status_code == 200
    except requests.RequestException as e:
        print(f"URL validation error occurred: {e}")
        return False

def monitor_changes(url, interval):
    if not validate_url(url):
        print("Invalid URL provided. Exiting...")
        return

    slack_token = os.getenv("SLACK_TOKEN")  # .env 파일에서 Slack 토큰 불러오기
    client = WebClient(token=slack_token)
    channel_id = os.getenv("CHANNEL_ID")  # .env 파일에서 채널 ID 불러오기
    send_slack_message(client, channel_id, "=====================")    
    send_slack_message(client, channel_id, "Monitoring started...")

    last_class = None
    
    try:
        while True:
            current_class = check_button_class(url)
            
            if current_class is None:
                send_slack_message(client, channel_id, "Button not found or HTTP error.")
            elif last_class is None:
                send_slack_message(client, channel_id, f"Initial class state: {current_class}")
            elif last_class != current_class:
                send_slack_message(client, channel_id, f"Class change detected: {last_class} -> {current_class}")
                send_slack_message(client, channel_id, url)
            
            last_class = current_class
            sleep_time = random.randint(interval - 450, interval + 450)
            time.sleep(sleep_time)

    except KeyboardInterrupt:
        print("Monitoring stopped.")
        send_slack_message(client, channel_id, "Monitoring has been stopped by the user.")
    except Exception as e:
        print(f"Unexpected error occurred: {e}")
        send_slack_message(client, channel_id, "An unexpected error occurred during monitoring.")

url = "https://linefriendssquare.com/products/bunini-mini-costume-keyring-gray?variant=44274476024007"
print("모니터링 시작...")
monitor_changes(url, 3600)