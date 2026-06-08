import requests
import json
import os

API_KEY = os.environ["TIAN_API_KEY"]
WEBHOOK_URL = os.environ["WEBHOOK_URL"]
KEYWORDS = ["芯片", "存储", "AI", "煤炭", "电力", "半导体", "光模块", "新能源", "电池"]

def fetch_news():
    url = f"http://api.tianapi.com/caijing/index?key={API_KEY}&num=30"
    try:
        resp = requests.get(url, timeout=10)
        data = resp.json()
        if data.get('code') == 200:
            return data.get('newslist', [])
        else:
            print("API错误:", data.get('msg'))
            return []
    except Exception as e:
        print("请求失败:", e)
        return []

def filter_news(news_list):
    important = []
    for item in news_list:
        title = item.get('title', '')
        content = item.get('content', '')
        text = title + content
        for kw in KEYWORDS:
            if kw in text:
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
            print("推送成功")
        else:
            print("推送失败", resp.text)
    except Exception as e:
        print("推送异常", e)

def main():
    print("开始抓取新闻...")
    news = fetch_news()
    if not news:
        return
    important = filter_news(news)
    if important:
        from datetime import datetime
        now = datetime.now().strftime('%Y-%m-%d %H:%M')
        msg = f"📰 重要新闻 {now}\n"
        for i, n in enumerate(important[:5], 1):
            msg += f"{i}. {n['title']}\n"
        send_wechat(msg)
    else:
        send_wechat("暂无关键词相关新闻")

if __name__ == "__main__":
    main()
