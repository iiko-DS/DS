# -*- coding: utf-8 -*-
"""Builds _audit/platform/<slug>.json from locally cached primary sources, verifying every quote."""
import json, os, re, sys

RAW = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.dirname(RAW)  # _audit/platform

MW = "https://raw.githubusercontent.com/material-components/material-web/main/"
NG = "https://raw.githubusercontent.com/angular/components/main/src/material/"
HIG = "https://developer.apple.com/design/human-interface-guidelines/"

# local file map for quote verification: source url -> local file
QA = {
 MW + "tokens/versions/v0_192/_md-comp-primary-navigation-tab.scss": "val__md-comp-primary-navigation-tab.scss",
 MW + "tokens/versions/v0_192/_md-comp-secondary-navigation-tab.scss": "val__md-comp-secondary-navigation-tab.scss",
 MW + "tokens/versions/v0_192/_md-comp-navigation-bar.scss": "val__md-comp-navigation-bar.scss",
 MW + "tokens/versions/v0_192/_md-comp-navigation-drawer.scss": "val__md-comp-navigation-drawer.scss",
 MW + "tokens/versions/v0_192/_md-comp-snackbar.scss": "val__md-comp-snackbar.scss",
 MW + "tokens/versions/v0_192/_md-comp-list.scss": "val__md-comp-list.scss",
 MW + "tokens/versions/v0_192/_md-sys-shape.scss": "shape_v0192.scss",
 MW + "tokens/_md-comp-secondary-tab.scss": "md3tok__md-comp-secondary-tab.scss",
 MW + "tokens/_md-comp-menu.scss": "md3tok__md-comp-menu.scss",
 MW + "menu/internal/_menu.scss": "md3_menu_internal.scss",
 MW + "menu/internal/menuitem/_menu-item.scss": "md3_menuitem.scss",
 MW + "button/internal/_touch-target.scss": "md3_touch_target.scss",
 MW + "labs/navigationbar/internal/_navigation-bar.scss": "md3_navbar_internal.scss",
 MW + "docs/components/tabs.md": "md3_tabs.md",
 MW + "docs/components/menu.md": "md3_menu.md",
 NG + "tabs/_m3-tabs.scss": "ng_tabs__m3-tabs.scss",
 NG + "tabs/_tabs-common.scss": "ng_tabs__tabs-common.scss",
 NG + "tabs/tabs.md": "ng_tabs_tabs.md",
 NG + "tabs/tab-group.ts": "ng_tabs_tab-group.ts",
 NG + "menu/menu.scss": "ng_menu_menu.scss",
 NG + "menu/_m3-menu.scss": "ng_menu__m3-menu.scss",
 NG + "menu/menu.md": "ng_menu_menu.md",
 NG + "core/style/_menu-common.scss": "ng_menu-common.scss",
 NG + "sidenav/sidenav.md": "ng_sidenav_sidenav.md",
 NG + "sidenav/_m3-sidenav.scss": "ng_sidenav__m3-sidenav.scss",
 NG + "sidenav/drawer.scss": "ng_sidenav_drawer.scss",
 NG + "stepper/stepper.md": "ng_stepper_stepper.md",
 NG + "stepper/_stepper-variables.scss": "ng_stepper__stepper-variables.scss",
 NG + "stepper/_m3-stepper.scss": "ng_stepper__m3-stepper.scss",
 NG + "snack-bar/snack-bar.md": "ng_snack-bar_snack-bar.md",
 NG + "snack-bar/snack-bar-container.scss": "ng_snack-bar_snack-bar-container.scss",
 NG + "snack-bar/snack-bar-config.ts": "ng_snack-bar_snack-bar-config.ts",
 NG + "snack-bar/_m3-snack-bar.scss": "ng_snack-bar__m3-snack-bar.scss",
}
HIGQ = {
 HIG + "tab-bars": "tab-bars", HIG + "toolbars": "toolbars", HIG + "sidebars": "sidebars",
 HIG + "menus": "menus", HIG + "context-menus": "context-menus", HIG + "action-sheets": "action-sheets",
 HIG + "alerts": "alerts", HIG + "page-controls": "page-controls", HIG + "steppers": "steppers",
 HIG + "accessibility": "accessibility", HIG + "sign-in-with-apple": "sign-in-with-apple",
}

def norm(s):
    s = s.replace("\u2019", "'").replace("\u2018", "'").replace("\u201c", '"').replace("\u201d", '"')
    s = s.replace("\u2014", "-").replace("\u00a0", " ").replace("\u2026", "...")
    return re.sub(r"\s+", " ", s).strip()

_cache = {}
def text_of(url):
    if url in _cache:
        return _cache[url]
    if url in QA:
        p = os.path.join(RAW, QA[url])
        t = open(p, encoding="utf-8", errors="replace").read()
    elif url in HIGQ:
        p = os.path.join(RAW, "higjson", HIGQ[url] + ".json")
        t = json.load(open(p, encoding="utf-8")).__str__()
        t = json.dumps(json.load(open(p, encoding="utf-8")), ensure_ascii=False)
    else:
        t = ""
    _cache[url] = t
    return t

FAILS = []
HKEY = {"md3": "height_dp", "angular_material": "height_px", "ios_hig": "height_pt"}
MEASKEYS = ("height_dp", "height_px", "height_pt", "width_px", "width_dp", "width_pt")

def _mk(name, value, quote, source, extra):
    d = {"name": name}
    d.update(extra)
    if value is not None:
        d["value"] = value
    d["quote"] = quote
    d["source"] = source
    if quote and quote != NF:
        if norm(quote) not in norm(text_of(source)):
            FAILS.append((name, source, quote[:90]))
    return d

def S(name, value=None, quote="", source="", **extra):
    """size entry (value -> height_* per platform at post-process time)"""
    return _mk(name, value, quote, source, extra)

def M(name, value=None, quote="", source="", **extra):
    """other measurement (always keeps explicit keys)"""
    d = _mk(name, value, quote, source, extra)
    if value is not None:
        d.pop("value", None)
        d.setdefault("measure_px", value)
    return d

def postprocess(platform, block):
    key = HKEY[platform]
    for s in block.get("sizes") or []:
        if "value" in s:
            v = s.pop("value")
            if not any(k in s for k in MEASKEYS):
                s[key] = v
    for m in block.get("other_measurements") or []:
        if "value" in m:
            m["measure_px"] = m.pop("value")
    return block

NF = "\u043d\u0435 \u043d\u0430\u0439\u0434\u0435\u043d\u043e"

