import requests


def send_telegram_message(content_str):
    """
    发送消息推送
    """
    token = 'xxx'
    chat_id = 'xxx'
    url = f"https://api.telegram.org/bot{token}/sendMessage"
    payload = {
        "chat_id": chat_id,
        "text": content_str,
        "parse_mode": "HTML"  # 支持html格式
    }

    try:
        response = requests.post(url, data=payload)
        return response.text
    except Exception as e:
        print(f"Error: {e}")

