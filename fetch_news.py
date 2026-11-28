"""ดึงข่าวจาก feeds.json -> เขียน news.json และส่ง Telegram เมื่อพบคำสำคัญ"""
import calendar
import json
import os
import re
from datetime import datetime, timezone

import feedparser
import requests

TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN")
CHAT_ID = os.environ.get("TELEGRAM_CHAT_ID")
NEWS_FILE, SEEN_FILE = "news.json", "seen.json"
MAX_ITEMS = 200


def read(path, default):
    try:
        with open(path, encoding="utf-8") as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return default


def write(path, data):
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=1)


def severity(text):
    t = text.lower()
    if re.search(r"zero-day|actively exploited|critical", t):
        return "critical"
    if re.search(r"ransomware|breach|exploit|vulnerab", t):
        return "high"
    return "info"


def iso(entry):
    st = entry.get("published_parsed") or entry.get("updated_parsed")
    ts = calendar.timegm(st) if st else datetime.now(timezone.utc).timestamp()
    return datetime.fromtimestamp(ts, timezone.utc).isoformat()


def clean(html):
    return re.sub(r"\s+", " ", re.sub(r"<[^>]+>", " ", html or "")).strip()[:220]


def image(entry):
    """หารูปประกอบข่าวจากฟีด (เก็บเฉพาะลิงก์ https ไม่ดาวน์โหลดรูปมาเก็บ)"""
    urls = []
    for key in ("media_thumbnail", "media_content"):
        urls += [m.get("url", "") for m in entry.get(key, []) or []]
    urls += [
        enc.get("href", "")
        for enc in entry.get("enclosures", []) or []
        if enc.get("type", "").startswith("image")
    ]
    html = [entry.get("summary", "")] + [c.get("value", "") for c in entry.get("content", []) or []]
    for h in html:
        m = re.search(r"<img[^>]+src=[\"']([^\"']+)", h or "")
        if m:
            urls.append(m.group(1))
    return next((u for u in urls if u.startswith("https://")), "")


def notify(item):
    if not (TOKEN and CHAT_ID):
        return
    text = f"[{item['source']}] {item['title']}\n{item['link']}"
    try:
        requests.post(
            f"https://api.telegram.org/bot{TOKEN}/sendMessage",
            data={"chat_id": CHAT_ID, "text": text},
            timeout=15,
        )
    except requests.RequestException:
        pass


cfg = read("feeds.json", {"feeds": [], "keywords": []})
keywords = [k.lower() for k in cfg.get("keywords", [])]
first_run = not os.path.exists(SEEN_FILE)  # รอบแรกไม่ส่ง Telegram เพื่อกันข้อความท่วม
seen_list = read(SEEN_FILE, [])
seen = set(seen_list)
news = {i["link"]: i for i in read(NEWS_FILE, [])}

# ลบข่าวของฟีดที่ถูกลบออกจาก feeds.json แล้ว (ป้องกันกรณีไฟล์ feeds.json ว่างจนลบข่าวทั้งหมด)
names = {f.get("name") or f["url"] for f in cfg.get("feeds", [])}
if names:
    news = {k: v for k, v in news.items() if v.get("source") in names}

for feed in cfg.get("feeds", []):
    for e in feedparser.parse(feed["url"]).entries:
        link = e.get("link")
        if not link or link in seen:
            continue
        title, summary = clean(e.get("title")), clean(e.get("summary"))
        item = {
            "title": title,
            "link": link,
            "source": feed.get("name") or feed["url"],
            "published": iso(e),
            "summary": summary,
            "severity": severity(title + " " + summary),
            "image": image(e),
        }
        news[link] = item
        seen.add(link)
        seen_list.append(link)
        if not first_run and any(k in (title + " " + summary).lower() for k in keywords):
            notify(item)

items = sorted(news.values(), key=lambda i: i["published"], reverse=True)[:MAX_ITEMS]
write(NEWS_FILE, items)
write(SEEN_FILE, seen_list[-3000:])