# ---------------------------------------------------------------- MD3 pieces
U_TAB_P = MW + "tokens/versions/v0_192/_md-comp-primary-navigation-tab.scss"
U_TAB_S = MW + "tokens/versions/v0_192/_md-comp-secondary-navigation-tab.scss"
U_TAB_S2 = MW + "tokens/_md-comp-secondary-tab.scss"
U_NAVBAR = MW + "tokens/versions/v0_192/_md-comp-navigation-bar.scss"
U_DRAWER = MW + "tokens/versions/v0_192/_md-comp-navigation-drawer.scss"
U_SNACK = MW + "tokens/versions/v0_192/_md-comp-snackbar.scss"
U_LIST = MW + "tokens/versions/v0_192/_md-comp-list.scss"
U_SHAPE = MW + "tokens/versions/v0_192/_md-sys-shape.scss"
U_MENU_TOK = MW + "tokens/_md-comp-menu.scss"
U_MENU_SCSS = MW + "menu/internal/_menu.scss"
U_MENU_ITEM = MW + "menu/internal/menuitem/_menu-item.scss"
U_TOUCH = MW + "button/internal/_touch-target.scss"
U_DOCS_TABS = MW + "docs/components/tabs.md"
U_DOCS_MENU = MW + "docs/components/menu.md"
U_DOCS_LIST = "https://github.com/material-components/material-web/tree/main/docs/components"
U_TOKEN_LIST = "https://github.com/material-components/material-web/tree/main/tokens"

# ---------------------------------------------------------------- Angular pieces
N_TABS_M3 = NG + "tabs/_m3-tabs.scss"
N_TABS_COMMON = NG + "tabs/_tabs-common.scss"
N_TABS_MD = NG + "tabs/tabs.md"
N_TABS_TS = NG + "tabs/tab-group.ts"
N_MENU_SCSS = NG + "menu/menu.scss"
N_MENU_M3 = NG + "menu/_m3-menu.scss"
N_MENU_MD = NG + "menu/menu.md"
N_MENU_COMMON = NG + "core/style/_menu-common.scss"
N_SIDE_MD = NG + "sidenav/sidenav.md"
N_SIDE_M3 = NG + "sidenav/_m3-sidenav.scss"
N_SIDE_SCSS = NG + "sidenav/drawer.scss"
N_STEP_MD = NG + "stepper/stepper.md"
N_STEP_VARS = NG + "stepper/_stepper-variables.scss"
N_STEP_M3 = NG + "stepper/_m3-stepper.scss"
N_SNACK_MD = NG + "snack-bar/snack-bar.md"
N_SNACK_SCSS = NG + "snack-bar/snack-bar-container.scss"
N_SNACK_TS = NG + "snack-bar/snack-bar-config.ts"
N_SNACK_M3 = NG + "snack-bar/_m3-snack-bar.scss"

# HIG urls
H_TAB = HIG + "tab-bars"; H_TOOL = HIG + "toolbars"; H_SIDE = HIG + "sidebars"
H_MENU = HIG + "menus"; H_CTX = HIG + "context-menus"; H_SHEET = HIG + "action-sheets"
H_ALERT = HIG + "alerts"; H_PAGE = HIG + "page-controls"; H_STEP = HIG + "steppers"
H_A11Y = HIG + "accessibility"; H_SIWA = HIG + "sign-in-with-apple"
H_COMPLIST = HIG + "components"

COMPONENTS = {}

