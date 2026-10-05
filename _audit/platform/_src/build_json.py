import json, os

OUT = os.path.expanduser("~/GitHub/iiko-DS/DS/_audit/platform")
os.makedirs(OUT, exist_ok=True)

MW = "https://raw.githubusercontent.com/material-components/material-web/main/"
AM = "https://raw.githubusercontent.com/angular/components/main/"
HIG = "https://developer.apple.com/design/human-interface-guidelines/"
HIGJ = "https://developer.apple.com/tutorials/data/design/human-interface-guidelines/"
APL = "https://developer.apple.com/documentation/"

MW_LIST_TOK = MW + "tokens/versions/v0_192/_md-comp-list.scss"
MW_LIST_ITEM_TOK = MW + "tokens/_md-comp-list-item.scss"
MW_LIST_DOC = MW + "docs/components/list.md"
MW_LIST_INTERNAL = MW + "list/internal/_list.scss"
MW_DT_TOK = MW + "tokens/versions/v0_192/_md-comp-data-table.scss"
MW_CARD_TOK = MW + "tokens/versions/v0_192/_md-comp-elevated-card.scss"
MW_CARD_FILLED = MW + "tokens/versions/v0_192/_md-comp-filled-card.scss"
MW_CARD_OUTLINED = MW + "tokens/versions/v0_192/_md-comp-outlined-card.scss"
MW_SHAPE_TOK = MW + "tokens/versions/v0_192/_md-sys-shape.scss"
MW_STATE_TOK = MW + "tokens/versions/v0_192/_md-sys-state.scss"
MW_TYPES_TOK = MW + "tokens/versions/v0_192/_md-sys-typescale.scss"
MW_ALL = MW + "all.ts"
M3_LISTS = "https://m3.material.io/components/lists/specs"
M3_CARDS = "https://m3.material.io/components/cards/specs"

AM_LIST_MD = AM + "src/material/list/list.md"
AM_LIST_M3 = AM + "src/material/list/_m3-list.scss"
AM_LIST_SCSS = AM + "src/material/list/list.scss"
AM_CARD_MD = AM + "src/material/card/card.md"
AM_CARD_M3 = AM + "src/material/card/_m3-card.scss"
AM_CARD_SCSS = AM + "src/material/card/card.scss"
AM_EXP_MD = AM + "src/material/expansion/expansion.md"
AM_EXP_M3 = AM + "src/material/expansion/_m3-expansion.scss"
AM_EXP_VARS = AM + "src/material/expansion/_expansion-variables.scss"
AM_EXP_HDR = AM + "src/material/expansion/expansion-panel-header.scss"
AM_TBL_MD = AM + "src/material/table/table.md"
AM_TBL_M3 = AM + "src/material/table/_m3-table.scss"
AM_TBL_SCSS = AM + "src/material/table/table.scss"
AM_TBL_FLEX = AM + "src/material/table/_table-flex-styles.scss"
AM_TREE_MD = AM + "src/material/tree/tree.md"
AM_TREE_M3 = AM + "src/material/tree/_m3-tree.scss"
AM_TREE_SCSS = AM + "src/material/tree/tree.scss"
AM_CDK_INDENT = AM + "src/cdk/tree/padding.ts"
AM_BTN_M3 = AM + "src/material/button/_m3-button.scss"

HIG_LT = HIG + "lists-and-tables"
HIG_ACC = HIG + "accessibility"
HIG_BTN = HIG + "buttons"
HIG_DIS = HIG + "disclosure-controls"
HIG_OUT = HIG + "outline-views"
HIG_COLL = HIG + "collections"
APL_LISTSTYLE = APL + "swiftui/liststyle"
APL_UITV_STYLE = APL + "uikit/uitableview/style-swift.enum"
APL_ROWHEIGHT = APL + "uikit/uitableview/rowheight"

VERIFIED = "2026-09-11"
NF = "не найдено"


def sz(name, quote, source, height_dp=None, value=None, unit=None):
    d = {"name": name, "quote": quote, "source": source}
    if height_dp is not None:
        d["height_dp"] = height_dp
    if value is not None:
        d["value"] = value
    if unit is not None:
        d["unit"] = unit
    return d


