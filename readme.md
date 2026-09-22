# iiko-ds-mobile

Мобильный слой дизайн-системы iiko: всё, что относится к планшету и телефону.

## Структура

```
iiko-ds-mobile/
├── modes.css                  ось режима (размер): [data-mode="mobile"]
├── components/                только CSS компонентов (как в iiko-ds-web)
│   └── index.css              агрегатор мобильного слоя
├── prototypes/                страницы-прототипы (как в iiko-ds-prototypes)
│   ├── button-modes.html      демо: Desktop и Mobile рядом + замеры из браузера
│   └── recommendations/       собираются генератором, в репозиторий не коммитятся
├── desktop-to-mobile-plan.md  план перевода компонентов ДС на мобилу
├── desktop-to-mobile-plan.xlsx
├── mobile-mode-notes.md       архитектура переменных: режимы и темы
├── mobile-workflow.md         регламент для дизайнеров
├── mobile-steps.md            тот же процесс по шагам
└── mobile-block-schemes.md    схемы процесса
```

Правило структуры то же, что в `iiko-ds-web`: один компонент — одна папка
`components/<Имя>_DS/`. Здесь лежат только те файлы, которые существуют
**на мобиле иначе**: структурные `*_mob`-компоненты (другая раскладка или
состав — шторка снизу, липкий футер, вертикальная группа кнопок).

## Что здесь НЕ дублируется

- **База токенов.** Она одна — `iiko-ds-web/tokens.css` (1743 переменные из
  Figma). Копия в этом репозитории разошлась бы с оригиналом при первом же
  обновлении ДС.
- **Компоненты, которые на мобиле отличаются только размерами** (Button,
  Input, Toggle, List и т. д.). Это те же файлы в `iiko-ds-web/components/`;
  мобильные размеры для них задаёт `modes.css`. Так же устроена и Figma:
  режим `Mobile` создаётся **у коллекции переменных**, а не у компонента.

## Как этот репозиторий лежит рядом с остальными

Клонируется в ту же папку, что `iiko-ds-web`, `iiko-ds-prototypes` и `_audit` —
страницы и генератор подключают соседние папки относительными путями, имена папок
менять нельзя. Порядок клонирования и первые команды — в README корневого
репозитория `iiko-ds`.

`prototypes/recommendations/` — **вывод генератора**, а не исходники: страницы
собираются командой `python _audit/rec/build.py` из данных `_audit/rec/data/`.
В репозиторий они не коммитятся (в `.gitignore`), папка создаётся сама при первой
сборке.

## Как подключить

```html
<link rel="stylesheet" href="../iiko-ds-web/font.css">
<link rel="stylesheet" href="../iiko-ds-web/tokens.css">
<link rel="stylesheet" href="../iiko-ds-mobile/modes.css">             <!-- ось размера -->
<link rel="stylesheet" href="../iiko-ds-mobile/components/index.css">  <!-- мобильные *_mob -->
<link rel="stylesheet" href="../iiko-ds-web/components/index.css">
```
и на корне экрана — атрибут режима:

```html
<html data-mode="mobile">
```

Порядок важен: `modes.css` обязан идти после `tokens.css` (специфичность у
`[data-mode="mobile"]` и `:root` одинаковая, решает очерёдность).

## Проверка

Открыть `prototypes/button-modes.html` — там десктоп и мобила стоят
рядом на одной странице (в Figma так нельзя: режим глобальный на файл) и есть
таблица замеров, снятых из браузера: высота, паддинги, кегль, иконка, тач-зона.

Ожидаемые высоты: Desktop M 36 / S 28 / XS 24, Mobile M 44.

Отдельно — `prototypes/recommendations/index.html`: по каждому компоненту страница с тем,
что рекомендуют платформы (Material Design 3, Angular Material, iOS HIG), с реальными
значениями ДС и примерами только рекомендованных вариантов. Собраны:

- `recommendations/button.html` — остаётся только размер M: 36 px на десктопе, 44 px на мобиле;
- `recommendations/button-icon.html` — M: 36 × 36 → 40 × 40 px, иконка 20 px без изменений;
- `recommendations/button-toggle.html` — сегмент 28 → 40 px (единственная высота у M3 и Angular Material).
