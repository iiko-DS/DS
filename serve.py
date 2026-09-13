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
import os
import socket
import sys

ROOT = os.path.dirname(os.path.abspath(__file__))
PORT = int(sys.argv[1]) if len(sys.argv) > 1 else 8899


class NoCacheHandler(http.server.SimpleHTTPRequestHandler):
    def end_headers(self):
        self.send_header("Cache-Control", "no-store, no-cache, must-revalidate, max-age=0")
        self.send_header("Pragma", "no-cache")
        self.send_header("Expires", "0")
        super().end_headers()

    def log_message(self, fmt, *args):  # тише в консоли
        sys.stderr.write("%s %s\n" % (self.address_string(), fmt % args))


def main():
    handler = functools.partial(NoCacheHandler, directory=ROOT)
    with http.server.ThreadingHTTPServer(("127.0.0.1", PORT), handler) as httpd:
        print("Сервер без кэша: http://127.0.0.1:%d/  (корень %s)" % (PORT, ROOT))
        print("Страницы: http://127.0.0.1:%d/iiko-ds-mobile/prototypes/recommendations/index.html" % PORT)
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