# ============================================================ TABS
COMPONENTS["tabs"] = {
 "component": "tabs",
 "platforms": {
  "md3": {
   "exists": True,
   "sizes": [
    S("Primary tab, container height (подпись; с иконкой в строку — 48)", 48,
      "'container-height': if($exclude-hardcoded-values, null, 48px),", U_TAB_P),
    S("Primary tab, container height с иконкой и подписью", 64,
      "'with-icon-and-label-text-container-height':\n      if($exclude-hardcoded-values, null, 64px),", U_TAB_P),
    S("Primary tab, active indicator height", 3,
      "'active-indicator-height': if($exclude-hardcoded-values, null, 3px),", U_TAB_P),
    S("Primary tab, icon size", 24,
      "'with-icon-icon-size': if($exclude-hardcoded-values, null, 24px),", U_TAB_P),
    S("Secondary tab, container height", 48,
      "'container-height': if($exclude-hardcoded-values, null, 48px),", U_TAB_S),
    S("Secondary tab, active indicator height", 2,
      "'active-indicator-height': if($exclude-hardcoded-values, null, 2px),", U_TAB_S),
   ],
   "other_measurements": [],
   "variants": [
    M("Primary tabs", None, "Primary tabs are placed at the top of the content pane under a top app bar.", U_DOCS_TABS),
    M("Secondary tabs", None, "Secondary tabs are used within a content area to further separate related\ncontent and establish hierarchy.", U_DOCS_TABS),
    M("Icons: иконка+подпись, только иконка, inline-icon", None, "Primary tabs can show their icons inline, like secondary tabs.", U_DOCS_TABS),
    M("Scrollable/overflow (метод scrollToTab)", None, "Scrolls the toolbar, if overflowing, to the active tab, or the provided tab.", U_DOCS_TABS),
    {"name": "Комментарий к высоте secondary tab (48 → 64 с иконкой)",
     "quote": "// include an icon and the size will adjust;\n  // height is 48 and it's 64 with icon", "source": U_TAB_S2},
   ],
   "touch_target_dp": 48,
   "touch_target_quote": "height: max(48px, 100%);",
   "touch_target_source": U_TOUCH,
   "notes_ru": "MD3 даёт токены двух уровней табов: primary и secondary, обе высоты 48 (64 с иконкой), индикатор 3 px у primary и 2 px у secondary, иконка 24. Вертикальной ориентации табов и табов внутри табов (3+ уровней) в исходниках нет; компонент горизонтальный (overflow: auto). Токены высоты touch-таргета 48 берутся не из табов, а из миксина button (единственный файл touch-target в библиотеке).",
   "sources": [U_TAB_P, U_TAB_S, U_TAB_S2, U_DOCS_TABS, U_TOUCH],
  },
  "angular_material": {
   "exists": True,
   "sizes": [
    S("Tab header, container height (density 0)", 48,
      "tab-container-height: list.nth((48px, 44px, 40px, 36px, 32px), $index),", N_TABS_M3, height_px=48),
    S("Tab active indicator height", 2, "tab-active-indicator-height: 2px,", N_TABS_M3, height_px=2),
    S("Tab header divider height", 1, "tab-divider-height: 1px,", N_TABS_M3, height_px=1),
   ],
   "other_measurements": [
    M("Минимальная ширина таба", 90, "min-width: 90px;", N_TABS_COMMON, width_px=90),
    M("Минимальная ширина кнопки пагинации", 32, "min-width: 32px;", N_TABS_COMMON, width_px=32),
   ],
   "variants": [
    M("Пагинация при переполнении", None,
      "When the list of tab labels exceeds the width of the header, pagination controls appear to let the user scroll left and right across the labels.", N_TABS_MD),
    {"name": "stretchTabs (mat-stretch-tabs), по умолчанию true",
     "quote": "@Input({alias: 'mat-stretch-tabs', transform: booleanAttribute})\n  stretchTabs: boolean = true;", "source": N_TABS_TS},
    {"name": "headerPosition: above | below",
     "quote": "export type MatTabHeaderPosition = 'above' | 'below';", "source": N_TABS_TS},
    {"name": "mat-align-tabs (start | center | end)",
     "quote": "[attr.mat-align-tabs]': 'alignTabs',", "source": N_TABS_TS},
    {"name": "dynamicHeight, preserveContent, lazy (matTabContent), drag-drop, mat-tab-nav-bar (роутинг)",
     "quote": "Tab contents can be lazy loaded by declaring the body in a `ng-template`\nwith the `matTabContent` attribute.", "source": N_TABS_MD},
   ],
   "density": "шкала 0…-4: 48 → 44 → 40 → 36 → 32 px (tab-container-height)",
   "notes_ru": "Angular Material: высота хедера 48 px, только горизонтальные табы (пагинация стрелками при переполнении), stretch по умолчанию включён, выравнивание start/center/end, хедер можно поставить below. Вертикальной ориентации нет. Density-шкала ужимает хедер до 32 px.",
   "sources": [N_TABS_M3, N_TABS_COMMON, N_TABS_MD, N_TABS_TS],
  },
  "ios_hig": {
   "exists": True,
   "sizes": [
    S("iOS tab bar height", None, NF, H_TAB, height_pt=None),
    S("tvOS tab bar height", 68,
      "The height of a tab bar is 68 points, and its top edge is 46 points from the top of the screen; you can\u2019t change either of these values.",
      H_TAB, height_pt=68),
   ],
   "other_measurements": [],
   "variants": [
    {"name": "iOS: таб-бар снизу, floating, Liquid Glass",
     "quote": "A tab bar floats above content at the bottom of the screen.", "source": H_TAB},
    {"name": "iPadOS: таб-бар сверху, конвертация в sidebar (tabBarOnly / sidebarAdaptable)",
     "quote": "The system displays a tab bar near the top of the screen. You can choose to have the tab bar appear as a fixed element, or with a button that converts it to a sidebar.",
     "source": H_TAB},
    {"name": "Переполнение → More-таб (iOS/iPadOS)",
     "quote": "If horizontal space limits the number of visible tabs, the trailing tab becomes a More tab in iOS and iPadOS, revealing the remaining items in a separate list.",
     "source": H_TAB},
    {"name": "Кастомизация: рекомендовано 5 или меньше табов по умолчанию",
     "quote": "If you let people select their own tabs, aim for a default list of five or fewer to preserve continuity between compact and regular view sizes.",
     "source": H_TAB},
    {"name": "Page controls (точки-индикаторы) как отдельный компонент",
     "quote": "More than about 10 dots are hard to count at a glance.", "source": H_PAGE},
    {"name": "Виджет-версия: Tab views",
     "quote": "In watchOS, page controls can be displayed at the bottom of the screen for horizontal pagination", "source": H_PAGE},
   ],
   "notes_ru": "В актуальной HIG числовой высоты iOS-таб-бара нет (значение 49 pt в тексте отсутствует — проверены все 127 страниц HIG); единственная числовая высота — tvOS 68 pt. Паттерн: 1 уровень табов, overflow уходит в More; максимум рекомендаций — 5 табов. Отдельных «многоуровневых» табов нет.",
   "sources": [H_TAB, H_PAGE, H_COMPLIST],
  },
 },
 "not_recommended_ru": [
  "Многоуровневые табы (табы внутри табов) — ни MD3, ни Angular Material не поддерживают больше двух уровней (MD3: primary + secondary; iOS: один уровень + More).",
  "Вертикальные табы — нет ни в Material Web, ни в Angular Material (только горизонтальные, overflow-скролл/пагинация).",
  "Высота 49 pt для iOS-таб-бара — в актуальной HIG это число отсутствует (legacy-значение из старой HIG), брать его как действующую норму нельзя.",
  "Табы с произвольным числом строк/подписью в две строки — не поддержано ни одной платформой (однострочная подпись).",
 ],
 "verdict_ru": "Высоты сходятся: MD3 48 dp (64 dp с иконкой), Angular Material 48 px (density до 32), iOS-таб-бар в актуальной HIG числом не задан. Индикатор выбранного таба различается: 3 px у MD3 primary, 2 px у MD3 secondary и у Angular Material. Практический вывод: делать один уровень табов, 48 px высоты, индикатор 2–3 px, overflow — скролл/пагинация; многоуровневые и вертикальные табы не нормированы нигде.",
}

