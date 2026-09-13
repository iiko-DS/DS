# -*- coding: utf-8 -*-
"""Дописать новые паттерны (партия 6) из out/new-patterns/<slug>.json
в конец out/patterns/<slug>.json. Старое не трогаем.
Примеры — разметка ДС (классы из data/<slug>.json -> examples[].html),
узкий экран — в <div class="pat__phone">."""
import json
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
NP = os.path.join(HERE, "out", "new-patterns")
PAT = os.path.join(HERE, "out", "patterns")
sys.path.insert(0, HERE)
from mock import check_balance  # noqa: E402

# --- примеры: по слагу, список (example_html, example_ru) в том же порядке, что new-patterns ---
EXAMPLES = {
 "tabs": [
  (
   '<div class="pat__phone">'
   '<div class="ds-tabs"><button class="ds-tab ds-tab--selected" type="button">Новый заказ'
   '<span class="ds-tab__icon"><span class="material-icons" style="font-size:20px">close</span></span></button>'
   '<button class="ds-tab" type="button">Меню</button></div>'
   '<div class="ds-snackbar ds-snackbar--dark"><div class="ds-snackbar__body">'
   '<span class="ds-snackbar__label">Вкладка «Новый заказ» закрыта · позиции не сохранены</span></div>'
   '<button class="ds-snackbar__button" type="button">Вернуть</button></div>'
   '</div>',
   'Крестик съёма — отдельная цель 44 px внутри вкладки с зазором от подписи, а после закрытия вкладки '
   'в снекбаре есть «Вернуть»: вкладка с несохранёнными позициями не исчезает молча.'
  ),
  (
   '<div class="pat__phone">'
   '<div class="phone__head"><span class="material-icons">arrow_back</span>'
   '<div class="phone__title">Заказы · Зал 2</div><span class="material-icons">more_vert</span></div>'
   '<div class="ds-tabs"><button class="ds-tab ds-tab--selected" type="button">Активные</button>'
   '<button class="ds-tab" type="button">Закрытые</button><button class="ds-tab" type="button">Отменённые</button></div>'
   '<div style="height:96px;overflow-y:auto;padding:0 16px">'
   '<p style="font-size:14px;line-height:20px;margin:0 0 8px">Стол 4 · 12 позиций</p>'
   '<p style="font-size:14px;line-height:20px;margin:0 0 8px">Стол 7 · 5 позиций</p>'
   '<p style="font-size:14px;line-height:20px;margin:0">Стол 2 · 9 позиций</p></div>'
   '</div>',
   'Полоса вкладок остаётся на экране (сверху, под шапкой), пока содержимое под ней прокручивается: '
   'активная вкладка не уезжает вместе со списком.'
  ),
  (
   '<div class="pat__phone">'
   '<div class="ds-tabs"><button class="ds-tab" type="button">Заказы</button>'
   '<button class="ds-tab ds-tab--selected" type="button">Смены</button>'
   '<button class="ds-tab" type="button">Отчёты</button></div>'
   '<div style="padding:24px 16px;text-align:center">'
   '<span class="material-icons" style="font-size:40px;color:#9E9E9E">event_busy</span>'
   '<p style="font-size:14px;line-height:20px;margin:8px 0 16px">Смен пока нет — закройте кассу, чтобы смена появилась</p>'
   '<button class="ds-btn ds-btn--accent" type="button">Открыть смену</button></div>'
   '</div>',
   'Пустая вкладка «Смены» остаётся доступной и показывает пустое состояние с объяснением и действием: '
   'состав и порядок вкладок на экране не меняется, раздел не исчезает.'
  ),
 ],
 "chips": [
  (
   '<div class="pat__phone">'
   '<div class="ds-chips-group">'
   '<div class="ds-chips ds-chips--filled"><span class="ds-chips__label">Сыр</span></div>'
   '<div class="ds-chips ds-chips--filled"><span class="ds-chips__label">Соус</span></div>'
   '<div class="ds-chips ds-chips--outlined"><span class="ds-chips__label">Острое</span></div>'
   '</div>'
   '<button class="ds-btn ds-btn--accent" type="button">Показать 12</button>'
   '</div>',
   'Тап по чипу только помечает фильтр, а список перестраивается по кнопке «Показать 12»: '
   'серия тапов подряд больше не перезагружает список и не сдвигает его под пальцем.'
  ),
  (
   '<div class="pat__phone">'
   '<div class="ds-chips-group">'
   '<div class="ds-chips ds-chips--filled"><span class="ds-chips__label">Сыр</span></div>'
   '<div class="ds-chips ds-chips--filled"><span class="ds-chips__label">Соус</span></div>'
   '<div class="ds-chips ds-chips--filled"><span class="ds-chips__label">Хлеб</span></div>'
   '</div>'
   '<div style="display:flex;gap:8px"><button class="ds-btn ds-btn--neutral ds-btn--outlined" type="button" '
   'style="flex:1">Сбросить</button><button class="ds-btn ds-btn--accent" type="button" style="flex:1">'
   'Показать 12</button></div>'
   '</div>',
   'Выбранные чипы сохраняются, пока панель фильтров открыта: набор применяется по кнопке, '
   'а закрытие слоя тапом по фону не выбрасывает выбранные значения.'
  ),
  (
   '<div class="pat__phone">'
   '<div style="overflow-x:auto"><div class="ds-chips-group" style="flex-wrap:nowrap">'
   '<div class="ds-chips ds-chips--outlined"><span class="ds-chips__label">Сыр</span></div>'
   '<div class="ds-chips ds-chips--outlined"><span class="ds-chips__label">Соус</span></div>'
   '<div class="ds-chips ds-chips--outlined"><span class="ds-chips__label">Хлеб</span></div>'
   '<div class="ds-chips ds-chips--outlined"><span class="ds-chips__label">Острое</span></div>'
   '<div class="ds-chips ds-chips--outlined"><span class="ds-chips__label">Веган</span></div>'
   '</div></div>'
   '<div class="ds-chips ds-chips--filled"><span class="ds-chips__label">Соус</span>'
   '<span class="ds-chips__close"><span class="material-icons" style="font-size:18px">close</span></span></div>'
   '</div>',
   'Полоса чипов прокручивается свайпом по горизонтали, а снятие фильтра живёт на крестике внутри чипа: '
   'на один жест — одно действие, свайпа на снятие нет.'
  ),
 ],
 "chips-input": [
  (
   '<div class="pat__phone">'
   '<div class="ds-chips-input" style="width:100%"><span class="ds-chips-input__label">Метки</span>'
   '<div class="ds-chips-input__frame"><div class="ds-chips-input__content" style="flex-wrap:wrap">'
   '<div class="ds-chips ds-chips--outlined"><span class="ds-chips__label">Сыр</span></div>'
   '<div class="ds-chips ds-chips--outlined"><span class="ds-chips__label">Соус</span></div>'
   '<div class="ds-chips ds-chips--outlined"><span class="ds-chips__label">Хлеб</span></div>'
   '<input type="text" placeholder="Добавить метку" '
   'style="border:0;background:none;font:inherit;color:inherit;outline:none;width:100%">'
   '</div></div></div>'
   '</div>',
   'Вставленный текст «Сыр, Соус, Хлеб» разобран по разделителям на три метки, курсор остался в поле: '
   'значения не приходится набирать заново по одному.'
  ),
  (
   '<div class="pat__phone">'
   '<div class="ds-chips-input" style="width:100%"><span class="ds-chips-input__label">Метки</span>'
   '<div class="ds-chips-input__frame"><div class="ds-chips-input__content" style="flex-wrap:wrap">'
   '<div class="ds-chips ds-chips--outlined"><span class="ds-chips__label">Бекон</span></div>'
   '<input type="text" value="Сыр козий" '
   'style="border:0;background:none;font:inherit;color:inherit;outline:none;width:100%">'
   '</div></div></div>'
   '<div style="display:flex;gap:8px"><button class="ds-btn ds-btn--neutral ds-btn--text" type="button" '
   'style="flex:1">Закрыть</button><button class="ds-btn ds-btn--accent" type="button" style="flex:1">'
   'Добавить</button></div>'
   '</div>',
   'Набранное значение стоит в поле до нажатия «Добавить», и кнопка действия рядом с ним: '
   'закрытие слоя не выбрасывает текст молча.'
  ),
  (
   '<div class="pat__phone">'
   '<div class="ds-chips-input" style="width:100%"><span class="ds-chips-input__label">Метки</span>'
   '<div class="ds-chips-input__frame"><div class="ds-chips-input__content">'
   '<input type="text" value="Сыр козий" '
   'style="border:0;background:none;font:inherit;color:inherit;outline:none;width:100%">'
   '</div></div></div>'
   '<div style="border-top:1px solid #E6E8EB;padding:12px 16px">'
   '<p style="font-size:14px;line-height:20px;margin:0 0 8px">Ничего не найдено — проверьте написание</p>'
   '<button class="ds-btn ds-btn--neutral ds-btn--text" type="button">Создать метку «Сыр козий»</button></div>'
   '</div>',
   'Под полем — понятное пустое состояние с действием «Создать метку «Сыр козий»»: человек видит, '
   'что совпадений нет, и может завести новое значение вместо тупика.'
  ),
 ],
 "icon-size": [
  (
   '<div class="pat__phone">'
   '<div style="display:flex;align-items:center;gap:12px">'
   '<span class="ds-icon-group__icon" style="width:24px;height:24px">'
   '<span class="material-icons" style="font-size:24px">local_shipping</span></span>'
   '<span style="font-size:16px;line-height:24px">Доставка · стол 4</span></div>'
   '<div style="display:flex;align-items:center;gap:14px">'
   '<span class="ds-icon-group__icon" style="width:28px;height:28px">'
   '<span class="material-icons" style="font-size:28px">local_shipping</span></span>'
   '<span style="font-size:20px;line-height:28px">Доставка · стол 4</span></div>'
   '</div>',
   'При крупном системном кегле строка выросла с 16 до 20 px, и иконка выросла вместе с ней — 24 → 28 px: '
   'подпись и знак остаются одного масштаба, иконка не «тонет» в крупном тексте.'
  ),
  (
   '<div class="pat__phone pat__phone-row" style="gap:24px;justify-content:flex-start">'
   '<span class="pat__hit"><span class="ds-icon-group__icon" style="width:24px;height:24px">'
   '<span class="material-icons" style="font-size:24px">edit</span></span></span>'
   '<span class="pat__hit"><span class="ds-icon-group__icon" style="width:24px;height:24px">'
   '<span class="material-icons" style="font-size:24px">delete</span></span></span>'
   '</div>',
   'Пунктиром показана цель 48 px вокруг иконок без подложки: паддинг вокруг видимого края знака '
   '(Apple — 24 pt) и зазор между соседними иконками — часть цели нажатия, а не пустое место.'
  ),
  (
   '<div class="pat__phone">'
   '<div style="display:flex;align-items:center;gap:12px">'
   '<span class="ds-icon-group__icon" style="width:16px;height:16px">'
   '<span class="material-icons" style="font-size:16px">print</span></span>'
   '<span style="font-size:14px;line-height:20px">Печать пречека</span></div>'
   '<div style="display:flex;align-items:center;gap:12px">'
   '<span class="ds-icon-group__icon" style="width:24px;height:24px">'
   '<span class="material-icons" style="font-size:24px">print</span></span>'
   '<span style="font-size:14px;line-height:20px">Печать пречека</span></div>'
   '</div>',
   'Сверху иконка ужата до 16 px — тонкие штрихи «принтера» сливаются в пятно; снизу та же строка '
   'с иконкой 24 px: ниже 20 px в ДС знак не опускается, ради этого не сужают подпись.'
  ),
 ],
 "divider": [
  (
   '<div class="pat__phone">'
   '<div style="display:flex;align-items:center;justify-content:space-between;height:48px">'
   '<span style="font-size:16px">Оплатить</span><span class="material-icons">chevron_right</span></div>'
   '<hr class="ds-divider ds-divider--m">'
   '<div style="display:flex;align-items:center;justify-content:space-between;height:48px">'
   '<span style="font-size:16px">Отменить заказ</span><span class="material-icons">chevron_right</span></div>'
   '</div>',
   'Линия 1 px разделяет две нажимаемые строки по 48 px: палец видит, где кончается «Оплатить» '
   'и начинается «Отменить заказ», — без линий цели сливаются в один блок.'
  ),
  (
   '<div class="pat__phone">'
   '<div style="display:flex;align-items:center;height:48px;font-size:16px">Изменить</div>'
   '<div style="display:flex;align-items:center;height:48px;font-size:16px">Печатать</div>'
   '<hr class="ds-divider ds-divider--m">'
   '<div style="display:flex;align-items:center;height:48px;font-size:16px;color:#C62828">Удалить</div>'
   '</div>',
   'Разрушительное «Удалить» стоит ниже линии, отдельно от основных действий строки: '
   'одного только отступа до него мало, линия отделяет действие с необратимым результатом.'
  ),
  (
   '<div class="pat__phone">'
   '<div style="display:flex;justify-content:space-between;font-size:14px;line-height:20px">'
   '<span>Сумма</span><span>2 480 ₽</span></div>'
   '<hr class="ds-divider ds-divider--lite" style="width:calc(100% - 32px);margin:8px auto">'
   '<div style="display:flex;justify-content:space-between;font-size:14px;line-height:20px">'
   '<span>Скидка</span><span>− 240 ₽</span></div>'
   '<hr class="ds-divider ds-divider--m">'
   '<div style="display:flex;justify-content:space-between;font-size:14px;line-height:20px">'
   '<span>Оплата картой</span><span>2 240 ₽</span></div>'
   '</div>',
   'Внутри блока связанные строки «Сумма» и «Скидка» разделены линией с отступом 16 px от обеих сторон, '
   'а линия от края до края стоит только между несвязанными частями блока: блок не распадается.'
  ),
 ],
 "logo": [
  (
   '<div class="pat__phone" data-mode="mobile">'
   '<div style="height:88px;display:flex;align-items:center;justify-content:center;'
   'background:#EDEFF3;border-radius:8px">'
   '<span class="material-icons" style="font-size:32px;color:#9E9E9E">schedule</span></div>'
   '<div class="phone__head"><div class="ds-logo-iiko">'
   '<span class="ds-logo-iiko__vector" style="width:72px;background:#EDEFF3"></span></div>'
   '<div class="phone__title">Заказы · Зал 2</div><span class="material-icons">more_vert</span></div>'
   '</div>',
   'Первый экран — нейтральная подложка загрузки без знака, а логотип живёт только в шапке: '
   'сплэш-экран в ДС не носитель бренда, он не отодвигает работу.'
  ),
  (
   '<div class="pat__phone" data-mode="mobile">'
   '<div class="phone__head"><div class="ds-logo-iiko">'
   '<span class="ds-logo-iiko__vector" style="width:72px;background:#EDEFF3"></span></div>'
   '<div class="phone__title">Заказы</div><span class="material-icons">more_vert</span></div>'
   '<div style="padding:12px 16px 0"><div class="ds-logo-syrve">'
   '<span class="ds-logo-syrve__vector" style="width:150px"></span></div>'
   '<p style="font-size:14px;line-height:20px;margin:8px 0 0">Полная версия знака — на широком экране</p></div>'
   '</div>',
   'В шапке — знак-графика 72 px, который не участвует в масштабировании системного текста, '
   'а полная надпись 150 px стоит только там, где есть ширина: кегль логотипа не ломается.'
  ),
  (
   '<div class="pat__phone" data-mode="mobile">'
   '<div class="phone__head"><a href="#" style="display:flex;align-items:center">'
   '<div class="ds-logo-iiko"><span class="ds-logo-iiko__vector" style="width:72px;background:#EDEFF3"></span>'
   '</div></a><div class="phone__title">Заказы · Зал 2</div>'
   '<span class="material-icons">more_vert</span></div>'
   '<div style="padding:12px 16px;font-size:14px;line-height:20px">'
   'Знак ведёт на главную и не сбрасывает выбранный зал</div>'
   '</div>',
   'В шапке — только знак и заголовок с выбранным залом: знак обёрнут в ссылку на главную, '
   'рядом с ним нет названия сервиса и ссылок разделов, а выбранный зал при тапе не сбрасывается.'
  ),
 ],
}