# =============================================================== LIST
list_core = {
    "component": "List (список)",
    "verified_at": VERIFIED,
    "platforms": {
        "md3": {
            "exists": True,
            "component_name": "Lists: md-list / md-list-item (Material Web — официальная библиотека MD3)",
            "sizes": [
                sz("Высота строки one-line", "'list-item-one-line-container-height':\n      if($exclude-hardcoded-values, null, 56px),", MW_LIST_TOK, height_dp=56),
                sz("Высота строки two-line", "'list-item-two-line-container-height':\n      if($exclude-hardcoded-values, null, 72px),", MW_LIST_TOK, height_dp=72),
                sz("Высота строки three-line", "'list-item-three-line-container-height':\n      if($exclude-hardcoded-values, null, 88px),", MW_LIST_TOK, height_dp=88),
                sz("Горизонтальный отступ строки (leading space)", "'list-item-leading-space': if($exclude-hardcoded-values, null, 16px),", MW_LIST_TOK, value=16, unit="dp"),
                sz("Горизонтальный отступ строки (trailing space)", "'list-item-trailing-space': if($exclude-hardcoded-values, null, 16px),", MW_LIST_TOK, value=16, unit="dp"),
                sz("Padding контейнера списка (верх/низ)", "padding: 8px 0;", MW_LIST_INTERNAL, value=8, unit="dp"),
                sz("Внутренние токены top-space / bottom-space строки", "'top-space': if($exclude-hardcoded-values, null, 12px),\n      'bottom-space': if($exclude-hardcoded-values, null, 12px),", MW_LIST_ITEM_TOK, value=12, unit="dp"),
                sz("Размер leading/trailing иконки", "'list-item-leading-icon-size': if($exclude-hardcoded-values, null, 24px),\n    'list-item-trailing-icon-size': if($exclude-hardcoded-values, null, 24px),", MW_LIST_TOK, value=24, unit="dp"),
                sz("Размер аватара (leading avatar)", "'list-item-leading-avatar-size': if($exclude-hardcoded-values, null, 40px),", MW_LIST_TOK, value=40, unit="dp"),
                sz("Размер изображения (leading image)", "'list-item-leading-image-height': if($exclude-hardcoded-values, null, 56px),\n    'list-item-leading-image-width': if($exclude-hardcoded-values, null, 56px),", MW_LIST_TOK, value="56x56", unit="dp"),
                sz("Ширина ведущего видео (leading video)", "'list-item-leading-video-width': if($exclude-hardcoded-values, null, 100px),", MW_LIST_TOK, value=100, unit="dp"),
                sz("Отступ divider внутри списка", "'divider-leading-space': if($exclude-hardcoded-values, null, 16px),\n    'divider-trailing-space': if($exclude-hardcoded-values, null, 16px),", MW_LIST_TOK, value=16, unit="dp"),
                sz("Основной текст строки = body-large", "'list-item-label-text-size':\n      map.get($deps, 'md-sys-typescale', 'body-large-size'),", MW_LIST_TOK, value="body-large", unit=None),
                sz("Значение body-large", "'body-large-size': if($exclude-hardcoded-values, null, 1rem),", MW_TYPES_TOK, value="1rem (16px)", unit="rem"),
                sz("Supporting text = body-medium", "'list-item-supporting-text-size':\n      map.get($deps, 'md-sys-typescale', 'body-medium-size'),", MW_LIST_TOK, value="body-medium", unit=None),
                sz("Значение body-medium", "'body-medium-size': if($exclude-hardcoded-values, null, 0.875rem),", MW_TYPES_TOK, value="0.875rem (14px)", unit="rem"),
                sz("Trailing supporting text / overline = label-small", "'list-item-trailing-supporting-text-size':\n      map.get($deps, 'md-sys-typescale', 'label-small-size'),", MW_LIST_TOK, value="label-small", unit=None),
                sz("Значение label-small", "'label-small-size': if($exclude-hardcoded-values, null, 0.6875rem),", MW_TYPES_TOK, value="0.6875rem (11px)", unit="rem"),
                sz("Touch target для строки списка", NF, None, value=NF, unit=None),
            ],
            "variants": [
                "one-line (только текст/headline)",
                "two-line (headline + supporting-text)",
                "three-line (headline + две строки supporting-text)",
                "icon item (leading 24 dp, trailing 24 dp)",
                "avatar item (40 dp, corner-full)",
                "image item (56x56 dp, corner-none)",
                "video item (leading video, ширина 100 dp; small video height 56 dp)",
                "divider между строками",
                "поведение через type: \"text\" (по умолчанию), \"button\", \"link\" (с href/target)",
            ],
            "states": [
                {"name": "hover state layer opacity", "value": 0.08,
                 "quote": "'hover-state-layer-opacity': if($exclude-hardcoded-values, null, 0.08),", "source": MW_STATE_TOK},
                {"name": "focus state layer opacity", "value": 0.12,
                 "quote": "'focus-state-layer-opacity': if($exclude-hardcoded-values, null, 0.12),", "source": MW_STATE_TOK},
                {"name": "pressed state layer opacity", "value": 0.12,
                 "quote": "'pressed-state-layer-opacity': if($exclude-hardcoded-values, null, 0.12)", "source": MW_STATE_TOK},
                {"name": "selected trailing icon color", "value": "md.sys.color.primary",
                 "quote": "'list-item-selected-trailing-icon-color':\n      map.get($deps, 'md-sys-color', 'primary'),", "source": MW_LIST_TOK},
                {"name": "disabled opacity строки", "value": None,
                 "note_ru": "Токен существует, но его значение подставляется из другого токена — числовая константа не задана",
                 "quote": "'disabled-opacity':\n        map.get($original-tokens, 'list-item-disabled-label-text-opacity'),", "source": MW_LIST_ITEM_TOK},
            ],
            "touch_target_dp": None,
            "touch_target_note_ru": "Числовой константы touch target для списка в официальных исходниках material-web нет — " + NF,
            "notes_ru": "MD3 задаёт высоты строк токенами md.comp.list.list-item.*: 56/72/88 dp, горизонтальные отступы 16 dp, контейнер списка 8 px, внутренние токены строки 12 dp. Типографика: label-text = body-large, supporting-text = body-medium, trailing-supporting-text = label-small. Это единственный компонент из набора, который есть и в спецификации MD3, и в официальной веб-библиотеке (md-list/md-list-item). Спец-страница m3.material.io/components/lists/specs существует, но рендерится клиентским JS, поэтому все числа взяты из официальных токенов и исходников material-web.",
            "sources": [M3_LISTS, MW_LIST_DOC, MW_LIST_TOK, MW_LIST_ITEM_TOK, MW_LIST_INTERNAL, MW_STATE_TOK, MW_TYPES_TOK],
        },
        "angular_material": {
            "exists": True,
            "component_name": "mat-list / mat-list-item, mat-nav-list, mat-action-list, mat-selection-list (+ mat-list-option)",
            "sizes": [
                sz("Высота строки one-line (плотность 0)", "list-list-item-one-line-container-height:\n        list.nth((48px, 44px, 40px, 36px, 32px, 24px), $index),", AM_LIST_M3, height_dp=48),
                sz("Высота строки two-line (плотность 0)", "list-list-item-two-line-container-height:\n        list.nth((64px, 60px, 56px, 52px, 48px, 48px), $index),", AM_LIST_M3, height_dp=64),
                sz("Высота строки three-line (плотность 0)", "list-list-item-three-line-container-height:\n        list.nth((88px, 84px, 80px, 76px, 72px, 56px), $index),", AM_LIST_M3, height_dp=88),
                sz("Отступы ведущей иконки (start/end space), плотность 0", "list-list-item-leading-icon-start-space: list.nth((16px, 12px, 8px, 4px, 4px, 4px), $index),\n    list-list-item-leading-icon-end-space: list.nth((16px, 12px, 8px, 4px, 4px, 4px), $index),", AM_LIST_M3, value=16, unit="px"),
                sz("Размер ведущей иконки", "// Match spec, which has list-item-leading-icon-size of 24px.\n    // Current version of tokens (0_161) has 18px.\n    list-list-item-leading-icon-size: 24px,", AM_LIST_M3, value=24, unit="px"),
                sz("Размер завершающей иконки", "list-list-item-trailing-icon-size: 24px,", AM_LIST_M3, value=24, unit="px"),
                sz("Размер аватара", "list-list-item-leading-avatar-size: 40px,", AM_LIST_M3, value=40, unit="px"),
                sz("Основной текст = body-large", "list-list-item-label-text-size: map.get($system, body-large-size),", AM_LIST_M3, value="body-large", unit=None),
                sz("Supporting text = body-medium", "list-list-item-supporting-text-size: map.get($system, body-medium-size),", AM_LIST_M3, value="body-medium", unit=None),
                sz("Trailing supporting text = label-small", "list-list-item-trailing-supporting-text-size: map.get($system, label-small-size),", AM_LIST_M3, value="label-small", unit=None),
                sz("Отступ divider рядом с аватаром", ".mat-mdc-list-item-avatar ~ .mat-divider-inset {\n    margin-left: 72px;", AM_LIST_SCSS, value=72, unit="px"),
            ],
            "variants": [
                "simple list (<mat-list-item> с текстом напрямую)",
                "multi-line list (matListItemTitle + matListItemLine; вход lines=N включает перенос текста)",
                "mat-nav-list (role=\"navigation\", только ссылки)",
                "mat-action-list (каждый элемент — <button>)",
                "mat-selection-list + mat-list-option (role=\"listbox\")",
                "подзаголовки matSubheader + <mat-divider>",
                "слоты строки: matListItemIcon, matListItemAvatar, matListItemMeta, matListItemTitle, matListItemLine",
            ],
            "density": "Есть: clamp-density($scale, -5). one-line (48, 44, 40, 36, 32, 24); two-line (64, 60, 56, 52, 48, 48); three-line (88, 84, 80, 76, 72, 56); отступы иконки (16, 12, 8, 4, 4, 4).",
            "touch_target_dp": None,
            "touch_target_note_ru": "Для mat-list токена touch target нет — " + NF + ". Общий M3-touch-target в Angular Material равен 48 px, но заведён он у кнопок: '$touch-target-size: 48px;' (" + AM_BTN_M3 + ").",
            "notes_ru": "Ключевое расхождение: в M3-теме Angular Material высоты строк 48/64/88 px (плотность 0), а в токенах MD3 — 56/72/88. Не совпадает one-line (48 против 56) и two-line (64 против 72). В комментариях исходников отмечено только расхождение по цвету контейнера и по размеру ведущей иконки ('Match spec, which has list-item-leading-icon-size of 24px. Current version of tokens (0_161) has 18px.'); про высоты комментариев нет. Отступ 72 px применяется к вложенному divider рядом с аватаром.",
            "sources": [AM_LIST_MD, AM_LIST_M3, AM_LIST_SCSS, AM_BTN_M3],
        },
        "ios_hig": {
            "exists": True,
            "component_name": "Lists and tables (HIG) / List, UITableView (API)",
            "sizes": [
                sz("Высота строки списка/таблицы", NF, None, value=NF, unit=None),
                sz("Размер контрола по умолчанию (iOS/iPadOS) — используется как ориентир области касания", "Platform Default control size Minimum control size iOS, iPadOS 44x44 pt 28x28 pt macOS 28x28 pt 20x20 pt tvOS 66x66 pt 56x56 pt visionOS 60x60 pt 28x28 pt watchOS 44x44 pt 28x28 pt", HIG_ACC, value="44x44 pt", unit="pt"),
                sz("Минимальный размер контрола (iOS/iPadOS)", "iOS, iPadOS 44x44 pt 28x28 pt", HIG_ACC, value="28x28 pt", unit="pt"),
                sz("Рекомендованный padding вокруг элементов", "In general, it works well to add about 12 points of padding around elements that include a bezel. For elements without a bezel, about 24 points of padding", HIG_ACC, value="12 pt (с безелем) / 24 pt (без безеля)", unit="pt"),
                sz("Высота строки UITableView по умолчанию", "The default height in points of each row in the table view.", APL_ROWHEIGHT, value="UITableView.automaticDimension (вычисляется автоматически; фиксированного 44 pt в документации нет)", unit=None),
            ],
            "variants": [
                "grouped — только в HIG: \"In iOS and iPadOS, for example, the grouped style uses headers, footers, and additional space to separate groups of data\"",
                "plain — только в API UIKit: \"A plain table view.\" (UITableView.Style)",
                "insetGrouped — только в API UIKit: \"A table view where the grouped sections are inset with rounded corners.\"",
                "SwiftUI ListStyle: automatic, bordered, carousel, elliptical, grouped, inset, insetGrouped, plain, sidebar",
                "macOS bordered (чередующийся фон строк), watchOS elliptical",
                "паттерн строки: info button (detail disclosure) vs disclosure indicator",
            ],
            "touch_target_dp": 44,
            "touch_target_note_ru": "Значение в pt, не в dp: HIG даёт 44x44 pt как размер контрола по умолчанию для iOS/iPadOS и 28x28 pt как минимум.",
            "notes_ru": "HIG не публикует ни одной числовой высоты строки списка или таблицы — только стили, правила контента и паттерн disclosure. Числа для iOS ограничены областями касания (44x44 pt) и padding вокруг элементов (12/24 pt).",
            "sources": [HIG_LT, HIGJ + "lists-and-tables.json", HIG_ACC, APL_LISTSTYLE, APL_UITV_STYLE, APL_ROWHEIGHT],
        },
    },
    "not_recommended_ru": [
        "Ни одна из трёх платформ не даёт высоты для строк «4+ строк»: MD3 ограничен one/two/three-line (56/72/88 dp), Angular Material — тремя строками, HIG чисел не даёт вовсе.",
        "Ни MD3, ни iOS HIG не имеют density/compact-режима списка — density API есть только у Angular Material (шкала 0…-5).",
        "Ни одна платформа не публикует числовой touch target именно для строки списка: у Angular Material 48 px заведён только у кнопок, в токенах MD3 такого параметра нет, у HIG есть лишь общая рекомендация 44x44 pt для контролов.",
        "Нет согласия по высоте двухстрочной строки: MD3 — 72 dp, Angular Material — 64 px. Совмещать значения двух Material-платформ без явного решения нельзя.",
        "Ни у MD3, ни у Angular Material, ни у HIG нет варианта «список с несколькими колонками» — это уже таблица.",
    ],
    "verdict_ru": "List — самый обеспеченный числами компонент набора. MD3 даёт 56/72/88 dp, отступы 16 dp, контейнер 8 px, внутренние токены строки 12 dp и токены состояний (hover 0.08, focus/pressed 0.12) — это единственная платформа с полной машинно-читаемой спецификацией. Angular Material в M3-теме использует другие высоты (48/64/88 px) плюс density API «0…-5», поэтому числа двух Material-платформ не взаимозаменяемы. iOS HIG сознательно не даёт высот строк — только стили (grouped/plain/insetGrouped) и общий минимум контрола 44x44 pt. Для iiko DS: эталон высот — MD3, density — из Angular Material, iOS даёт только стили и правило раскрытия.",
}