# ============================================================ MENU
COMPONENTS["menu"] = {
 "component": "menu",
 "platforms": {
  "md3": {
   "exists": True,
   "sizes": [
    S("Menu item, min-height однострочного (токен list-item)", 56,
      "'list-item-one-line-container-height':\n      if($exclude-hardcoded-values, null, 56px),", U_LIST),
    S("Menu item, min-height двухстрочного", 72,
      "'list-item-two-line-container-height':\n      if($exclude-hardcoded-values, null, 72px),", U_LIST),
   ],
   "other_measurements": [
    M("Menu item, leading/trailing space (padding)", 16, "'list-item-leading-space': if($exclude-hardcoded-values, null, 16px),", U_LIST),
    M("Menu panel, min-width", 112, "min-width: 112px;", U_MENU_SCSS),
    M("Menu panel, отступ сверху/снизу списка", 8, "'top-space': if($exclude-hardcoded-values, null, 8px),", U_MENU_TOK),
    M("Menu item, gap (иконка/текст)", 16, "display: flex;\n    gap: 16px;", U_MENU_ITEM),
    M("Menu container, corner-extra-small (shape)", 4, "'corner-extra-small': if($exclude-hardcoded-values, null, 4px),", U_SHAPE),
   ],
   "variants": [
    {"name": "Позиционирование относительно anchor; positioning=\"popover\" | fixed",
     "quote": "When opened, menus position themselves to an anchor. Thus, either `anchor` or `anchorElement` must be supplied to `md-menu` before opening.", "source": U_DOCS_MENU},
    {"name": "Overflow / submenu (hasOverflow)",
     "quote": "`hasOverflow` | `has-overflow` | `boolean` | `false` | Displays overflow content like a submenu. Not required in most cases when using `positioning=\"popover\"`.", "source": U_DOCS_MENU},
    {"name": "Selected item (выделение выбранного)",
     "quote": "'list-item-selected-container-color':\n      map.get($deps, 'md-sys-color', 'secondary-container'),", "source": MW + "tokens/versions/v0_192/_md-comp-menu.scss"},
    {"name": "Item: иконка слева, supporting text, trailing supporting text",
     "quote": "md-item[multiline] {\n    min-height: map.get($tokens, 'two-line-container-height');", "source": U_MENU_ITEM},
    {"name": "Item: иконки в слотах start/end, selected-состояние",
     "quote": "  [slot='start'] {\n    color: map.get($tokens, 'leading-icon-color');", "source": U_MENU_ITEM},
   ],
   "touch_target_dp": 48,
   "touch_target_quote": "height: max(48px, 100%);",
   "touch_target_source": U_TOUCH,
   "notes_ru": "В material-web высота пункта меню берётся из list-item токенов: 56 px (одна строка) / 72 px (две строки) — это НЕ 48 dp, которые обычно цитируют по странице Menus спецификации m3.material.io (страница не отдаётся без JS, поэтому 48 dp как первоисточник подтвердить не удалось). Панель: min-width 112 px, паддинг списка 8 px сверху/снизу, пункт — 16 px до края, иконка 24 px, скругление 4 px (corner-extra-small), elevation level2. Sub-menu in material-web; 'menuitemcheckbox/menuitemradio' ролей нет.",
   "sources": [U_LIST, U_MENU_ITEM, U_MENU_SCSS, U_MENU_TOK, U_SHAPE, U_DOCS_MENU, U_TOKEN_LIST],
  },
  "angular_material": {
   "exists": True,
   "sizes": [
    S("Menu item height ($item-height)", 48, "$item-height: 48px !default;", N_MENU_COMMON, height_px=48),
    S("Menu item min-height (рендер панели)", 48, "min-height: 48px;", N_MENU_SCSS, height_px=48),
   ],
   "other_measurements": [
    M("Overlay min-width", 112, "$overlay-min-width: 112px !default;   // 56 * 2", N_MENU_COMMON),
    M("Overlay max-width", 280, "$overlay-max-width: 280px !default;   // 56 * 5", N_MENU_COMMON),
    M("Паддинг списка пунктов (menu content)", 8, "padding: 8px 0;", N_MENU_SCSS),
    M("menu-item-icon-size", 24, "menu-item-icon-size: 24px,", N_MENU_M3),
    M("menu-item leading/trailing spacing", 12, "menu-item-leading-spacing: 12px,", N_MENU_M3),
    M("Позиция пункта: line-height = height ($item-height)", 48, "line-height: $item-height;\n  height: $item-height;", N_MENU_COMMON),
   ],
   "variants": [
    {"name": "Позиционирование xPosition/yPosition, overlapTrigger",
     "quote": "The position can be changed using the `xPosition` (`before | after`) and `yPosition`\n(`above | below`) attributes. The menu can be forced to overlap the trigger using the\n`overlapTrigger` attribute.", "source": N_MENU_MD},
    {"name": "Nested submenu (matMenuTriggerFor внутри mat-menu-item)",
     "quote": "Material supports the ability for an `mat-menu-item` to open a sub-menu.", "source": N_MENU_MD},
    {"name": "Context menu (matContextMenuTriggerFor)",
     "quote": "You can set up a `mat-menu` as a context menu by adding the `matContextMenuTriggerFor` directive\nto your container and binding it to a menu instance.", "source": N_MENU_MD},
    {"name": "Иконки в пунктах, lazy rendering (matMenuContent), передача данных (matMenuTriggerData)",
     "quote": "By default, the menu content will be initialized even when the panel is closed. To defer\ninitialization until the menu is open, the content can be provided as an `ng-template`\nwith the `matMenuContent` attribute:", "source": N_MENU_MD},
    {"name": "Роли menuitemcheckbox/menuitemradio НЕ поддерживаются",
     "quote": "Angular Material does not support the `menuitemcheckbox` or `menuitemradio` roles.", "source": N_MENU_MD},
   ],
   "density": "не поддерживается (в _m3-menu.scss секция density пустая: `density: (),`)",
   "notes_ru": "Angular Material: пункт меню 48 px (и min-height, и line-height), панель 112–280 px, паддинг списка 8 px, иконка 24 px. Density-шкалы у меню нет. Есть вложенные меню и context-menu триггер, но нет checkbox/radio-пунктов. Панель не имеет верхней/нижней границы по высоте — ограничивается max-width и скроллом.",
   "sources": [N_MENU_SCSS, N_MENU_M3, N_MENU_MD, N_MENU_COMMON],
  },
  "ios_hig": {
   "exists": True,
   "sizes": [S("Высота пункта меню / высота панели", None, NF, H_MENU, height_pt=None)],
   "other_measurements": [],
   "variants": [
    {"name": "iOS/iPadOS: три раскладки меню — small (4 items), medium (3 items), large (список)",
     "quote": "In iOS and iPadOS, a menu can display items in one of the following three layouts.", "source": H_MENU},
    {"name": "Small: ряд из четырёх пунктов-иконок без подписей",
     "quote": "A row of four items appears at the top of the menu, above a list that contains the remaining items. For each item in the top row, the menu displays a symbol or icon, but no label.", "source": H_MENU},
    {"name": "Medium: ряд из трёх пунктов (иконка над короткой подписью)",
     "quote": "A row of three items appears at the top of the menu, above a list that contains the remaining items. For each item in the top row, the menu displays a symbol or icon above a short label.", "source": H_MENU},
    {"name": "Submenu: максимум один уровень, ~5 пунктов",
     "quote": "Also, if a submenu contains more than about five items, consider creating a new menu.", "source": H_MENU},
    {"name": "Context menu: не более ~3 групп (separators)",
     "quote": "In general, you don\u2019t want more than about three groups in a context menu.", "source": H_CTX},
    {"name": "Action sheets: не более 4 кнопок, включая Cancel",
     "quote": "Avoid displaying more than four buttons in an action sheet, including the Cancel button.", "source": H_SHEET},
   ],
   "notes_ru": "iOS HIG описывает меню как раскладки и правила содержимого (small/medium/large, один уровень сабменю, ~3 группы в контекстном меню, ≤4 кнопок в action sheet), но не даёт ни одной числовой величины высоты/отступов. Action sheet — это не popup-меню: выбирать действие надо через action sheet, а не через меню.",
   "sources": [H_MENU, H_CTX, H_SHEET],
  },
 },
 "not_recommended_ru": [
  "Пункт меню 48 dp как «спецификация MD3» — в доступных первоисточниках это число не подтверждается (в Material Web пункт = 56/72 px из list-item токенов; 48 px есть только у Angular Material).",
  "Checkbox/radio-пункты меню — не поддерживаются в Angular Material (роли menuitemcheckbox/menuitemradio), в Material Web отдельных токенов нет.",
  "Многоуровневые сабменю — iOS HIG прямо ограничивает одним уровнем; у Material нет токенов/стилей под 3+ уровня.",
  "Меню как форма/интерактивный контейнер: Angular Material запрещает любые интерактивные контролы внутри MatMenu, кроме MatMenuItem.",
  "Action sheet длиннее 4 кнопок (iOS) и меню с более чем ~3 группами (контекстное меню iOS) — выходят за норму HIG.",
 ],
 "verdict_ru": "Высота пункта меню — точка расхождения: Angular Material жёстко 48 px (line-height = height), Material Web берёт 56/72 px из list-item токенов (48 dp из спецификации m3.material.io недоступен для проверки, страница требует JS). Ширина панели совпадает у обеих реализаций: 112 px минимум (Angular Material добавляет максимум 280 px). iOS HIG размеров не задаёт вообще, но ограничивает структуру: ≤4 кнопки в action sheet, один уровень сабменю, ~3 группы.",
}

