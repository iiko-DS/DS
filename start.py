#!/usr/bin/env python3
"""Собрать страницы и сразу открыть их в браузере — одна команда.

  python start.py              собрать и поднять сервер на порту 8899
  python start.py 9000         другой порт
  python start.py --no-build   не пересобирать, только открыть сервер

Это то же самое, что `python _audit/rec/build.py` плюс `python serve.py`,
просто за один шаг. Страницы открываются по адресу, который напечатает сервер.
"""
import os
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
BUILD = os.path.join("_audit", "rec", "build.py")


def main():
    args = [a for a in sys.argv[1:] if a != "--no-build"]
    skip_build = "--no-build" in sys.argv[1:]

    if not os.path.isfile(os.path.join(HERE, BUILD)):
        print("Запускать из корня папки DS: рядом должен лежать %s" % BUILD)
        return 1

    if not skip_build:
        print("Собираю страницы...")
        result = subprocess.run([sys.executable, BUILD], cwd=HERE)
        if result.returncode != 0:
            print("\nСборка упала — смотри текст ошибки выше. Проверить окружение: python doctor.py")
            return result.returncode

    print("\nПоднимаю локальный сервер (остановить — Ctrl+C)...")
    return subprocess.run([sys.executable, os.path.join(HERE, "serve.py")] + args, cwd=HERE).returncode


if __name__ == "__main__":
    sys.exit(main())