SLUGS = ["tabs", "chips", "chips-input", "icon-size", "divider", "logo"]


def with_prefix(text, label):
    """В части заготовок пункт уже начинается с названия — второй раз не добавляем."""
    return text if text.startswith(label) else label + ": " + text


def fmt_entry(e):
    """Запись в том же виде, в каком лежат уже дописанные: отступ 1, плюс один уровень."""
    s = json.dumps(e, ensure_ascii=False, indent=1)
    return "\r\n".join("  " + line for line in s.split("\n"))


def append_surgical(path, entries):
    """Дописать записи в конец patterns_ru, не перезаписывая старое (байты старого
    куска остаются как были: строки и переносы не трогаем)."""
    raw = open(path, encoding="utf-8", newline="").read()
    mm = list(re.finditer(r"\r?\n  \}", raw))
    assert mm, path
    idx = mm[-1]
    rest = raw[idx.end():]
    assert re.match(r"^\s*\]\s*\}\s*$", rest), (path, repr(rest))
    text = ",\r\n".join(fmt_entry(e) for e in entries)
    with open(path, "w", encoding="utf-8", newline="") as f:
        f.write(raw[:idx.end()] + ",\r\n" + text + rest)
    json.load(open(path, encoding="utf-8"))  # проверка, что файл читается