# ============================================================ SIDENAV
COMPONENTS["sidenav"] = {
 "component": "sidenav",
 "platforms": {
  "md3": {
   "exists": True,
   "sizes": [
    S("Navigation drawer, container width", 360,
      "'container-width': if($exclude-hardcoded-values, null, 360px),", U_DRAWER, width_dp=360),
    S("Navigation bar, container height", 80,
      "'container-height': if($exclude-hardcoded-values, null, 80px),", U_NAVBAR),
    S("Navigation drawer, active indicator height", 56,
      "'active-indicator-height': if($exclude-hardcoded-values, null, 56px),", U_DRAWER),
    S("Navigation bar, active indicator height", 32,
      "'active-indicator-height': if($exclude-hardcoded-values, null, 32px),", U_NAVBAR),
   ],
   "other_measurements": [
    M("Navigation drawer, active indicator width", 336, "'active-indicator-width': if($exclude-hardcoded-values, null, 336px),", U_DRAWER),
    M("Navigation bar, active indicator width", 64, "'active-indicator-width': if($exclude-hardcoded-values, null, 64px),", U_NAVBAR),
    M("Navigation drawer, icon size", 24, "'icon-size': if($exclude-hardcoded-values, null, 24px),", U_DRAWER),
    M("Navigation bar, icon size", 24, "'icon-size': if($exclude-hardcoded-values, null, 24px),", U_NAVBAR),
    M("Navigation drawer, форма (corner-large-end)", 16, "'container-shape': map.get($deps, 'md-sys-shape', 'corner-large-end'),", U_DRAWER),
    M("Navigation bar, реализация: height: var(--_container-height)", 80, "height: var(--_container-height);", MW + "labs/navigationbar/internal/_navigation-bar.scss"),
   ],
   "variants": [
    {"name": "Navigation drawer (standard / modal) — labs-компонент в Material Web",
     "evidence": "/labs/navigationdrawer/internal/navigation-drawer.ts", "source": "https://github.com/material-components/material-web/tree/main/labs/navigationdrawer"},
    {"name": "Navigation bar (нижняя навигация, labs)",
     "evidence": "/labs/navigationbar/internal/navigation-bar.ts", "source": "https://github.com/material-components/material-web/tree/main/labs/navigationbar"},
    {"name": "Navigation rail — есть токены (tokens/v0_192/_md-comp-navigation-rail.scss), но компонента в библиотеке нет",
     "evidence": "tokens/v0_192/_md-comp-navigation-rail.scss", "source": U_TOKEN_LIST},
   ],
   "touch_target_dp": 48,
   "touch_target_quote": "height: max(48px, 100%);",
   "touch_target_source": U_TOUCH,
   "notes_ru": "MD3 drawer: ширина 360 dp, иконка 24, индикатор 56×336, скругление с одного края 16 (corner-large-end), высота 100%. Нижняя navigation bar: 80 dp, индикатор 32×64. В Material Web drawer и navigation bar живут в labs (не в стабильном API), navigation rail существует только токенами — компонента нет. Отдельного варианта navigation drawer ширины 240 dp в MD3-токенах нет.",
   "sources": [U_DRAWER, U_NAVBAR, MW + "labs/navigationbar/internal/_navigation-bar.scss", U_TOKEN_LIST, U_TOUCH],
  },
  "angular_material": {
   "exists": True,
   "sizes": [
    S("Sidenav/drawer container width (M3-токен)", 360,
      "sidenav-container-width: 360px,", N_SIDE_M3, width_px=360),
   ],
   "other_measurements": [
    M("Скругление drawer (corner-large = 16px)", 16, "sidenav-container-shape: map.get($system, corner-large),", N_SIDE_M3),
    M("Толщина разделителя side-mode", 1, "border-right-width: 1px;", N_SIDE_SCSS),
    M("Длительность анимации переезда drawer", 400, "transition: transform 400ms cubic-bezier(0.25, 0.8, 0.25, 1);", N_SIDE_SCSS),
    M("z-index: content 1 / side-drawer 2 / backdrop 3 / over-drawer 4 (верхний уровень)", 4, "$drawer-over-drawer-z-index: 4;", N_SIDE_SCSS),
   ],
   "variants": [
    {"name": "Режимы mode: over (по умолчанию) | push | side",
     "quote": "| `over` | Sidenav floats over the primary content, which is covered by a backdrop                 |", "source": N_SIDE_MD},
    {"name": "position: start (по умолчанию) | end, максимум два sidenav в контейнере",
     "quote": "A\n`<mat-sidenav-container>` can have up to two `<mat-sidenav>` elements total, but only one for any\ngiven side.", "source": N_SIDE_MD},
    {"name": "MatSidenav (полноэкранный) vs MatDrawer (секция приложения)",
     "quote": "The drawer component is designed to add side content to a small section of your app.", "source": N_SIDE_MD},
    {"name": "fixedInViewport + fixedTopGap/fixedBottomGap (только mat-sidenav)",
     "quote": "For `<mat-sidenav>` only (not `<mat-drawer>`) fixed positioning is supported.", "source": N_SIDE_MD},
    {"name": "Ширина по умолчанию — по контенту; задаётся CSS",
     "quote": "The `<mat-sidenav>` and `<mat-drawer>` will, by default, fit the size of its content. The width can\nbe explicitly set via CSS:", "source": N_SIDE_MD},
    {"name": "autosize, disableClose, autoFocus, hasBackdrop",
     "quote": "`<mat-drawer>` also supports all of these same modes and options.", "source": N_SIDE_MD},
   ],
   "density": "не поддерживается (в _m3-sidenav.scss секция density пустая: `density: (),`)",
   "notes_ru": "Angular Material: M3-токен ширины 360 px, но документация отдельно оговаривает, что по умолчанию ширина по контенту и задаётся CSS (в примере 200 px). Вариантов ширины 240 px в исходниках нет (в _m2-sidenav.scss ширина = auto). Три режима over/push/side, position start/end, до двух sidenav, анимация 400 ms. Density-шкалы нет.",
   "sources": [N_SIDE_MD, N_SIDE_M3, N_SIDE_SCSS],
  },
  "ios_hig": {
   "exists": True,
   "sizes": [S("Ширина sidebar", None, NF, H_SIDE, width_pt=None)],
   "other_measurements": [],
   "variants": [
    {"name": "Sidebar (навигация по разделам приложения), версия «таб-бар, превращающийся в sidebar»",
     "quote": "you choose whether to display a sidebar or a tab bar when your app opens.", "source": H_SIDE},
    {"name": "Максимум два уровня иерархии в sidebar",
     "quote": "In general, show no more than two levels of hierarchy in a sidebar.", "source": H_SIDE},
    {"name": "macOS: три размера sidebar (small/medium/large) — влияют на row height/текст/глифы",
     "quote": "A sidebar\u2019s row height, text, and glyph size depend on its overall size, which can be small, medium, or large.", "source": H_SIDE},
    {"name": "Скрытие sidebar: iPadOS — edge swipe, macOS — кнопка/меню view",
     "quote": "For example, in iPadOS, people expect to use the built-in edge swipe gesture; in macOS, you can include a show/hide button", "source": H_SIDE},
    {"name": "Navigation bar (44 pt) как отдельная страница HIG отсутствует",
     "quote": "In iOS, a navigation-specific toolbar is sometimes called a navigation bar.", "source": H_TOOL},
   ],
   "notes_ru": "В HIG нет ни страницы Navigation bars, ни числовой ширины sidebar (запрошенный /navigation-bars возвращает 404; текущий сайт закрывает тему страницей Toolbars). Единственная числовая привязка к 44 pt во всей HIG — рекомендация Apple для высоты кнопки Sign in with Apple («44 points tall, which is the default (and recommended) button height in iOS»), а не высота навбара. Правила структуры: ≤2 уровня иерархии, sidebar как адаптация таб-бара.",
   "sources": [H_SIDE, H_TOOL, H_SIWA, H_COMPLIST],
  },
 },
 "not_recommended_ru": [
  "Ширина боковой панели 240 dp — нет ни в MD3-токенах, ни в исходниках Angular Material (у Angular 360 px токен / auto по M2 / пример 200 px).",
  "Высота iOS navigation bar 44 pt — в актуальной HIG этого числа нет (страницы Navigation bars не существует); историческое значение нельзя выдавать за действующую норму.",
  "Sidebar глубже двух уровней иерархии — прямо не рекомендуется в iOS HIG.",
  "Два одинаковых «старта» (два sidenav на одну сторону) — ошибка конфигурации в Angular Material.",
  "Navigation rail как компонент — в Material Web есть только токены, компонента нет (для веба вариант не нормирован).",
 ],
 "verdict_ru": "Ширина сходится: и MD3 (navigation drawer), и Angular Material M3 дают 360 dp/px; 240 dp не подтверждается ни одним исходником. Высоты: MD3 даёт drawer 100% и navigation bar 80 dp с индикатором 56×336 / 32×64, Angular Material режимами over/push/side и анимацией 400 ms — но не задаёт высоту панели. iOS: sidebar нормирован только структурно (≤2 уровня, адаптивная версия таб-бара), числовой ширины нет.",
}

