#!/usr/bin/env python3
"""Проверка окружения перед работой — вместо «у меня ничего не работает».

Запуск из корня папки DS:

  python doctor.py

Проверяет: версию Python, наличие репозиториев рядом (iiko-ds, iiko-ds-web, iiko-ds-mobile),
адреса их origin, собраны ли страницы. Ничего не меняет — только смотрит и говорит, что делать.
"""
import os
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ORG = "iiko-DS"
SIBLINGS = ["iiko-ds-web", "iiko-ds-mobile"]
PAGES = os.path.join(HERE, "iiko-ds-mobile", "prototypes", "recommendations")

ok, warn, bad = "  ок   ", "  ...  ", "  !!!  "
problems = []
notes = []


def say(mark, text):
    print("%s %s" % (mark, text))


def git(path, *args):
    return subprocess.run(
        ["git", "-C", path] + list(args),
        capture_output=True, text=True, encoding="utf-8", errors="replace",
    )


print("Проверяю рабочую папку: %s\n" % HERE)

# 1. Python
v = sys.version_info
if v >= (3, 8):
    say(ok, "Python %d.%d.%d" % (v.major, v.minor, v.micro))
else:
    say(bad, "Python %d.%d.%d — нужен 3.8 или новее" % (v.major, v.minor, v.micro))
    problems.append("обновить Python до 3.8+")

# 2. Сам корень
if os.path.isfile(os.path.join(HERE, "serve.py")) and os.path.isfile(os.path.join(HERE, "_audit", "rec", "build.py")):
    say(ok, "это корень рабочей папки (есть serve.py и _audit/rec/build.py)")
else:
    say(bad, "запускать надо из корня папки DS: рядом должны лежать serve.py и папка _audit")
    problems.append("запустить doctor.py из корня папки DS")

# 3. Репозитории рядом и их адреса
for name in ["(корень iiko-ds)"] + SIBLINGS:
    path = HERE if name.startswith("(") else os.path.join(HERE, name)
    label = "iiko-ds" if name.startswith("(") else name
    if not os.path.isdir(os.path.join(path, ".git")):
        say(bad, "%-18s папки нет — репозиторий не склонирован" % label)
        problems.append("склонировать %s в папку DS" % label)
        continue
    url = git(path, "remote", "get-url", "origin").stdout.strip()
    if not url:
        say(bad, "%-18s у origin нет адреса" % label)
        problems.append("%s: не настроен origin" % label)
        continue
    if "/%s/%s" % (ORG, label) not in url.replace("\\", "/"):
        say(warn, "%-18s origin смотрит не туда: %s" % (label, url))
        notes.append("в %s переставить адрес: git -C %s remote set-url origin https://github.com/%s/%s.git"
                     % (label, path, ORG, label))
        continue
    branch = git(path, "rev-parse", "--abbrev-ref", "HEAD").stdout.strip()
    dirty = [l for l in git(path, "status", "--porcelain", "--untracked-files=no").stdout.splitlines() if l.strip()]
    state = "ветка %s" % (branch or "?")
    if dirty:
        state += ", незакоммиченных правок: %d" % len(dirty)
    say(ok, "%-18s адрес верный, %s" % (label, state))

# 4. Собранные страницы
index = os.path.join(PAGES, "index.html")
if os.path.isfile(index):
    count = len([f for f in os.listdir(PAGES) if f.endswith(".html")])
    say(ok, "страницы собраны: %d html в iiko-ds-mobile/prototypes/recommendations/" % count)
else:
    say(warn, "страницы ещё не собраны")
    notes.append("собрать и открыть: python start.py")

print()
if problems:
    print("Что делать:")
    for p in problems:
        print("  -", p)
elif notes:
    print("Мелочи, которые стоит сделать:")
    for n in notes:
        print("  -", n)
else:
    print("Всё в порядке. Работать: python start.py (собрать и открыть страницы)")

if notes and problems:
    print("\nЗаодно:")
    for n in notes:
        print("  -", n)