# =============================================================== CARD
card_core = {
    "component": "Card (карточка)",
    "verified_at": VERIFIED,
    "platforms": {
        "md3": {
            "exists": True,
            "component_name": "Cards: elevated / filled / outlined (страница m3.material.io + официальные токены *_card)",
            "sizes": [
                sz("Радиус контейнера elevated card = md.sys.shape.corner.medium", "'container-shape': map.get($deps, 'md-sys-shape', 'corner-medium'),", MW_CARD_TOK, value=12, unit="dp"),
                sz("Радиус контейнера filled card = corner.medium", "'container-shape': map.get($deps, 'md-sys-shape', 'corner-medium'),", MW_CARD_FILLED, value=12, unit="dp"),
                sz("Радиус контейнера outlined card = corner.medium", "'container-shape': map.get($deps, 'md-sys-shape', 'corner-medium'),", MW_CARD_OUTLINED, value=12, unit="dp"),
                sz("Значение токена md.sys.shape.corner.medium", "'corner-medium': if($exclude-hardcoded-values, null, 12px),", MW_SHAPE_TOK, value=12, unit="dp"),
                sz("Толщина обводки outlined card", "'outline-width': if($exclude-hardcoded-values, null, 1px),", MW_CARD_OUTLINED, value=1, unit="dp"),
                sz("Размер иконки в карточке", "'icon-size': if($exclude-hardcoded-values, null, 24px),", MW_CARD_TOK, value=24, unit="dp"),
                sz("Внутренние отступы карточки (padding)", NF, None, value=NF, unit=None),
            ],
            "variants": [
                "elevated card (m3.material.io: \"Cards display content and actions about a single subject. Explore three types: elevated, filled and outlined.\")",
                "filled card",
                "outlined card",
                "типографика карточки по токенам: title = title-large (1.375rem/22px), subtitle = title-medium (1rem/16px)",
            ],
            "touch_target_dp": None,
            "touch_target_note_ru": "Токена touch target у карточек MD3 нет — " + NF,
            "notes_ru": "У карточек в официальном наборе токенов MD3 есть container-shape (corner-medium = 12 dp), outline-width 1 px, icon-size 24 px, elevation и типографика — но НЕТ токена внутренних отступов. Значение 16 dp, которое обычно называют «padding карточки MD3», в токенах MD3 не зафиксировано: оно существует как формулировка 'the standard padding specified in the Material Design spec' в документации Angular Material (см. платформу angular_material). Спец-страница m3.material.io/components/cards/specs существует, но рендерится клиентским JS — числа из неё машинно не извлекаются. Компонента Card в Material Web нет (в all.ts таких экспортов нет).",
            "sources": [M3_CARDS, MW_CARD_TOK, MW_CARD_FILLED, MW_CARD_OUTLINED, MW_SHAPE_TOK, MW_ALL, MW_TYPES_TOK],
        },
        "angular_material": {
            "exists": True,
            "component_name": "mat-card (+ mat-card-header, mat-card-content, mat-card-actions, mat-card-footer, mat-card-title, mat-card-subtitle, mat-card-title-group, mat-card-image, mat-card-avatar)",
            "sizes": [
                sz("Padding контента карточки по умолчанию", "// Default padding for text content within a card.\n$mat-card-default-padding: 16px !default;", AM_CARD_SCSS, value=16, unit="px"),
                sz("Padding шапки карточки", "// Apply default padding for a text content region. Omit any bottom padding because we assume\n    // this region will be followed by another region that includes top padding.\n    padding: $mat-card-default-padding $mat-card-default-padding 0;", AM_CARD_SCSS, value="16 16 0", unit="px"),
                sz("Размер аватара в шапке", "// Size of the `mat-card-header` region custom to Angular Material.\n$mat-card-header-size: 40px !default;", AM_CARD_SCSS, value=40, unit="px"),
                sz("Минимальная высота блока действий", "min-height: 52px;\n  padding: 8px;", AM_CARD_SCSS, value=52, unit="px"),
                sz("Padding блока действий", "min-height: 52px;\n  padding: 8px;", AM_CARD_SCSS, value=8, unit="px"),
                sz("Изображение sm-image", "// Specifically sized small image, specific to Angular Material.\n.mat-mdc-card-sm-image {\n  width: 80px;\n  height: 80px;\n}", AM_CARD_SCSS, value="80x80", unit="px"),
                sz("Изображение md-image", "// Specifically sized medium image, specific to Angular Material.\n.mat-mdc-card-md-image {\n  width: 112px;\n  height: 112px;\n}", AM_CARD_SCSS, value="112x112", unit="px"),
                sz("Изображение lg-image", "// Specifically sized large image, specific to Angular Material.\n.mat-mdc-card-lg-image {\n  width: 152px;\n  height: 152px;\n}", AM_CARD_SCSS, value="152x152", unit="px"),
                sz("Изображение xl-image", "// Specifically sized extra-large image, specific to Angular Material.\n.mat-mdc-card-xl-image {\n  width: 240px;\n  height: 240px;\n}", AM_CARD_SCSS, value="240x240", unit="px"),
                sz("Радиус контейнера (все три варианта) = corner-medium, обводка 1 px у outlined", "card-elevated-container-shape: map.get($system, corner-medium),\n      card-filled-container-shape: map.get($system, corner-medium),\n      card-outlined-container-shape: map.get($system, corner-medium),\n      card-outlined-outline-width: 1px,", AM_CARD_M3, value=12, unit="dp"),
                sz("Типографика заголовка = title-large", "card-title-text-size: map.get($system, title-large-size),", AM_CARD_M3, value="title-large", unit=None),
                sz("Типографика подзаголовка = title-medium", "card-subtitle-text-size: map.get($system, title-medium-size),", AM_CARD_M3, value="title-medium", unit=None),
            ],
            "variants": [
                "секции: mat-card-header, mat-card-content, mat-card-actions, mat-card-footer, <img mat-card-image>",
                "шапка: mat-card-title, mat-card-subtitle, <img mat-card-avatar>, mat-card-title-group",
                "<mat-card-actions align=\"start|end\">",
                "M3-варианты по токенам: elevated / filled / outlined",
                "a11y-роли: role=group / region / landmark; tabindex 0 / -1 / без tabindex",
            ],
            "density": "НЕТ. В M3-токенах карточки указано 'density: ()' — density-настроек у mat-card нет.",
            "touch_target_dp": None,
            "notes_ru": "Именно Angular Material документирует 16 px как «стандартный padding из спецификации Material Design»: 'In many cases developers may just want the standard padding specified in the Material Design spec. In this case, the <mat-card-header>, <mat-card-content>, and <mat-card-footer> sections can be used.' Так как токена padding у MD3 нет, 16 dp придётся обосновывать этой формулировкой, а не ссылкой на токен MD3. Размеры изображений 80/112/152/240 px и avatar 40 px помечены в исходниках как 'specific to Angular Material' — в спеке-числах MD3 их нет.",
            "sources": [AM_CARD_MD, AM_CARD_M3, AM_CARD_SCSS],
        },
        "ios_hig": {
            "exists": False,
            "component_name": "нет — страница Cards в HIG отсутствует (HTTP 404)",
            "sizes": [],
            "variants": [],
            "touch_target_dp": 44,
            "touch_target_note_ru": "44x44 pt — общий размер контрола из HIG Accessibility; к карточкам он не привязан.",
            "notes_ru": "В iOS HIG карточки нет: developer.apple.com/design/human-interface-guidelines/cards возвращает 404, а в разделах Lists and tables, Collections и Layout карточка не описана ни как компонент, ни численно — " + NF + ". Ближайшие описанные паттерны для iOS — списки/таблицы и collections (row/grid). Любые «карточки iOS» в дизайн-системе будут вне HIG, то есть без официального источника.",
            "sources": [HIG_LT, HIG_COLL, HIG + "cards (HTTP 404)"],
        },
    },
    "not_recommended_ru": [
        "Ни одна из трёх платформ не задаёт размеров карточки (ширина/высота/аспект) — только радиус, обводка, тень и типографика.",
        "Padding-токен карточки отсутствует у MD3: 16 dp существует только как формулировка «standard padding из спеки Material Design» в документации Angular Material.",
        "Density карточки нет нигде: ни MD3 (нет токена), ни Angular Material ('density: ()'), ни в HIG.",
        "У iOS HIG карточки нет вообще — брать с iOS числа для карточек нельзя ни в каком виде.",
        "Ни одна платформа не даёт отдельного touch target для карточки и не описывает «карточку-список» или карточку с изображением и аватаром одновременно.",
    ],
    "verdict_ru": "Карточку можно обосновать лишь частично: MD3 официально даёт радиус 12 dp (corner-medium), обводку 1 dp у outlined и иконку 24 dp — но ни padding, ни размеров. 16 dp опирается на формулировку Angular Material «standard padding specified in the Material Design spec», и называть это «числом из MD3» неверно. Angular Material добавляет неспековые размеры (avatar 40 px, изображения 80/112/152/240 px, actions 52/8 px) и не имеет density. iOS HIG карточку не описывает, поэтому ссылка на iOS в разделе карточек недопустима.",
}