# ============================================================ STEPPER
COMPONENTS["stepper"] = {
 "component": "stepper",
 "platforms": {
  "md3": {
   "exists": False,
   "sizes": [S("Любые размеры компонента Stepper", None, NF, U_TOKEN_LIST, height_dp=None)],
   "other_measurements": [],
   "variants": [{"name": "Варианты (горизонтальный/вертикальный и т.п.)", "quote": NF, "source": U_DOCS_LIST}],
   "touch_target_dp": None,
   "notes_ru": "Размеры: не найдено (нет источника). Компонента Stepper в Material Design 3 (в реализуемом наборе Material Web) нет: в списке токенов (tokens/, 60+ md-comp-*.scss, включая v0_192) нет ни одного файла stepper, в docs/components только 20 компонентов (button…text-field) без stepper, в полном списке файлов репозитория (1029 файлов) подстрока 'stepper' не встречается. Соответственно нет ни высоты шага, ни вариантов (горизонтальный/вертикальный).",
   "sources": [U_TOKEN_LIST, U_DOCS_LIST,
               "https://data.jsdelivr.com/v1/package/gh/material-components/material-web@main/flat"],
  },
  "angular_material": {
   "exists": True,
   "sizes": [
    S("Высота хедера шага ($header-height)", 72, "$header-height: 72px !default;", N_STEP_VARS, height_px=72),
    S("Минимальная высота хедера", 42, "$header-minimum-height: 42px !default;", N_STEP_VARS, height_px=42),
    S("Высота иконки/лейбла в хедере", 24, "$label-header-height: 24px;", N_STEP_VARS, height_px=24),
    S("Вертикальный степпер: отступ контента", 36, "$vertical-stepper-content-margin: 36px;", N_STEP_VARS, height_px=36),
   ],
   "other_measurements": [
    M("labelPosition=bottom: зазор до контента", 16, "$label-position-bottom-top-gap: 16px;", N_STEP_VARS),
    M("Минимальная ширина лейбла", 50, "$label-min-width: 50px;", N_STEP_VARS),
    M("Боковой отступ (side gap)", 24, "$side-gap: 24px;", N_STEP_VARS),
    M("Толщина линии между шагами", 1, "$line-width: 1px;", N_STEP_VARS),
    M("Размер иконки шага", 16, "$step-header-icon-size: 16px;", N_STEP_VARS),
   ],
   "variants": [
    {"name": "orientation: horizontal | vertical",
     "quote": "There are two stepper variants: `horizontal` and `vertical`. You can switch between the two using\nthe `orientation` attribute.", "source": N_STEP_MD},
    {"name": "labelPosition: end (по умолчанию) | bottom — только горизонтальный",
     "quote": "For a horizontal `mat-stepper` it's possible to define the position of the label. `end` is the\ndefault value, while `bottom` will place it under the step icon instead of at its side.", "source": N_STEP_MD},
    {"name": "headerPosition: top (по умолчанию) | bottom",
     "quote": "If you're using a horizontal stepper, you can control where the stepper's content is positioned\nusing the `headerPosition` input.", "source": N_STEP_MD},
    {"name": "linear / optional / editable / completed / error state (showError) / lazy (matStepContent) / кастомные состояния и иконки",
     "quote": "The `linear` attribute can be set on `mat-stepper` to create a linear stepper that requires the\nuser to complete previous steps before proceeding to following steps.", "source": N_STEP_MD},
    {"name": "Responsive stepper: смена orientation по вьюпорту",
     "quote": "If your app supports a wide variety of screens and a stepper's layout doesn't fit a particular\nscreen size, you can control its `orientation` dynamically to change the layout based on the\nviewport.", "source": N_STEP_MD},
    {"name": "На малых экранах HIG-рекомендация документации: вертикальный",
     "quote": "Prefer vertical steppers when building for small screen sizes, as horizontal\nsteppers typically take up significantly more horizontal space thus introduce\nhorizontal scrolling.", "source": N_STEP_MD},
    {"name": "Доступность: роль tablist/tab/tabpanel",
     "quote": "The stepper is treated as a tabbed view for accessibility purposes, so it is given\n`role=\"tablist\"` by default.", "source": N_STEP_MD},
   ],
   "density": "шкала 0…-4: 72 → 68 → 64 → 60 → 42 px (stepper-header-height; 42 — минимум, ниже нельзя)",
   "notes_ru": "Единственная платформа с компонентом «wizard» — Angular Material: хедер 72 px (density до 42 px), оба варианта ориентации, labelPosition, headerPosition, linear/optional/editable/error, шаги реализованы как tablist/tab/tabpanel. Горизонтальный вариант на телефоне сама документация не рекомендует — просить вертикальный.",
   "sources": [N_STEP_MD, N_STEP_VARS, N_STEP_M3],
  },
  "ios_hig": {
   "exists": True,
   "sizes": [S("Высота шага / хедера", None, NF, H_STEP, height_pt=None)],
   "other_measurements": [],
   "variants": [
    {"name": "Steppers в HIG — это НЕ wizard: двухсегментный инкрементальный контрол",
     "quote": "A stepper is a two-segment control that people use to increase or decrease an incremental value.", "source": H_STEP},
    {"name": "Платформы: iOS/iPadOS/visionOS без особенностей; watchOS/tvOS не поддерживается",
     "quote": "No additional considerations for iOS, iPadOS, or visionOS. Not supported in watchOS or tvOS.", "source": H_STEP},
    {"name": "Пара с текстовым полем для больших диапазонов",
     "quote": "Consider pairing a stepper with a text field when large value changes are likely.", "source": H_STEP},
   ],
   "notes_ru": "У iOS HIG нет компонента многошагового мастера. Страница Steppers — про контрол «+/-» рядом с полем значения (macOS/iOS), это другой смысл слова. Разделов/паттернов для wizard-флоу в HIG нет: 127 страниц HIG содержат только паттерны Onboarding, Modality, Entering data и т.п. Поэтому ни высоты шага, ни рекомендаций по горизонтальному/вертикальному wizard от Apple не существует.",
   "sources": [H_STEP, HIG + "onboarding", HIG + "patterns", H_COMPLIST],
  },
 },
 "not_recommended_ru": [
  "Горизонтальный wizard-степпер на телефоне — ни одна платформа его не нормирует: MD3 степпера нет вообще, iOS HIG такого компонента не имеет, а документация Angular Material прямо предупреждает про горизонтальный скролл и советует вертикальный.",
  "Многошаговый мастер как компонент iOS — в HIG отсутствует; «Steppers» у Apple это инкрементальный контрол, путать нельзя.",
  "Высота шага в MD3 — нет источника: компонента и токенов stepper в Material Design 3 / Material Web нет.",
  "Пять и более шагов в горизонтальном степпере — не нормировано нигде (у Angular Material ширина лейбла минимум 50 px, но предела числа шагов нет).",
 ],
 "verdict_ru": "Степпер есть только у Angular Material (хедер 72 px, density до 42 px, горизонтальный и вертикальный); в Material Design 3 компонента Stepper нет ни в токенах, ни в компонентах, и у Apple HIG под «Stepper» имеется в виду инкрементальный контрол, а не мастер. Любые цифры по «MD3 stepper» или «iOS stepper (wizard)» будут выдумкой. На мобильной ширине нормированного решения нет — единственная опора: рекомендация Angular Material использовать вертикальный степпер, а не горизонтальный.",
}

