#!/usr/bin/env python3
"""Проверка окружения перед работой — вместо «у меня ничего не работает».

Запуск из корня папки DS:

  python doctor.py

Проверяет: версию Python, корень DS и адрес его origin, папки components-web и components-mobile
внутри, соседнюю папку Prototypes, собраны ли страницы. Ничего не меняет — только смотрит
и говорит, что делать.
"""
import os
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ORG = "iiko-DS"
FOLDERS = ["components-web", "components-mobile"]
PAGES = os.path.join(HERE, "components-mobile", "prototypes", "recommendations")

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

# 3. Корень DS: git-репозиторий, адрес origin и состояние
if not os.path.isdir(os.path.join(HERE, ".git")):
    say(bad, "%-18s не git-репозиторий — запускать из корня склонированного DS" % "DS")
    problems.append("запустить doctor.py из корня папки DS")
else:
    url = git(HERE, "remote", "get-url", "origin").stdout.strip()
    if not url:
        say(bad, "%-18s у origin нет адреса" % "DS")
        problems.append("DS: не настроен origin")
    elif "/%s/%s" % (ORG, "DS") not in url.replace("\\", "/"):
        say(warn, "%-18s origin смотрит не туда: %s" % ("DS", url))
        notes.append("в DS переставить адрес: git -C %s remote set-url origin https://github.com/%s/DS.git" % (HERE, ORG))
    else:
        branch = git(HERE, "rev-parse", "--abbrev-ref", "HEAD").stdout.strip()
        dirty = [l for l in git(HERE, "status", "--porcelain", "--untracked-files=no").stdout.splitlines() if l.strip()]
        state = "ветка %s" % (branch or "?")
        if dirty:
            state += ", незакоммиченных правок: %d" % len(dirty)
        say(ok, "%-18s адрес верный, %s" % ("DS", state))

# 3a. Папки слоёв ДС внутри DS
for name in FOLDERS:
    path = os.path.join(HERE, name)
    if os.path.isdir(path):
        say(ok, "%-18s на месте (папка внутри DS)" % name)
    else:
        say(bad, "%-18s папки нет — репозиторий DS склонирован неполно" % name)
        problems.append("%s: нет папки внутри DS" % name)

# 3b. Prototypes — соседняя папка
proto = os.path.normpath(os.path.join(HERE, "..", "Prototypes"))
if os.path.isdir(os.path.join(proto, ".git")):
    url = git(proto, "remote", "get-url", "origin").stdout.strip()
    if "/%s/%s" % (ORG, "Prototypes") in url.replace("\\", "/"):
        say(ok, "%-18s рядом, адрес верный" % "Prototypes")
    else:
        say(warn, "%-18s origin смотрит не туда: %s" % ("Prototypes", url))
        notes.append("в Prototypes переставить адрес: git -C %s remote set-url origin https://github.com/%s/Prototypes.git" % (proto, ORG))
else:
    say(warn, "%-18s папки нет рядом — если нужна работа с прототипами, клонировать её рядом с DS" % "Prototypes")
    notes.append("склонировать Prototypes рядом с папкой DS")

# 4. Собранные страницы
index = os.path.join(PAGES, "index.html")
if os.path.isfile(index):
    count = len([f for f in os.listdir(PAGES) if f.endswith(".html")])
    say(ok, "страницы собраны: %d html в components-mobile/prototypes/recommendations/" % count)
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