# =============================================================== EXPANSION PANEL
exp_core = {
    "component": "Expansion panel (раскрывающаяся панель)",
    "verified_at": VERIFIED,
    "platforms": {
        "md3": {
            "exists": False,
            "component_name": "нет — в MD3 такого компонента нет",
            "sizes": [],
            "variants": [],
            "touch_target_dp": None,
            "notes_ru": "В MD3 панели раскрытия нет: m3.material.io/components/expansion-panels и m3.material.io/components/accordion отдают 404; в наборе официальных токенов MD3 (tokens/versions/v0_192) файлов с именами *_expansion* или *_accordion* нет; в официальной веб-библиотеке Material Web компонента тоже нет (all.ts). Всё, что можно указать, — " + NF + ".",
            "sources": ["https://m3.material.io/components/expansion-panels (HTTP 404)", "https://m3.material.io/components/accordion (HTTP 404)", MW_ALL],
        },
        "angular_material": {
            "exists": True,
            "component_name": "mat-expansion-panel, mat-accordion (+ mat-expansion-panel-header, mat-panel-title, mat-panel-description)",
            "sizes": [
                sz("Высота шапки в свёрнутом состоянии", "// Default minimum and maximum height for collapsed panel headers.\n$header-collapsed-height: 48px !default;", AM_EXP_VARS, height_dp=48),
                sz("Минимальная высота свёрнутой шапки", "$header-collapsed-minimum-height: 36px !default;", AM_EXP_VARS, height_dp=36),
                sz("Высота шапки в раскрытом состоянии", "// Default minimum and maximum height for expanded panel headers.\n$header-expanded-height: 64px !default;", AM_EXP_VARS, height_dp=64),
                sz("Минимальная высота раскрытой шапки", "$header-expanded-minimum-height: 48px !default;", AM_EXP_VARS, height_dp=48),
                sz("Высоты шапки в M3-токенах (плотность 0)", "expansion-header-collapsed-state-height: list.nth((48px, 44px, 40px, 36px), $index),\n    expansion-header-expanded-state-height: list.nth((64px, 60px, 56px, 48px), $index),", AM_EXP_M3, height_dp=48),
                sz("Радиус контейнера панели", "expansion-container-shape: 12px,", AM_EXP_M3, value=12, unit="dp"),
                sz("Горизонтальный padding шапки (внутри .mat-expansion-panel-header)", "padding: 0 24px;", AM_EXP_HDR, value=24, unit="px"),
                sz("Длительность и кривая анимации раскрытия", "$header-transition: 225ms cubic-bezier(0.4, 0, 0.2, 1);", AM_EXP_VARS, value="225 ms cubic-bezier(0.4, 0, 0.2, 1)", unit=None),
                sz("Типографика текста шапки = title-medium", "expansion-header-text-size: map.get($system, title-medium-size),", AM_EXP_M3, value="title-medium", unit=None),
                sz("Типографика контента панели = body-large", "expansion-container-text-size: map.get($system, body-large-size),", AM_EXP_M3, value="body-large", unit=None),
                sz("Padding раскрытого контента панели", NF, None, value=NF, unit=None),
            ],
            "variants": [
                "одиночная панель",
                "mat-accordion (multi=\"false\" по умолчанию — открыта одна панель; multi=\"true\" — несколько)",
                "hideToggle (скрыть индикатор раскрытия)",
                "disabled",
                "блок действий внизу панели (виден только в раскрытом состоянии)",
                "ленивый рендер контента через <ng-template matExpansionPanelContent>",
                "a11y: role=\"button\" на шапке + aria-controls (имитация <details>/<summary>)",
            ],
            "density": "Есть: clamp-density($scale, -3); свёрнутая шапка (48, 44, 40, 36), раскрытая (64, 60, 56, 48).",
            "touch_target_dp": None,
            "touch_target_note_ru": "Отдельного touch target для шапки панели нет ни в исходниках Angular Material, ни в MD3/HIG — " + NF,
            "notes_ru": "Единственная платформа с этим компонентом — Angular Material. Модель высот шапки: 48 px свёрнутая (минимум 36), 64 px раскрытая (минимум 48); при плотности -1…-3 — (44, 40, 36) и (60, 56, 48). Padding контента числами не документирован (" + NF + "), в исходниках задан только padding шапки (0 24px) и разделитель блока действий (цвет outline).",
            "sources": [AM_EXP_MD, AM_EXP_M3, AM_EXP_VARS, AM_EXP_HDR],
        },
        "ios_hig": {
            "exists": True,
            "component_name": "Disclosure controls (disclosure triangle / disclosure button) — ближайший раскрывающийся паттерн, но не панель",
            "sizes": [
                sz("Числовые размеры панели/шапки в HIG", NF, None, value=NF, unit=None),
                sz("Область касания для контролов", "Platform Default control size Minimum control size iOS, iPadOS 44x44 pt 28x28 pt macOS 28x28 pt 20x20 pt", HIG_ACC, value="44x44 pt", unit="pt"),
            ],
            "variants": [
                "disclosure triangle (поворот: внутрь — скрыто, вниз — раскрыто)",
                "disclosure button",
                "disclosure indicator в строке списка (переход на следующий уровень, а не раскрытие на месте)",
                "macOS: outline view с disclosure triangles",
            ],
            "touch_target_dp": 44,
            "touch_target_note_ru": "44x44 pt — общий размер контрола из HIG Accessibility, не привязан к панели.",
            "notes_ru": "HIG описывает раскрытие как disclosure control, а не как панель: 'A disclosure triangle shows and hides information and functionality associated with a view or a list of items.' и 'A disclosure triangle points inward from the leading edge when its content is hidden and down when its content is visible. Clicking or tapping the disclosure triangle switches between these two states, and the view expands or collapses accordingly to accommodate the content.' Ни высот, ни отступов, ни таймингов анимации в HIG нет — " + NF + ".",
            "sources": [HIG_DIS, HIGJ + "disclosure-controls.json", HIG_LT, HIG_ACC],
        },
    },
    "not_recommended_ru": [
        "Компонента нет в MD3 вообще: ни спеки, ни токенов, ни реализации — обосновать панель «по Material» невозможно.",
        "В HIG нет панели: есть только disclosure-паттерн без единого числа (высота, отступы, тайминг анимации отсутствуют).",
        "Padding раскрытого контента не документирован числами ни у Angular Material, ни в других источниках.",
        "Density/compact-вариант есть только у Angular Material (до -3); MD3 и HIG его не имеют.",
        "Ни одна платформа не даёт touch target для шапки панели (48 px у Angular Material — это высота шапки, а не область касания).",
    ],
    "verdict_ru": "Expansion panel отсутствует и в MD3, и в iOS HIG — все числа приходят только из Angular Material: шапка 48 px свёрнутая / 64 px раскрытая (минимумы 36/48), радиус 12 dp, padding шапки 24 px, анимация 225 ms, density до -3. Это значит, что для iiko DS панель нельзя выдать за «платформенную рекомендацию» двух платформ из трёх: iOS даёт лишь паттерн disclosure без чисел, а MD3 — ничего. Остаётся либо принять реализацию Angular Material как эталон, либо зафиксировать собственные константы, честно пометив отсутствие внешних источников.",
}

