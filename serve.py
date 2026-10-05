#!/usr/bin/env python3
"""Локальный сервер для репозитория DS — БЕЗ кэширования.

Зачем отдельный файл, а не `python -m http.server`:
штатный SimpleHTTPRequestHandler не отдаёт заголовок Cache-Control, и браузер
кэширует CSS/HTML по эвристике (≈10 % от возраста файла). Из-за этого страница
могла рисоваться старым modes.css — «мобильное» поле показывало 48 вместо 56.
Здесь ко всем ответам добавляется `Cache-Control: no-store`, поэтому Ctrl+F5
не нужен: страница всегда берёт текущие файлы.

Запуск:
  python serve.py                 # порт 8899, корень — папка этого файла
  python serve.py 9000            # другой порт
"""

import functools
import http.server
import json
import os
import re
import socket
import sys

ROOT = os.path.dirname(os.path.abspath(__file__))
PORT = int(sys.argv[1]) if len(sys.argv) > 1 else 8899

# Куда складывать решения ревью (страницы рекомендаций). Один человек — один файл,
# поэтому мнения разных людей не затирают друг друга и файлы спокойно коммитятся в git.
REVIEW_DIR = os.path.join(ROOT, "_audit", "rec", "review")


def safe_name(value, fallback):
    """Имя файла из названия компонента или имени человека: только буквы, цифры, - и _."""
    value = re.sub(r"[^\w\-]+", "_", str(value or "").strip(), flags=re.UNICODE).strip("_")
    return (value or fallback)[:48]


class NoCacheHandler(http.server.SimpleHTTPRequestHandler):
    def end_headers(self):
        self.send_header("Cache-Control", "no-store, no-cache, must-revalidate, max-age=0")
        self.send_header("Pragma", "no-cache")
        self.send_header("Expires", "0")
        super().end_headers()

    def log_message(self, fmt, *args):  # тише в консоли
        sys.stderr.write("%s %s\n" % (self.address_string(), fmt % args))

    def do_POST(self):
        """Приём решений ревью: POST /__rec-review → _audit/rec/review/<компонент>.<человек>.json.

        Ничего кроме этой папки сервер не пишет."""
        if self.path.split("?")[0] != "/__rec-review":
            self.send_error(404, "unknown endpoint")
            return
        try:
            length = int(self.headers.get("Content-Length") or 0)
            payload = json.loads(self.rfile.read(length).decode("utf-8"))
            if not isinstance(payload, dict):
                raise ValueError("ожидался объект JSON")
            slug = safe_name(payload.get("component"), "component")
            person = safe_name(payload.get("person"), "guest")
            os.makedirs(REVIEW_DIR, exist_ok=True)
            path = os.path.join(REVIEW_DIR, "%s.%s.json" % (slug, person))
            with open(path, "w", encoding="utf-8", newline="\n") as f:
                f.write(json.dumps(payload, ensure_ascii=False, indent=2) + "\n")
            rel = os.path.relpath(path, ROOT).replace(os.sep, "/")
            body = json.dumps({"ok": True, "path": rel}, ensure_ascii=False).encode("utf-8")
            self.send_response(200)
            self.send_header("Content-Type", "application/json; charset=utf-8")
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            self.wfile.write(body)
        except Exception as e:  # noqa: BLE001 — сервер служебный, ошибку отдаём текстом
            body = json.dumps({"ok": False, "error": str(e)}, ensure_ascii=False).encode("utf-8")
            self.send_response(400)
            self.send_header("Content-Type", "application/json; charset=utf-8")
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            self.wfile.write(body)


def main():
    handler = functools.partial(NoCacheHandler, directory=ROOT)
    with http.server.ThreadingHTTPServer(("127.0.0.1", PORT), handler) as httpd:
        print("Сервер без кэша: http://127.0.0.1:%d/  (корень %s)" % (PORT, ROOT))
        print("Страницы: http://127.0.0.1:%d/components-mobile/prototypes/recommendations/index.html" % PORT)
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            print("\nОстановлен.")


if __name__ == "__main__":
    try:
        main()
    except OSError as e:
        if isinstance(e, OSError) and getattr(e, "errno", None) in (48, 98, 10048):
            print("Порт %d занят — останови старый сервер или запусти с другим портом" % PORT)
        else:
            raise
