from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError

slack_token = "x"
client = WebClient(token=slack_token)

try:
    response = client.chat_postMessage(
        channel="", #채널 id를 입력합니다.
        text="안녕하세요~!"
    )
except SlackApiError as e:
    assert e.response["error"]