# =============================================================== TABLE
tbl_core = {
    "component": "Table (data table)",
    "verified_at": VERIFIED,
    "platforms": {
        "md3": {
            "exists": True,
            "component_name": "Data table — спеки и компонента нет, но официальные токены md.comp.data-table опубликованы",
            "exists_note_ru": "Страницы спецификации нет: m3.material.io/components/tables, /components/table и /components/data-table отдают 404; в Material Web компонента нет (all.ts). Однако в официальном наборе токенов MD3 есть файл _md-comp-data-table.scss — это единственный источник чисел MD3 по таблице.",
            "sizes": [
                sz("Высота строки заголовка", "'header-container-height': if($exclude-hardcoded-values, null, 56px),", MW_DT_TOK, height_dp=56),
                sz("Высота строки данных", "'row-item-container-height': if($exclude-hardcoded-values, null, 52px),", MW_DT_TOK, height_dp=52),
                sz("Высота футера", "'footer-container-height': if($exclude-hardcoded-values, null, 52px),", MW_DT_TOK, height_dp=52),
                sz("Толщина внешней обводки таблицы", "'outline-width': if($exclude-hardcoded-values, null, 1px),", MW_DT_TOK, value=1, unit="dp"),
                sz("Толщина обводки строки", "'row-item-outline-width': if($exclude-hardcoded-values, null, 1px),", MW_DT_TOK, value=1, unit="dp"),
                sz("Кегль текста заголовка = title-small", "'header-headline-size':\n      map.get($deps, 'md-sys-typescale', 'title-small-size'),", MW_DT_TOK, value="title-small", unit=None),
                sz("Значение title-small", "'title-small-size': if($exclude-hardcoded-values, null, 0.875rem),", MW_TYPES_TOK, value="0.875rem (14px)", unit="rem"),
                sz("Кегль текста строки данных = body-medium", "'row-item-label-text-size':\n      map.get($deps, 'md-sys-typescale', 'body-medium-size'),", MW_DT_TOK, value="body-medium", unit=None),
                sz("Значение body-medium", "'body-medium-size': if($exclude-hardcoded-values, null, 0.875rem),", MW_TYPES_TOK, value="0.875rem (14px)", unit="rem"),
                sz("Padding ячеек", NF, None, value=NF, unit=None),
            ],
            "variants": [
                "вариантов компоновки нет: страницы компонента не существует, есть только токены",
                "токенами описаны: строка заголовка, строка данных (selected/unselected), футер, иконка сортировки при ховере заголовка",
                "состояния строки по токенам: row-item-selected-container-color, row-item-selected-hover-state-layer-opacity, row-item-unselected-*",
            ],
            "touch_target_dp": None,
            "touch_target_note_ru": "Токена touch target для таблицы в MD3 нет — " + NF,
            "notes_ru": "MD3 описывает таблицу только токенами: заголовок 56 dp, строка и футер 52 dp, обводки 1 dp, заголовок title-small (14 px), данные body-medium (14 px), состояния selected/unselected и ховер иконки сортировки. Padding ячеек, density, sticky-поведение, ширина колонок и любая вариативность в токенах отсутствуют — " + NF + ". Компонента в Material Web не существует.",
            "sources": [MW_DT_TOK, MW_TYPES_TOK, MW_ALL, "https://m3.material.io/components/tables (HTTP 404)"],
        },
        "angular_material": {
            "exists": True,
            "component_name": "mat-table / mat-header-row / mat-row (CDK table)",
            "sizes": [
                sz("Высота строки заголовка (значение по умолчанию = токен MD3)", "height: token-utils.slot(table-header-container-height, $fallbacks, 56px);", AM_TBL_SCSS, height_dp=56),
                sz("Высота строки данных", "height: token-utils.slot(table-row-item-container-height, $fallbacks, 52px);", AM_TBL_SCSS, height_dp=52),
                sz("Высота футера", "height: token-utils.slot(table-footer-container-height, $fallbacks, 52px);", AM_TBL_SCSS, height_dp=52),
                sz("Горизонтальный padding ячейки заголовка", ".mdc-data-table__header-cell {\n  padding: 0 16px;\n}", AM_TBL_SCSS, value=16, unit="px"),
                sz("Кегль заголовка", "font-size: token-utils.slot(table-header-headline-size, $fallbacks, 14px);", AM_TBL_SCSS, value=14, unit="px"),
                sz("Кегль строки данных", "font-size: token-utils.slot(table-row-item-label-text-size, $fallbacks, 14px);", AM_TBL_SCSS, value=14, unit="px"),
                sz("Толщина обводки строки", "table-row-item-outline-width: 1px,", AM_TBL_M3, value=1, unit="px"),
                sz("Высоты заголовка по плотностям 0/-1/-2/-3/-4", "table-header-container-height: list.nth((56px, 52px, 48px, 44px, 40px), $index),", AM_TBL_M3, height_dp=56),
                sz("Высоты строки и футера по плотностям 0/-1/-2/-3/-4", "table-footer-container-height: list.nth((52px, 48px, 44px, 40px, 36px), $index),\n    table-row-item-container-height: list.nth((52px, 48px, 44px, 40px, 36px), $index),", AM_TBL_M3, height_dp=52),
            ],
            "variants": [
                "sticky header: 'In order to fix the header row to the top of the scrolling viewport containing the table, you can add a `sticky` input to the `matHeaderRowDef`.'",
                "sticky footer (в Safari нужен sticky на всех rendering строках футера)",
                "sticky колонки: 'To do this, add the `sticky` or `stickyEnd` directive to the `ng-container` column definition.'",
                "несколько шаблонов строк (по предикату when)",
                "footer row (mat-footer-row)",
                "нативная <table> и flex-таблица (отдельный файл _table-flex-styles.scss)",
            ],
            "density": "Есть: clamp-density($scale, -4); заголовок (56, 52, 48, 44, 40), строка и футер (52, 48, 44, 40, 36).",
            "touch_target_dp": None,
            "touch_target_note_ru": "Токена touch target для таблицы нет — " + NF,
            "notes_ru": "Angular Material повторяет токенные значения MD3 (заголовок 56, строка/футер 52) и добавляет то, чего у MD3 нет: padding ячейки 16 px, кегль 14 px, density (до -4), sticky-заголовок, sticky-футер, sticky-колонки, footer row, несколько шаблонов строк. Sticky реализован классом '.mat-mdc-table-sticky { position: sticky !important; }'. В документации отдельно предупреждают о дрожании stuck-ячеек в Safari на мобильных и в Edge.",
            "sources": [AM_TBL_MD, AM_TBL_SCSS, AM_TBL_M3, AM_TBL_FLEX],
        },
        "ios_hig": {
            "exists": True,
            "component_name": "Lists and tables (HIG) / Table, UITableView (API)",
            "sizes": [
                sz("Высота строки/заголовка таблицы в HIG", NF, None, value=NF, unit=None),
                sz("Область касания (общий размер контрола)", "Platform Default control size Minimum control size iOS, iPadOS 44x44 pt 28x28 pt macOS 28x28 pt 20x20 pt tvOS 66x66 pt 56x56 pt visionOS 60x60 pt 28x28 pt watchOS 44x44 pt 28x28 pt", HIG_ACC, value="44x44 pt", unit="pt"),
                sz("Высота строки UITableView по умолчанию", "The default height in points of each row in the table view.", APL_ROWHEIGHT, value="UITableView.automaticDimension (вычисляется автоматически; 44 pt не зафиксировано)", unit=None),
            ],
            "variants": [
                "plain — API UIKit: 'A plain table view.'",
                "grouped — API UIKit: 'A table view where sections have distinct groups of rows.'; HIG: 'the grouped style uses headers, footers, and additional space to separate groups of data'",
                "insetGrouped — API UIKit: 'A table view where the grouped sections are inset with rounded corners.'",
                "macOS bordered (чередующийся фон строк), watchOS elliptical",
                "для иерархии HIG рекомендует outline view: 'Use an outline view instead of a table view to present hierarchical data.'",
            ],
            "touch_target_dp": 44,
            "touch_target_note_ru": "44x44 pt — общий размер контрола из HIG Accessibility, к строкам таблицы напрямую не привязан.",
            "notes_ru": "HIG не даёт ни одной числовой высоты строки, заголовка или ячейки таблицы (" + NF + "); Apple-документация rowHeight также не фиксирует 44 pt, а описывает высоту как вычисляемую автоматически. Числовая часть HIG по таблицам ограничена общей рекомендацией 44x44 pt. Дополнительно HIG требует: описательные заголовки колонок в title case без завершающей точки, сортировку по клику на заголовок (macOS), изменение ширины колонок и чередующийся фон строк для широких многоколоночных таблиц.",
            "sources": [HIG_LT, HIGJ + "lists-and-tables.json", HIG_ACC, APL_UITV_STYLE, APL_ROWHEIGHT, HIG_OUT],
        },
    },
    "not_recommended_ru": [
        "У MD3 нет ни страницы спецификации таблицы, ни компонента — только токены: никаких правил поведения (sticky, сортировка, ширина колонок, padding ячеек) MD3 не публикует.",
        "iOS HIG не даёт ни одного числа по таблице (ни высоты строки, ни заголовка, ни padding ячейки) — только стили plain/grouped/insetGrouped.",
        "Padding ячейки 16 px существует только у Angular Material; в токенах MD3 такого параметра нет, поэтому «16 dp по Material» для таблицы подтвердить нечем.",
        "Density таблицы есть только у Angular Material (до -4); MD3 и HIG её не имеют.",
        "Ни одна платформа не публикует минимальную ширину колонки, максимальное число колонок и правило для многострочных ячеек (переменная высота строки).",
        "Sticky-строки и sticky-колонки официально описаны только у Angular Material (плюс предупреждение о дрожании в Safari/Edge); MD3 и HIG этого не описывают.",
    ],
    "verdict_ru": "Таблица — случай, где «платформенная рекомендация» фактически одна: MD3 даёт только токены (56/52/52 dp, обводки 1 dp, title-small/body-medium), HIG — только стили без чисел, а всю рабочую числовую обвязку (padding ячейки 16 px, кегль 14 px, density до -4, sticky заголовка и колонок) даёт Angular Material. Для iiko DS: высоты 56/52/52 dp можно взять как согласованные у MD3 и Angular Material, а всё остальное — либо принять из Angular Material, либо зафиксировать как собственную константу системы с пометкой, что у MD3/HIG этих чисел нет.",
}

