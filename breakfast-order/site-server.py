#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
统一站点服务器 (端口80)
- /                 -> AI资讯静态站 (ai-news-site)
- /breakfast/       -> 早餐点单页面
- /breakfast/api/*  -> 早餐点单 API
"""
import json
import os
import sys
import threading
import subprocess
import mimetypes
from datetime import datetime, timedelta
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import urlparse, parse_qs

# 点单提交后自动推送给主人的 QQ
QQ_NOTIFY_TARGET = "AE09E3EC4BCBB9BA31D09E71F47CB6FE"
QQ_NOTIFY_CHANNEL = "qqbot"


def notify_qq(text):
    """后台异步调用 openclaw 发送 QQ 消息，失败只记日志不影响主流程。"""
    def _run():
        try:
            subprocess.run(
                ["openclaw", "message", "send",
                 "--channel", QQ_NOTIFY_CHANNEL,
                 "--target", QQ_NOTIFY_TARGET,
                 "--message", text],
                timeout=30,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
            )
        except Exception as e:
            sys.stderr.write("[notify_qq] error: %s\n" % e)
    threading.Thread(target=_run, daemon=True).start()

SITE_DIR = "/root/.openclaw/workspace/ai-news-site"
BF_DIR = "/root/.openclaw/workspace/breakfast-order"
BF_DATA = os.path.join(BF_DIR, "data")
ORDERS_FILE = os.path.join(BF_DATA, "orders.json")
PORT = 80

sys.path.insert(0, BF_DIR)
import server as bf  # 复用早餐业务的 MENU / 逻辑

bf.load_orders()
lock = threading.Lock()


class ReuseServer(ThreadingHTTPServer):
    allow_reuse_address = True
    daemon_threads = True


class Handler(BaseHTTPRequestHandler):
    protocol_version = "HTTP/1.1"

    def log_message(self, *a):
        sys.stderr.write("%s - - %s\n" % (self.address_string(), a[0] % a[1:] if a else ""))

    # ---------- helpers ----------
    def _json(self, obj, code=200):
        body = json.dumps(obj, ensure_ascii=False).encode()
        self.send_response(code)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Access-Control-Allow-Origin", "*")
        self.end_headers()
        self.wfile.write(body)

    def _file(self, path):
        if not os.path.isfile(path):
            self.send_error(404, "Not Found"); return
        ctype = mimetypes.guess_type(path)[0] or "application/octet-stream"
        if path.endswith(".html"): ctype = "text/html; charset=utf-8"
        if path.endswith(".js"): ctype = "application/javascript; charset=utf-8"
        if path.endswith(".css"): ctype = "text/css; charset=utf-8"
        with open(path, "rb") as f:
            body = f.read()
        self.send_response(200)
        self.send_header("Content-Type", ctype)
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Cache-Control", "no-cache")
        self.send_header("Access-Control-Allow-Origin", "*")
        self.end_headers()
        self.wfile.write(body)

    def _safe_join(self, base, rel):
        p = os.path.normpath(os.path.join(base, rel.lstrip("/")))
        return p if p.startswith(base) else None

    # ---------- GET ----------
    def do_GET(self):
        parsed = urlparse(self.path)
        path = parsed.path
        # 早餐 API
        if path == "/breakfast/api/menu":
            self._json({"menu": bf.MENU, "orders": bf.orders}); return
        if path == "/breakfast/api/daily-menu":
            self._json(bf.build_daily_menu()); return
        if path == "/breakfast/api/orders":
            self._json({"orders": bf.orders}); return
        if path == "/breakfast/api/history":
            qs = parse_qs(parsed.query)
            hist = bf.load_history()
            today = datetime.now().strftime("%Y-%m-%d")
            if bf.orders and today not in hist:
                hist[today] = bf.orders
            date = (qs.get("date") or [None])[0]
            if date:
                data = hist.get(date, {})
                self._json({"date": date, "menu": bf.build_menu_for(data, date), "orders": data})
            else:
                days = {}
                for d, od in hist.items():
                    if not od:
                        continue
                    m = bf.build_menu_for(od, d)
                    names = [f"{s['emoji']}{s['name']}" for s in m["summary"]]
                    days[d] = {"count": m["total_items"], "people": m["total_people"], "preview": "、".join(names[:6])}
                self._json({"days": days}); return
        # 早餐页面
        if path in ("/breakfast", "/breakfast/"):
            self._file(os.path.join(BF_DIR, "index.html")); return
        if path.startswith("/breakfast/"):
            fp = self._safe_join(BF_DIR, path[len("/breakfast/"):])
            self._file(fp) if fp else self.send_error(403); return
        # 静态站
        if path in ("/", ""):
            self._file(os.path.join(SITE_DIR, "index.html")); return
        fp = self._safe_join(SITE_DIR, path)
        self._file(fp) if fp else self.send_error(403)

    # ---------- POST ----------
    def do_POST(self):
        path = urlparse(self.path).path
        length = int(self.headers.get("Content-Length", 0))
        try:
            data = json.loads((self.rfile.read(length) if length else b"{}").decode() or "{}")
        except Exception:
            self._json({"ok": False, "error": "无效的 JSON"}, 400); return

        if path == "/breakfast/api/submit":
            name = (data.get("name") or "").strip()
            items = data.get("items") or []
            if not name:
                self._json({"ok": False, "error": "请填写你的名字"}, 400); return
            clean = []
            for it in items:
                iid = it.get("id")
                qty = max(1, int(it.get("qty", 1)))
                if isinstance(iid, str) and iid.startswith("c_"):
                    nm = it.get("name") or iid[2:]
                    clean.append({"id": iid, "name": nm, "emoji": "✍️", "qty": qty, "price": 0})
                    continue
                base = bf.item_of(iid)
                if not base: continue
                clean.append({"id": base["id"], "name": base["name"], "emoji": base.get("emoji", "🍽"),
                              "qty": qty, "price": base.get("price", 0)})
            if not clean:
                self._json({"ok": False, "error": "请至少选择一样早餐"}, 400); return
            with lock:
                bf.orders[name] = {"name": name, "items": clean,
                                   "ts": datetime.now().strftime("%Y-%m-%d %H:%M:%S")}
                bf.save_orders()
            # 提交成功后推送一条 QQ 给主人
            try:
                tmr = (datetime.now() + timedelta(days=1)).strftime("%m/%d")
                picked = "、".join(f"{i['name']}×{i['qty']}" if i.get("qty", 1) > 1 else i["name"] for i in clean)
                notify_qq(f"✅ 收到啦～\n👤 {name} 点了：{picked}\n明早（{tmr}）给你安排上 🍳")
            except Exception:
                pass
            self._json({"ok": True, "message": f"{name} 的早餐已提交！", "daily_menu": bf.build_daily_menu()})
        elif path == "/breakfast/api/reset":
            with lock:
                bf.orders.clear(); bf.save_orders()
            self._json({"ok": True, "message": "今日点单已清空"})
        elif path == "/breakfast/api/cancel":
            name = (data.get("name") or "").strip()
            with lock:
                if name in bf.orders:
                    del bf.orders[name]; bf.save_orders()
            self._json({"ok": True, "message": f"{name} 的点单已取消"})
        else:
            self.send_error(404)

    def do_OPTIONS(self):
        self.send_response(200)
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        self.send_header("Content-Length", "0")
        self.end_headers()


if __name__ == "__main__":
    print(f"统一站点服务器启动: 端口 {PORT}")
    print(f"  AI资讯站:  http://0.0.0.0/")
    print(f"  早餐点单:  http://0.0.0.0/breakfast/")
    ReuseServer(("0.0.0.0", PORT), Handler).serve_forever()