report = []
for slug in SLUGS:
    src_new = os.path.join(NP, slug + ".json")
    dst = os.path.join(PAT, slug + ".json")
    new = json.load(open(src_new, encoding="utf-8"))
    data = json.load(open(dst, encoding="utf-8"))
    existing = data.get("patterns_ru") or []
    ex = EXAMPLES[slug]
    assert len(ex) == len(new), (slug, len(ex), len(new))
    have = {p.get("title") for p in existing}
    added = []
    for i, n in enumerate(new):
        if not n.get("quote") or n.get("verified") is False:
            print("  пропуск (нет цитаты/не подтверждено): %s — %s" % (slug, n.get("situation")))
            continue
        title = n["situation"]
        if title in have:
            print("  пропуск (уже есть): %s — %s" % (slug, title))
            continue
        who = str(n["who"]).split(" — ")[0].strip()
        bad, err = check_balance(ex[i][0])
        assert bad == 0 and not err, (slug, i, bad, err)
        added.append({
            "title": title,
            "items": [
                with_prefix(n["happens"], "Что происходит"),
                with_prefix(n["systems"], "Что делают системы"),
                with_prefix(n["us"], "Что делать нам"),
            ],
            "src": "Источники: %s (%s)" % (who, n["url"]),
            "example_html": ex[i][0],
            "example_ru": ex[i][1],
        })
        have.add(title)
    before = len(existing)
    data["patterns_ru"] = existing + added
    if added:
        append_surgical(dst, added)
    report.append((slug, before, len(added), len(data["patterns_ru"])))

for slug, before, added, after in report:
    print("%s: было %d, добавлено %d, стало %d" % (slug, before, added, after))
