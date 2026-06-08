import requests
import json
import os

API_KEY = os.environ["TIAN_API_KEY"]
WEBHOOK_URL = os.environ["WEBHOOK_URL"]
KEYWORDS = ["chip", "storage", "AI", "coal", "power", "semiconductor", "optical", "new energy", "battery"]

def fetch_news():
    url = f"http://api.tianapi.com/caijing/index?key={API_KEY}&num=30"
    try:
        resp = requests.get(url, timeout=10)
        data = resp.json()
        if data.get('code') == 200:
            return data.get('newslist', [])
        else:
            print("API error:", data.get('msg'))
            return []
    except Exception as e:
        print("Request failed:", e)
        return []

def filter_news(news_list):
    important = []
    for item in news_list:
        title = item.get('title', '')
        content = item.get('content', '')
        text = title + content
        for kw in KEYWORDS:
            if kw.lower() in text.lower():
                important.append({
                    'title': title,
                    'time': item.get('ctime', ''),
                    'source': item.get('source', '')
                })
                break
    return important

def send_wechat(content):
    data = {"msgtype": "text", "text": {"content": content[:2000]}}
    headers = {"Content-Type": "application/json"}
    try:
        resp = requests.post(WEBHOOK_URL, json=data, headers=headers)
        if resp.json().get('errcode') == 0:
            print("Push success")
        else:
            print("Push failed", resp.text)
    except Exception as e:
        print("Push exception", e)

def main():
    print("Fetching news...")
    news = fetch_news()
    if not news:
        return
    important = filter_news(news)
    if important:
        from datetime import datetime
        now = datetime.now().strftime('%Y-%m-%d %H:%M')
        msg = f"Important news {now}\n"
        for i, n in enumerate(important[:5], 1):
            msg += f"{i}. {n['title']}\n"
        send_wechat(msg)
    else:
        send_wechat("No relevant news found.")

if __name__ == "__main__":
    main()
