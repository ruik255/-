import requests
import json
import os
from datetime import datetime

API_KEY = os.environ["TIAN_API_KEY"]
WEBHOOK_URL = os.environ["WEBHOOK_URL"]

# 非常宽泛的关键词，确保能匹配大多数财经新闻
KEYWORDS = [
    "中国", "市场", "经济", "发展", "公司", "行业", "投资", "增长",
    "芯片", "存储", "半导体", "光模块", "AI", "人工智能", "算力",
    "煤炭", "电力", "新能源", "电池", "电动车", "光伏", "储能",
    "科技", "政策", "工信部", "发改委", "能源", "涨价", "供需",
    "基金", "股票", "A股", "美股", "港股", "IPO", "上市", "融资"
]

def fetch_news():
    url = f"http://api.tianapi.com/caijing/index?key={API_KEY}&num=50"
    try:
        resp = requests.get(url, timeout=10)
        data = resp.json()
        if data.get('code') == 200:
            newslist = data.get('newslist', [])
            print(f"获取到 {len(newslist)} 条新闻")
            return newslist
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
        matched = False
        for kw in KEYWORDS:
            if kw in text:
                important.append({
                    'title': title,
                    'time': item.get('ctime', ''),
                    'source': item.get('source', '')
                })
                matched = True
                print(f"匹配关键词 '{kw}': {title[:50]}...")
                break
        if not matched:
            print(f"未匹配: {title[:50]}...")
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
        send_wechat("新闻抓取失败，请检查API Key或网络")
        return
    important = filter_news(news)
    print(f"共匹配到 {len(important)} 条重要新闻")
    if important:
        now = datetime.now().strftime('%Y-%m-%d %H:%M')
        msg = f"📰 重要新闻 {now}\n"
        for i, n in enumerate(important[:20], 1):
            msg += f"{i}. {n['title']}\n"
        send_wechat(msg)
    else:
        send_wechat(f"暂无关键词相关新闻（共{len(news)}条）")

if __name__ == "__main__":
    main()