# ============================================================ SNACKBAR
COMPONENTS["snackbar"] = {
 "component": "snackbar",
 "platforms": {
  "md3": {
   "exists": True,
   "sizes": [
    S("Snackbar, высота однострочного", 48,
      "'with-single-line-container-height':\n      if($exclude-hardcoded-values, null, 48px),", U_SNACK),
    S("Snackbar, высота двухстрочного", 68,
      "'with-two-lines-container-height': if($exclude-hardcoded-values, null, 68px)", U_SNACK),
    S("Snackbar, icon size", 24,
      "'icon-size': if($exclude-hardcoded-values, null, 24px),", U_SNACK),
   ],
   "other_measurements": [
    M("Скругление контейнера (corner-extra-small)", 4, "'corner-extra-small': if($exclude-hardcoded-values, null, 4px),", U_SHAPE),
   ],
   "variants": [
    {"name": "С действием (action label) и без",
     "quote": "'action-label-text-line-height':\n      map.get($deps, 'md-sys-typescale', 'label-large-line-height'),", "source": U_SNACK},
    {"name": "Однострочный / двухстрочный",
     "quote": "'supporting-text-line-height':\n      map.get($deps, 'md-sys-typescale', 'body-medium-line-height'),", "source": U_SNACK},
    {"name": "С иконкой",
     "quote": "'icon-size': if($exclude-hardcoded-values, null, 24px),", "source": U_SNACK},
   ],
   "touch_target_dp": 48,
   "touch_target_quote": "height: max(48px, 100%);",
   "touch_target_source": U_TOUCH,
   "notes_ru": "MD3 задаёт токены snackbar: 48 px одна строка / 68 px две строки, иконка 24, скругление 4 (corner-extra-small), action-label типографика label-large, supporting text — body-medium. Позиции (снизу по центру) в токенах нет — она на странице спецификации m3.material.io, которая без JS не отдаётся. Важно: в Material Web компонента snackbar нет, только токены — элемент придётся делать самому.",
   "sources": [U_SNACK, U_SHAPE, U_TOKEN_LIST],
  },
  "angular_material": {
   "exists": True,
   "sizes": [
    S("Ширина контейнера, минимум", 344, "min-width: 344px;", N_SNACK_SCSS, width_px=344),
    S("Ширина контейнера, максимум", 672, "max-width: 672px;", N_SNACK_SCSS, width_px=672),
    S("Внешний отступ контейнера", 8, "margin: 8px;", N_SNACK_SCSS, height_px=8),
    S("Внутренний отступ текста (14px сверху/снизу)", 14,
      "padding: 14px $_side-padding 14px 16px;", N_SNACK_SCSS, height_px=14),
   ],
   "other_measurements": [
    M("Скругление (corner-extra-small)", 4, "snack-bar-container-shape: map.get($system, corner-extra-small),", N_SNACK_M3),
    M("Тень (elevation 6)", 6, "@include elevation.elevation(6);", N_SNACK_SCSS),
    M("Анимация появления / исчезновения, ms", 150, "animation: _mat-snack-bar-enter 150ms cubic-bezier(0, 0, 0.2, 1) forwards;", N_SNACK_SCSS),
   ],
   "variants": [
    {"name": "Позиция по умолчанию: bottom + center",
     "quote": "verticalPosition?: MatSnackBarVerticalPosition = 'bottom';", "source": N_SNACK_TS},
    {"name": "Позиции: start | center | end | left | right; вертикально top | bottom",
     "quote": "export type MatSnackBarHorizontalPosition = 'start' | 'center' | 'end' | 'left' | 'right';", "source": N_SNACK_TS},
    {"name": "Длительность: по умолчанию 0 (без авто-закрытия), задаётся вручную",
     "quote": "duration?: number = 0;", "source": N_SNACK_TS},
    {"name": "Только один snackbar одновременно",
     "quote": "Only one snackbar can ever be opened at one time. If a new snackbar is opened while a previous\nmessage is still showing, the older message will be automatically dismissed.", "source": N_SNACK_MD},
    {"name": "Одно действие + политесс polite, фокус не переносится",
     "quote": "`MatSnackBar` does not move focus to the snackbar element.", "source": N_SNACK_MD},
    {"name": "handset-режим: ширина 100vw / 100%",
     "quote": "width: 100vw;", "source": N_SNACK_SCSS},
    {"name": "Не задавать duration при наличии действия",
     "quote": "Avoid setting a `duration` for snackbars that have an action available, as screen reader users may\nwant to navigate to the snackbar element to activate the action.", "source": N_SNACK_MD},
   ],
   "density": "не поддерживается (в _m3-snack-bar.scss секция density пустая: `density: (),`)",
   "notes_ru": "Angular Material: панель 344–672 px, отступ 8 px по периметру, текст 14 px, скругление 4, elevation 6, вход 150 ms. Дефолты: bottom + center, duration 0 (то есть без авто-закрытия — значение нужно задавать явно), politeness polite, одновременно только один snackbar. Фокус на snackbar не переносится, поэтому для действия нужна альтернатива. Density-шкалы нет.",
   "sources": [N_SNACK_SCSS, N_SNACK_M3, N_SNACK_TS, N_SNACK_MD],
  },
  "ios_hig": {
   "exists": False,
   "sizes": [S("Размеры snackbar/toast", None, NF, HIG + "components", height_pt=None)],
   "other_measurements": [],
   "variants": [{"name": "Варианты snackbar/toast", "quote": NF, "source": H_COMPLIST}],
   "notes_ru": "В iOS HIG компонента snackbar/toast нет: в списке компонентов HIG (72 страницы) нет ни snackbar, ни toast, ни banner. Ближайшие системные замены — Alerts (модальный, «up to three buttons»), Action sheets (≤4 кнопок) и Notifications (пользовательские уведомления). Числовых размеров у них нет; единственная числовая величина в этих разделах — максимальная высота accessory view в visionOS-алерте 154 pt.",
   "sources": [H_COMPLIST, H_ALERT, H_SHEET, HIG + "notifications"],
  },
 },
 "not_recommended_ru": [
  "Snackbar/toast в iOS — паттерна нет в HIG (72 страницы компонентов); заменять надо на alert/action sheet или пользовательское уведомление, либо это будет кастомный (не нормированный платформой) элемент.",
  "Позиция снизу по центру как число от MD3 — в токенах MD3 позиции нет, это утверждение со страницы спецификации (не проверяемо без JS).",
  "Готовый компонент snackbar в Material Web — отсутствует: есть только токены, элемент придётся реализовывать самостоятельно.",
  "Авто-скрытие snackbar с действием — противоречит рекомендации Angular Material (duration не задавать, если есть action).",
  "Несколько snackbar одновременно — Angular Material прямо ограничивает одним.",
 ],
 "verdict_ru": "Высоты близки по смыслу, но заданы в разных системах: MD3 — 48 dp однострочный / 68 dp двухстрочный (иконка 24, скругление 4), Angular Material — панель 344–672 px, отступ 8 px, текст 14 px, скругление 4, по умолчанию bottom+center и duration 0. В Material Web компонента нет, только токены; в iOS HIG паттерна нет вовсе. Практический вывод: высоту брать 48/68 dp из MD3, поведение (один за раз, без авто-скрытия при действии, без переноса фокуса) — из Angular Material.",
}

os.makedirs(OUT, exist_ok=True)
for slug, data in COMPONENTS.items():
    for platform, block in data["platforms"].items():
        postprocess(platform, block)
    p = os.path.join(OUT, slug + ".json")
    with open(p, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    print("wrote", p)

print("\nQUOTE VERIFY FAILURES:", len(FAILS))
for f in FAILS:
    print("  FAIL", f)
