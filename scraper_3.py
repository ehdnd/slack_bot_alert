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
    except requests.RequestException as e:
        print(f"HTTP 요청 에러 발생: {e}")
        return None

def send_slack_message(client, channel, text):
    try:
        client.chat_postMessage(
            channel=channel,
            text=text
        )
    except SlackApiError as e:
        print(f"Slack API 에러 발생: {e.response['error']}")

def monitor_changes(url, interval):
    slack_token = os.getenv("SLACK_TOKEN")  # .env 파일에서 Slack 토큰 불러오기
    client = WebClient(token=slack_token)
    channel_id = os.getenv("CHANNEL_ID")   # 채널 ID를 입력합니다.
    
    send_slack_message(client, channel_id, "모니터링 시작...")

    last_class = None
    
    try:
        while True:
            current_class = check_button_class(url)
            
            if current_class is None:
                send_slack_message(client, channel_id, "버튼을 찾을 수 없습니다.")
            elif last_class is None:
                send_slack_message(client, channel_id, f"초기 클래스 상태: {current_class}")
            elif last_class != current_class:
                send_slack_message(client, channel_id, f"클래스 변경 감지: {last_class} -> {current_class}")
            
            last_class = current_class
            sleep_time = random.randint(interval - 450, interval + 450)
            time.sleep(sleep_time)

    except KeyboardInterrupt:
        print("모니터링 종료.")
        send_slack_message(client, channel_id, "모니터링이 사용자에 의해 종료되었습니다.")
    except Exception as e:
        print(f"예상치 못한 에러 발생: {e}")
        send_slack_message(client, channel_id, "모니터링 중 예상치 못한 에러가 발생했습니다.")

# url = "https://linefriendssquare.com/products/bunini-mini-costume-keyring-gray?variant=44274476024007"
url = "https://asdfasdfasdf"
monitor_changes(url, 3600)
