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
                {"id": "s1", "name": "小笼包", "emoji": "🥟", "desc": "一笼6只，鲜肉", "price": 6},
                {"id": "s2", "name": "豆浆油条", "emoji": "🥖", "desc": "经典搭配", "price": 5},
                {"id": "s3", "name": "肠粉", "emoji": "🍥", "desc": "鸡蛋瘦肉", "price": 7},
                {"id": "s4", "name": "煎饼果子", "emoji": "🌯", "desc": "加蛋加脆饼", "price": 8},
                {"id": "s5", "name": "三明治", "emoji": "🥪", "desc": "火腿芝士", "price": 9},
                {"id": "s6", "name": "白粥", "emoji": "🍚", "desc": "配小菜", "price": 3},
            ],
        },
        {
            "id": "protein",
            "name": "蛋奶",
            "icon": "🥚",
            "items": [
                {"id": "p1", "name": "水煮蛋", "emoji": "🥚", "desc": "1个", "price": 2},
                {"id": "p2", "name": "煎蛋", "emoji": "🍳", "desc": "溏心", "price": 3},
                {"id": "p3", "name": "牛奶", "emoji": "🥛", "desc": "250ml", "price": 4},
                {"id": "p4", "name": "酸奶", "emoji": "🍶", "desc": "原味", "price": 5},
            ],
        },
        {
            "id": "side",
            "name": "小食",
            "icon": "🍎",
            "items": [
                {"id": "d1", "name": "苹果", "emoji": "🍎", "desc": "1个", "price": 3},
                {"id": "d2", "name": "香蕉", "emoji": "🍌", "desc": "1根", "price": 2},
                {"id": "d3", "name": "蒸红薯", "emoji": "🍠", "desc": "1个", "price": 4},
                {"id": "d4", "name": "坚果", "emoji": "🥜", "desc": "混合一小包", "price": 5},
            ],
        },
        {
            "id": "drink",
            "name": "饮品",
            "icon": "☕",
            "items": [
                {"id": "k1", "name": "热豆浆", "emoji": "🥛", "desc": "无糖/微甜", "price": 3},
                {"id": "k2", "name": "咖啡", "emoji": "☕", "desc": "美式", "price": 8},
                {"id": "k3", "name": "橙汁", "emoji": "🍊", "desc": "鲜榨", "price": 6},
                {"id": "k4", "name": "温水", "emoji": "💧", "desc": "一杯", "price": 0},
            ],
        },
    ]
}

# 内存中的人员 -> 早餐 记录
orders = {}   # {name: {"name":..., "items":[{id,name,qty,price}], "ts":...}}
lock = threading.Lock()


def ensure_data():
    os.makedirs(DATA_DIR, exist_ok=True)


def load_orders():
    global orders
    ensure_data()
    if os.path.exists(ORDERS_FILE):
        try:
            with open(ORDERS_FILE, "r", encoding="utf-8") as f:
                orders = json.load(f)
        except Exception:
            orders = {}


def save_orders():
    ensure_data()
    with open(ORDERS_FILE, "w", encoding="utf-8") as f:
        json.dump(orders, f, ensure_ascii=False, indent=2)


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


def build_daily_menu():
    """汇总所有点单，生成每日早餐菜单"""
    agg = {}  # item_id -> {name, emoji, price, qty}
    total_people = len(orders)
    for person, od in orders.items():
        for it in od.get("items", []):
            iid = it["id"]
            if iid not in agg:
                base = item_of(iid) or {"id": iid, "name": it.get("name", iid), "emoji": it.get("emoji", "🍽"), "price": it.get("price", 0)}
                agg[iid] = {"id": iid, "name": base["name"], "emoji": base.get("emoji", "🍽"),
                            "price": base.get("price", 0), "qty": 0, "people": []}
            agg[iid]["qty"] += it.get("qty", 1)
            agg[iid]["people"].append(person)

    summary = sorted(agg.values(), key=lambda x: -x["qty"])
    total_price = sum(x["price"] * x["qty"] for x in summary)
    total_items = sum(x["qty"] for x in summary)

    per_person = []
    for person, od in orders.items():
        p_total = sum(it.get("price", 0) * it.get("qty", 1) for it in od.get("items", []))
        per_person.append({
            "name": person,
            "items": od.get("items", []),
            "total": p_total,
            "ts": od.get("ts"),
        })
    per_person.sort(key=lambda x: x["name"])

    return {
        "date": datetime.now().strftime("%Y-%m-%d"),
        "generated_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "total_people": total_people,
        "total_items": total_items,
        "total_price": total_price,
        "summary": summary,
        "per_person": per_person,
    }


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
            self._json({"menu": MENU, "orders": orders})
        elif path == "/api/daily-menu":
            self._json(build_daily_menu())
        elif path == "/api/orders":
            self._json({"orders": orders})
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
                base = item_of(iid)
                if not base:
                    continue
                qty = max(1, int(it.get("qty", 1)))
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
