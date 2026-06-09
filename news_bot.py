import requests
import os

API_KEY = os.environ["TIAN_API_KEY"]
WEBHOOK_URL = os.environ["WEBHOOK_URL"]

def fetch_news():
    url = f"http://api.tianapi.com/caijing/index?key={API_KEY}&num=50"
    try:
        r = requests.get(url, timeout=10)
        data = r.json()
        if data.get('code') == 200:
            return data.get('newslist', [])
        else:
            print("API错误:", data.get('msg'))
            return []
    except Exception as e:
        print("请求异常:", e)
        return []

def send_wechat(text):
    payload = {"msgtype": "text", "text": {"content": text[:2000]}}
    try:
        r = requests.post(WEBHOOK_URL, json=payload)
        if r.json().get('errcode') == 0:
            print("推送成功")
        else:
            print("推送失败", r.text)
    except Exception as e:
        print("推送异常", e)

def main():
    print("开始抓取新闻...")
    news = fetch_news()
    if not news:
        send_wechat("获取新闻失败")
        return
    # 只取前10条新闻的标题，不筛选，直接发送
    titles = [item.get('title', '无标题') for item in news[:10]]
    msg = "测试：今日前10条新闻标题\n" + "\n".join(titles)
    send_wechat(msg)

if __name__ == "__main__":
    main()
