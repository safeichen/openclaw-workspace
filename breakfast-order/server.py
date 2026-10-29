#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
早餐点单系统 - 后端服务
在 QQ 中打开页面选早餐 -> 提交 -> 生成每日早餐菜单
"""
import json
import os
import threading
from datetime import datetime
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import urlparse, parse_qs

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, "data")
ORDERS_FILE = os.path.join(DATA_DIR, "orders.json")
MENU_FILE = os.path.join(DATA_DIR, "menu.json")
PUBLIC_BASE = os.environ.get("BREAKFAST_PUBLIC_BASE", "http://43.159.52.61")
PORT = int(os.environ.get("BREAKFAST_PORT", "8092"))

# 菜单（可自行增删）
MENU = {
    "categories": [
        {
            "id": "staple",
            "name": "主食",
            "icon": "🍚",
            "items": [
                {"id": "s1", "name": "小笼包", "emoji": "🥟", "desc": "", "price": 0},
                {"id": "s2", "name": "锅贴", "emoji": "🥟", "desc": "", "price": 0},
                {"id": "s3", "name": "煎饼", "emoji": "🥞", "desc": "", "price": 0},
                {"id": "s4", "name": "手抓饼", "emoji": "🫓", "desc": "", "price": 0},
                {"id": "s5", "name": "汉堡", "emoji": "🍔", "desc": "", "price": 0},
                {"id": "s6", "name": "烧麦", "emoji": "🍡", "desc": "", "price": 0},
                {"id": "s7", "name": "馒头", "emoji": "🍞", "desc": "", "price": 0},
                {"id": "s8", "name": "肉夹馍", "emoji": "🥙", "desc": "", "price": 0},
                {"id": "s9", "name": "吐司", "emoji": "🍞", "desc": "", "price": 0},
                {"id": "s10", "name": "松饼", "emoji": "🥞", "desc": "", "price": 0},
                {"id": "s11", "name": "烤薯角", "emoji": "🍟", "desc": "", "price": 0},
            ],
        },
        {
            "id": "pair",
            "name": "搭配",
            "icon": "🍳",
            "items": [
                {"id": "p1", "name": "培根", "emoji": "🥓", "desc": "", "price": 0},
                {"id": "p2", "name": "火腿", "emoji": "🍖", "desc": "", "price": 0},
                {"id": "p3", "name": "煎蛋", "emoji": "🍳", "desc": "", "price": 0},
                {"id": "p4", "name": "水煮蛋", "emoji": "🥚", "desc": "", "price": 0},
                {"id": "p6", "name": "午餐肉", "emoji": "🥫", "desc": "", "price": 0},
            ],
        },
        {
            "id": "other",
            "name": "其他",
            "icon": "✍️",
            "items": [
                {"id": "o1", "name": "其他（可文字输入）", "emoji": "✍️", "desc": "选这个可补充说明", "price": 0},
            ],
        },
    ]
}

# 内存中的人员 -> 早餐 记录
orders = {}   # {name: {"name":..., "items":[{id,name,qty,price}], "ts":...}}
lock = threading.Lock()


def ensure_data():
    os.makedirs(DATA_DIR, exist_ok=True)


def _date_of_order(od):
    """从记录的 ts 里取日期部分（YYYY-MM-DD）。"""
    ts = (od or {}).get("ts") or ""
    return ts[:10] if len(ts) >= 10 else ""


def load_orders():
    global orders
    ensure_data()
    today = datetime.now().strftime("%Y-%m-%d")
    hist = load_history()
    if today in hist:
        orders = hist[today]
    elif os.path.exists(ORDERS_FILE):
        try:
            with open(ORDERS_FILE, "r", encoding="utf-8") as f:
                orders = json.load(f)
        except Exception:
            orders = {}
    else:
        orders = {}
    # 日期隔离：只保留「今天下的单」（今天选、明天吃）。
    # 昨天及更早的单视为已消费，先归档到 history 再从当前 orders 清掉。
    stale_dates = set()
    keep = {}
    for name, od in list(orders.items()):
        d = _date_of_order(od)
        if d == today:
            keep[name] = od
        elif d:
            stale_dates.add(d)
    if len(keep) != len(orders):
        orders = keep
        save_orders()  # 同步把当前 orders.json 更新为今天的单


def rollover_orders():
    """读取前调用：把「非今天」的单从内存剔除（跨天滚动）。
    这样即使服务跨过零点长时间运行，也不会把昨天的单当成今天的展示。
    """
    global orders
    today = datetime.now().strftime("%Y-%m-%d")
    keep, dropped = {}, False
    for name, od in list(orders.items()):
        if _date_of_order(od) == today:
            keep[name] = od
        else:
            dropped = True
    if dropped or len(keep) != len(orders):
        with lock:
            orders = keep
            save_orders()
    return orders


def current_orders():
    """返回「今天的」点单（会先做跨天滚动）。"""
    return rollover_orders()


HISTORY_FILE = os.path.join(DATA_DIR, "history.json")


def load_history():
    ensure_data()
    if os.path.exists(HISTORY_FILE):
        try:
            with open(HISTORY_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            return {}
    return {}


def save_history(hist):
    ensure_data()
    with open(HISTORY_FILE, "w", encoding="utf-8") as f:
        json.dump(hist, f, ensure_ascii=False, indent=2)


def save_orders():
    ensure_data()
    with open(ORDERS_FILE, "w", encoding="utf-8") as f:
        json.dump(orders, f, ensure_ascii=False, indent=2)
    # 同步归档到 history.json（按日期）
    today = datetime.now().strftime("%Y-%m-%d")
    hist = load_history()
    if orders:
        hist[today] = orders
    elif today in hist:
        # 清空当天
        hist[today] = {}
    save_history(hist)


def price_of(item_id):
    for cat in MENU["categories"]:
        for it in cat["items"]:
            if it["id"] == item_id:
                return it
    return None


def item_of(item_id):
    for cat in MENU["categories"]:
        for it in cat["items"]:
            if it["id"] == item_id:
                return it
    return None


def build_menu_for(orders_data, date_str):
    """通用：把某个日期的一份 orders 汇总成菜单"""
    agg = {}
    total_people = len(orders_data)
    for person, od in orders_data.items():
        for it in od.get("items", []):
            iid = it["id"]
            if iid not in agg:
                base = item_of(iid) or {"id": iid, "name": it.get("name", iid), "emoji": it.get("emoji", "🍽"), "price": it.get("price", 0)}
                agg[iid] = {"id": iid, "name": base["name"], "emoji": base.get("emoji", "🍽"),
                            "price": base.get("price", 0), "qty": 0, "people": []}
            agg[iid]["qty"] += it.get("qty", 1)
            agg[iid]["people"].append(person)

    summary = sorted(agg.values(), key=lambda x: -x["qty"])
    total_items = sum(x["qty"] for x in summary)

    per_person = []
    for person, od in orders_data.items():
        per_person.append({
            "name": person,
            "items": od.get("items", []),
            "ts": od.get("ts"),
        })
    per_person.sort(key=lambda x: x["name"])

    return {
        "date": date_str,
        "generated_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "total_people": total_people,
        "total_items": total_items,
        "total_price": 0,
        "summary": summary,
        "per_person": per_person,
    }


def build_daily_menu():
    """汇总今日点单"""
    rollover_orders()
    return build_menu_for(orders, datetime.now().strftime("%Y-%m-%d"))


class Handler(BaseHTTPRequestHandler):
    def log_message(self, *args):
        pass

    def _json(self, obj, code=200):
        body = json.dumps(obj, ensure_ascii=False).encode("utf-8")
        self.send_response(code)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Access-Control-Allow-Origin", "*")
        self.end_headers()
        self.wfile.write(body)

    def _file(self, path, ctype):
        try:
            with open(path, "rb") as f:
                body = f.read()
        except FileNotFoundError:
            self.send_error(404, "Not Found")
            return
        self.send_response(200)
        self.send_header("Content-Type", ctype)
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Cache-Control", "no-cache")
        self.end_headers()
        self.wfile.write(body)

    def do_GET(self):
        parsed = urlparse(self.path)
        path = parsed.path
        if path in ("/", "/index.html"):
            self._file(os.path.join(BASE_DIR, "index.html"), "text/html; charset=utf-8")
        elif path == "/api/menu":
            self._json({"menu": MENU, "orders": current_orders()})
        elif path == "/api/daily-menu":
            self._json(build_daily_menu())
        elif path == "/api/orders":
            self._json({"orders": current_orders()})
        elif path == "/api/history":
            qs = parse_qs(parsed.query)
            hist = load_history()
            # 补齐当天（可能还没归档）
            today = datetime.now().strftime("%Y-%m-%d")
            cur = current_orders()
            if cur and today not in hist:
                hist[today] = cur
            date = (qs.get("date") or [None])[0]
            if date:
                data = hist.get(date, {})
                self._json({"date": date, "menu": build_menu_for(data, date), "orders": data})
            else:
                # 日历总览：只返回有记录的日期概览
                days = {}
                for d, od in hist.items():
                    if not od:
                        continue
                    m = build_menu_for(od, d)
                    names = [f"{s['emoji']}{s['name']}" for s in m["summary"]]
                    days[d] = {"count": m["total_items"], "people": m["total_people"], "preview": "、".join(names[:6])}
                self._json({"days": days})
        else:
            self.send_error(404, "Not Found")

    def do_POST(self):
        parsed = urlparse(self.path)
        length = int(self.headers.get("Content-Length", 0))
        raw = self.rfile.read(length) if length else b"{}"
        try:
            data = json.loads(raw.decode("utf-8") or "{}")
        except Exception:
            self._json({"ok": False, "error": "无效的 JSON"}, 400)
            return

        if parsed.path == "/api/submit":
            name = (data.get("name") or "").strip()
            items = data.get("items") or []
            if not name:
                self._json({"ok": False, "error": "请填写你的名字"}, 400)
                return
            clean = []
            for it in items:
                iid = it.get("id")
                qty = max(1, int(it.get("qty", 1)))
                if isinstance(iid, str) and iid.startswith("c_"):
                    # 自定义输入项
                    nm = it.get("name") or iid[2:]
                    clean.append({"id": iid, "name": nm, "emoji": "✍️", "qty": qty, "price": 0})
                    continue
                base = item_of(iid)
                if not base:
                    continue
                clean.append({"id": iid, "name": base["name"], "emoji": base.get("emoji", "🍽"),
                              "qty": qty, "price": base.get("price", 0)})
            if not clean:
                self._json({"ok": False, "error": "请至少选择一样早餐"}, 400)
                return
            with lock:
                orders[name] = {
                    "name": name,
                    "items": clean,
                    "ts": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                }
                save_orders()
            self._json({"ok": True, "message": f"{name} 的早餐已提交！", "daily_menu": build_daily_menu()})
        elif parsed.path == "/api/reset":
            with lock:
                orders.clear()
                save_orders()
            self._json({"ok": True, "message": "今日点单已清空"})
        elif parsed.path == "/api/cancel":
            name = (data.get("name") or "").strip()
            with lock:
                if name in orders:
                    del orders[name]
                    save_orders()
            self._json({"ok": True, "message": f"{name} 的点单已取消"})
        else:
            self.send_error(404, "Not Found")

    def do_OPTIONS(self):
        self.send_response(200)
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        self.end_headers()


def main():
    ensure_data()
    load_orders()
    server = ThreadingHTTPServer(("0.0.0.0", PORT), Handler)
    print(f"🥣 早餐点单系统已启动")
    print(f"   本地: http://localhost:{PORT}")
    print(f"   公网: {PUBLIC_BASE}:{PORT}")
    server.serve_forever()


if __name__ == "__main__":
    main()