# =============================================================== TREE
tree_core = {
    "component": "Tree (дерево)",
    "verified_at": VERIFIED,
    "platforms": {
        "md3": {
            "exists": False,
            "component_name": "нет — в MD3 дерева нет",
            "sizes": [],
            "variants": [],
            "touch_target_dp": None,
            "notes_ru": "В MD3 компонента «дерево» нет: m3.material.io/components/tree и /components/trees отдают 404; в наборе официальных токенов MD3 нет ни одного файла *_tree* (ближайшие — списки и меню); в официальной веб-библиотеке Material Web такого компонента нет (all.ts). Числа и варианты — " + NF + ".",
            "sources": ["https://m3.material.io/components/tree (HTTP 404)", "https://m3.material.io/components/trees (HTTP 404)", MW_ALL],
        },
        "angular_material": {
            "exists": True,
            "component_name": "mat-tree / mat-tree-node / mat-nested-tree-node (+ matTreeNodeDef, matTreeNodeToggle, matTreeNodePadding)",
            "sizes": [
                sz("Минимальная высота узла (плотность 0)", "tree-node-min-height: list.nth((48px, 44px, 40px, 36px, 28px), $index),", AM_TREE_M3, height_dp=48),
                sz("Отступ одного уровня (indent) по умолчанию", "* Default number 40px from material design menu sub-menu spec.", AM_CDK_INDENT, value=40, unit="px"),
                sz("Значение indent в CDK", "_indent: number = 40;", AM_CDK_INDENT, value=40, unit="px"),
                sz("Типографика узла = body-large", "tree-node-text-size: map.get($system, body-large-size),", AM_TREE_M3, value="body-large", unit=None),
                sz("Внутренний padding узла сверх indent", NF, None, value=NF, unit=None),
            ],
            "variants": [
                "flat tree (mat-tree-node; узлы — соседи): 'Flat trees are generally easier to style and inspect. They are also more friendly to scrolling variations, such as infinite or virtual scrolling.'",
                "nested tree (mat-nested-tree-node + matTreeNodeOutlet)",
                "matTreeNodeToggle (+ [matTreeNodeToggleRecursive]) — раскрытие и сворачивание, в том числе рекурсивно",
                "matTreeNodePadding (только flat tree) — отступ по уровню через matNodePadding",
                "несколько шаблонов узлов (предикат when)",
                "DataSource: levelAccessor (плоские данные) или childrenAccessor (вложенные), trackBy",
                "a11y: WAI-ARIA tree widget; для корректной работы нужны levelAccessor/childrenAccessor (treeControl не даёт правильной a11y), isExpandable на раскрываемых узлах",
            ],
            "density": "Есть: clamp-density($scale, -4); min-height узла (48, 44, 40, 36, 28).",
            "touch_target_dp": None,
            "touch_target_note_ru": "Токена touch target для узла/тогла нет — " + NF,
            "notes_ru": "Angular Material — единственный источник чисел: min-height узла 48 px при плотности 0 и отступ 40 px на уровень. В комментарии CDK отступ 40 px обоснован не дерево-спекою, а подменю меню: 'Default number 40px from material design menu sub-menu spec.' Внутренний padding узла числами не документирован (" + NF + "); для nested tree отступ задаётся CSS, отдельного токена нет.",
            "sources": [AM_TREE_MD, AM_TREE_M3, AM_TREE_SCSS, AM_CDK_INDENT],
        },
        "ios_hig": {
            "exists": True,
            "component_name": "Outline views — ближайший аналог дерева, описан только для macOS",
            "sizes": [
                sz("Высота строки и отступ уровня в HIG", NF, None, value=NF, unit=None),
                sz("Область касания (общий размер контрола)", "Platform Default control size Minimum control size iOS, iPadOS 44x44 pt 28x28 pt macOS 28x28 pt 20x20 pt", HIG_ACC, value="44x44 pt", unit="pt"),
            ],
            "variants": [
                "outline view с disclosure triangles: 'Parent containers have disclosure triangles that expand to reveal their children.'",
                "чередующиеся цвета строк в многоколоночных outline view",
                "редактирование данных, сохранение состояния раскрытия",
                "для неиерархических данных HIG советует таблицу (обратная рекомендация к lists-and-tables)",
            ],
            "touch_target_dp": 44,
            "touch_target_note_ru": "44x44 pt — общий размер контрола из HIG Accessibility, к узлам дерева напрямую не привязан.",
            "notes_ru": "HIG описывает иерархический список как outline view и только для macOS: 'An outline view includes at least one column that contains primary hierarchical data, such as a set of parent containers and their children.' Числовых значений (высота строки, отступ уровня, размер disclosure-треугольника) нет — " + NF + ". Отдельного компонента-дерева для iOS у Apple нет.",
            "sources": [HIG_OUT, HIGJ + "outline-views.json", HIG_LT, HIG_ACC],
        },
    },
    "not_recommended_ru": [
        "В MD3 дерева нет ни как компонента, ни как токенов — Material исключён как источник по дереву полностью.",
        "У Apple дерево описано только для macOS (outline views) и без чисел: ни отступ уровня, ни высота строки не заданы; для iOS компонента-дерева нет.",
        "Числовой отступ уровня (40 px) существует только в реализации Angular Material/CDK и обоснован спекой подменю меню, а не деревом — это не платформенная рекомендация.",
        "Ни одна платформа не даёт рекомендаций по максимальной глубине дерева, минимальному размеру toggle-иконки и поведению при горизонтальном скролле.",
        "Density узла есть только у Angular Material (до -4); MD3 и HIG плотности не задают.",
    ],
    "verdict_ru": "Дерево — самый «бесхозный» компонент набора: MD3 его не имеет вовсе, iOS HIG описывает только macOS outline view и без единого числа. Все числа (min-height узла 48 dp при плотности 0 и отступ 40 px на уровень) приходят исключительно из Angular Material, причём 40 px в исходниках мотивированы спекой подменю меню, а не дерева. Для страницы iiko DS это надо показать прямо: дерево — компонент без платформенного эталона, значения берутся из реализации и должны быть зафиксированы как решение дизайн-системы.",
}

files = {
    "list": list_core,
    "card": card_core,
    "expansion-panel": exp_core,
    "table": tbl_core,
    "tree": tree_core,
}

for slug, data in files.items():
    p = os.path.join(OUT, slug + ".json")
    with open(p, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
        f.write("\n")
    print("wrote", p, os.path.getsize(p), "bytes")
