"""Сборка макетов телефона для блока «На экране» на страницах рекомендаций.

Разметка компонентов ДС берётся дословно из уже проверенных страниц
(`_audit/rec/data/*.json`), здесь только склейка: экран = корпус + направляющие
блоки. Каждый экран помечен data-mode="mobile", поэтому мобильные значения и
правки из колонки «Правка» действуют и внутри макета.

Пример:
    from mock import *
    html = phones(
        screen(status() + head("Новый заказ") + body(search() + lst([...])) + foot(btn("Отмена"), btn("Создать")),
               "Футер формы: две кнопки в ряд"),
        ...)
"""

STATUS = ('<div class="phone__status"><span>9:41</span><span class="phone__ic">'
          '<span class="material-icons">signal_cellular_alt</span>'
          '<span class="material-icons">wifi</span>'
          '<span class="material-icons">battery_full</span></span></div>')


def status():
    return STATUS


def head(title, left="arrow_back", right="more_vert"):
    return ('<div class="phone__head"><span class="material-icons">%s</span>'
            '<span class="phone__title">%s</span><span class="material-icons">%s</span></div>'
            % (left, title, right))


def body(*blocks):
    return '<div class="phone__body">%s</div>' % "".join(blocks)


def foot(*blocks):
    return '<div class="phone__foot">%s</div>' % "".join(blocks)


def line(*blocks):
    """Строка кнопок в одну линию."""
    return '<div class="phone__line">%s</div>' % "".join(blocks)


def actions(*blocks):
    """Кнопки в столбик, каждая на всю ширину."""
    return '<div class="phone__actions">%s</div>' % "".join(blocks)


def icons(*blocks):
    return '<div class="phone__icons">%s</div>' % "".join(blocks)


def chips(*labels):
    return '<div class="phone__chips">%s</div>' % "".join(
        '<div class="ds-chips ds-chips--outlined"><span class="ds-chips__label">%s</span></div>' % l for l in labels)


def row(text):
    return '<div class="phone__row">%s</div>' % text


def divider():
    return '<hr class="ds-divider ds-divider--m">'


def search(label="Поиск", right="close"):
    r = ('<span class="ds-search__right-icon"><span class="material-icons" style="font-size:24px">%s</span></span>'
         % right) if right else ''
    return ('<div class="ds-search"><span class="ds-search__icon">'
            '<span class="material-icons" style="font-size:24px">search</span></span>'
            '<span class="ds-search__label">%s</span>%s</div>' % (label, r))


def input_field(placeholder="Название процесса", size="m"):
    return ('<div class="ds-input ds-input--%s"><div class="ds-input__frame"><div class="ds-input__content">'
            '<input class="ds-input__field" type="text" placeholder="%s"></div></div></div>' % (size, placeholder))


def lst(items, right_icons=False):
    """items: (иконка, label-up, текст, справа). right_icons=True — справа иконка-кнопки
    (строка передаётся готовой разметкой в четвёртом элементе)."""
    out = []
    for icon, up, text, right in items:
        right_html = ('<div class="ds-list-container__element-right">%s</div>' % right) if right_icons else \
                     ('<div class="ds-list-container__element-right"><span class="ds-list-item__label-down">%s</span></div>' % right)
        out.append('<div class="ds-list-container__item">'
                   '<div class="ds-list-container__element-left"><span class="ds-list-item__icon">'
                   '<span class="material-icons" style="font-size:24px">%s</span></span></div>'
                   '<div class="ds-list-container__content"><span class="ds-list-item__label-up">%s</span>'
                   '<span class="ds-list-item__text">%s</span></div>%s</div>' % (icon, up, text, right_html))
    return '<div class="ds-list-container">%s</div>' % "".join(out)


def btn(label, style="accent", typ="filled", icon=None, trailing=False, size="m"):
    ic = '<span class="ds-btn__icon material-icons">%s</span>' % icon if icon else ''
    inner = (('<span class="ds-btn__label">%s</span>' % label) + ic) if trailing else \
            (ic + ('<span class="ds-btn__label">%s</span>' % label))
    return '<button class="ds-btn ds-btn--%s ds-btn--%s ds-btn--%s" type="button">%s</button>' % (size, style, typ, inner)


def iconbtn(name, style="neutral", typ="outlined", size="m"):
    return ('<button class="ds-btn-icon ds-btn-icon--%s ds-btn-icon--%s ds-btn-icon--%s" type="button" aria-label="%s">'
            '<span class="ds-btn-icon__icon"><span class="material-icons" style="font-size:20px">%s</span></span></button>'
            % (size, style, typ, name, name))


def checkbox(label, on=False):
    return ('<label class="ds-checkbox"><input class="ds-checkbox__input" type="checkbox"%s>'
            '<span class="ds-checkbox__box"></span><span class="ds-checkbox__label">%s</span></label>'
            % (" checked" if on else "", label))


def radio(label, name, on=False):
    return ('<label class="ds-radio"><input class="ds-radio__input" type="radio" name="%s"%s>'
            '<span class="ds-radio__box"><span class="ds-radio__state"></span></span>'
            '<span class="ds-radio__label">%s</span></label>' % (name, " checked" if on else "", label))


def toggle(label, on=True):
    return ('<label class="ds-slide-toggle"><span class="ds-slide-toggle__row">'
            '<input type="checkbox" class="ds-slide-toggle__input"%s>'
            '<span class="ds-slide-toggle__track"></span>'
            '<span class="ds-slide-toggle__title">%s</span></span></label>' % (" checked" if on else "", label))


def tabs(labels, selected=0):
    return ('<div class="ds-tabs">%s</div>' % "".join(
        '<button class="ds-tab%s" type="button">%s</button>' % (" ds-tab--active" if i == selected else "", l)
        for i, l in enumerate(labels)))


def sheet(title, text, *blocks):
    return ('<div class="phone__scrim"></div><div class="phone__sheet">'
            '<p class="phone__sheet-title">%s</p><p class="phone__sheet-text">%s</p>%s</div>'
            % (title, text, "".join(blocks)))


def card(title, text):
    return '<div class="phone__card"><p class="phone__card-title">%s</p><p class="phone__card-text">%s</p></div>' % (title, text)


def screen(inner, caption):
    return ('<div class="phones__item"><div class="phone"><div class="phone__screen" data-mode="mobile">%s</div></div>'
            '<p class="phone__caption">%s</p></div>' % (inner, caption))


def phones(*screens):
    return '<div class="phones">%s</div>' % "".join(screens)


def check_balance(html):
    """Баланс <div> — готовая HTML-строка складывается вручную, ошибки не видно глазами."""
    from html.parser import HTMLParser

    class C(HTMLParser):
        def __init__(self):
            super().__init__(); self.d = 0; self.err = []

        def handle_starttag(self, t, a):
            if t == "div": self.d += 1

        def handle_endtag(self, t):
            if t == "div":
                self.d -= 1
                if self.d < 0: self.err.append("лишний </div>")

    c = C(); c.feed(html)
    return c.d, c.err


def plain_icon(name, size=24, color=None):
    """Обычная иконка, не кнопка: в шапках и заголовках это символ, а не компонент."""
    style = 'font-size:%dpx' % size + (';color:%s' % color if color else '')
    return '<span class="material-icons" style="%s">%s</span>' % (style, name)


def card_head(title, text, right=""):
    """Карточка: заголовок с иконками справа и подпись."""
    return ('<div class="phone__card"><div class="phone__card-head"><div>'
            '<p class="phone__card-title">%s</p><p class="phone__card-text">%s</p></div>%s</div></div>'
            % (title, text, right))
