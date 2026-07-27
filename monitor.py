import requests
import json
import os
import time
from datetime import datetime

UP_UID = os.environ["UP_UID"]
SERVER_CHAN_KEY = os.environ["SERVER_CHAN_KEY"]
COOKIE = os.environ["BILI_COOKIE"]

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Accept": "application/json, text/plain, */*",
    "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8",
    "Referer": "https://space.bilibili.com/",
    "Cookie": COOKIE
}

STATE_FILE = "last_state.json"

def send_wechat(title, content):
    url = f"https://sctapi.ftqq.com/{SERVER_CHAN_KEY}.send"
    requests.post(url, data={"title": title, "desp": content})

def get_latest_video(mid):
    url = f"https://api.bilibili.com/x/space/arc/search?mid={mid}&ps=1&pn=1&order=pubdate"
    try:
        resp = requests.get(url, headers=HEADERS, timeout=15)
        if resp.status_code == 200:
            data = resp.json()
            if data["code"] == 0:
                vlist = data["data"]["list"]["vlist"]
                if vlist:
                    return vlist[0]["aid"], vlist[0]["title"]
    except Exception as e:
        print("视频请求异常:", e)
    return None, None

def get_latest_dynamic(mid):
    url = f"https://api.bilibili.com/x/polymer/web-dynamic/v1/feed/space?host_mid={mid}"
    try:
        resp = requests.get(url, headers=HEADERS, timeout=15)
        if resp.status_code == 200:
            data = resp.json()
            if data["code"] == 0:
                items = data["data"]["items"]
                if items:
                    dyn = items[0]
                    desc = dyn.get("modules", {}).get("module_dynamic", {}).get("desc", {})
                    text = desc.get("text", "无文字")
                    return dyn["id_str"], text
    except Exception as e:
        print("动态请求异常:", e)
    return None, None

def load_state():
    if os.path.exists(STATE_FILE):
        with open(STATE_FILE) as f:
            return json.load(f)
    return {"latest_video_aid": 0, "latest_dynamic_id": ""}

def save_state(state):
    with open(STATE_FILE, "w") as f:
        json.dump(state, f)

def main():
    state = load_state()
    
    vid_aid, vid_title = get_latest_video(UP_UID)
    if vid_aid and vid_aid > state["latest_video_aid"]:
        msg = f"{vid_title}\nhttps://www.bilibili.com/video/av{vid_aid}"
        send_wechat("B站新视频", msg)
        state["latest_video_aid"] = vid_aid

    dyn_id, dyn_text = get_latest_dynamic(UP_UID)
    if dyn_id and dyn_id != state["latest_dynamic_id"]:
        msg = f"{dyn_text}\nhttps://t.bilibili.com/{dyn_id}"
        send_wechat("B站新动态", msg)
        state["latest_dynamic_id"] = dyn_id

    save_state(state)

if __name__ == "__main__":
    main()
