# Задание: доделать страницы рекомендаций iiko DS

Страницы генерируются из данных:
`C:\Users\asukharev\GitHub\iiko-DS\DS\_audit\rec\data\<slug>.json` → `_audit\rec\build.py` →
`iiko-ds-mobile\prototypes\recommendations\<slug>.html`.

**Эталон** (сделан и принят владельцем): `C:\Users\asukharev\GitHub\iiko-DS\DS\_audit\rec\data\button.json`.
Открой его и повторяй структуру дословно. Разметка экранов собирается хелперами
`C:\Users\asukharev\GitHub\iiko-DS\DS\_audit\rec\mock.py`.

## Что писать

Один файл на компонент, в подпапку своей задачи:

- `out\edits\<slug>.json` → `{"slug": "...", "edits": [...]}`
- `out\previews\<slug>.json` → `{"slug": "...", "preview_html": "..."}`
- `out\platforms\<slug>.json` → `{"slug": "...", "platform_notes_ru": [...], "logic_ru": [...]}`

Полный вид (когда делаешь все три блока — в своей подпапке только свои ключи):

```json
{"slug": "<slug>",
 "edits": [{"row": 0, "edits": [{"id": "height", "v": 44, "sel": ".ds-btn", "css": "height:@px"}]}],
 "platform_notes_ru": [{"title": "Material Design 3", "items": ["...", "..."]},
                       {"title": "iOS HIG", "items": ["...", "..."]}],
 "logic_ru": ["...", "..."],
 "preview_html": "<div class=\"phones\">…</div>"}
```

Больше НИЧЕГО не менять: не трогать `data/*.json`, `build.py`, `mock.py`,
`iiko-ds-web`, страницы в `recommendations/`, сервер и браузер, файлы других
подпапок `out/`. Только свои файлы в своей подпапке.

## 1. edits — 4-я колонка «Правка»

Поле делается для каждой строки `changes`, где в колонке **Mobile есть конкретное
число в px** (например «48 px», «44 px», «56 px», «16 / 24»). Если в Mobile числа
нет («те же», «тот же», «на всю ширину», «по содержимому») — строку пропустить,
в `edits` её не включать.

- `row` — индекс строки в `changes` (с нуля).
- `v` — это число из колонки Mobile.
- `sel` — CSS-селектор элемента этого компонента. **Обязательно проверить скриптом,
  что селектор находится в разметке страницы** (классы брать из `examples[].html`
  в `data/<slug>.json`). Пример проверки:
  `python -c "import json,re;s=open('.../<slug>.json',encoding='utf-8').read();print(len(re.findall(r'\.ds-checkbox\b', s)))"`
- `css` — реальные CSS-свойства, которые меняют именно это значение:
  `height`, `min-height`, `width`, `min-width`, `padding-top/bottom/left/right`,
  `font-size`, `gap`, `border-radius`, `margin-left` и т. п. `@` заменяется на число,
  `@px` — на число с `px`.
- Правило применяется на странице как `[data-mode="mobile"] <sel> { … }` внутри
  мобильной панели — значит селектор должен целить компонент, который на странице
  реально есть.
- Два числа в одной строке (верт./гор. паддинги, «20 × 20») → два объекта в `edits`.
- `id` — короткий латинский, уникальный внутри компонента (`height`, `pad-v`, `font`).
- `sync` — только если одно значение линейно связано с другим, как в эталоне:
  `"sync": {"field": "pad-v", "a": 0.5, "b": -10}` значит `t = a * v + b`.

Пример (button.json, строка «Паддинги»):

```json
{"row": 2, "edits": [
  {"id": "pad-v", "v": 12, "sel": ".ds-btn", "css": "padding-top:@px; padding-bottom:@px",
   "sync": {"field": "height", "a": 2, "b": 20}},
  {"id": "pad-h", "v": 16, "sel": ".ds-btn", "css": "padding-left:@px; padding-right:@px"}]}
```

## 2. platform_notes_ru — две первые колонки блока «Что говорят платформы»

Две группы: `{"title": "Material Design 3", …}` и `{"title": "iOS HIG", …}`
(третью колонку «Логика» generator добавляет сам из `logic_ru`).

По 3–6 пунктов в каждой колонке. Пункт — короткая фраза по-русски: что платформа
задаёт для ЭТОГО компонента, какое число, что лучше и какие опасения («нельзя»,
«риск», «не рекомендуется»), в скобках — источник.

Источники (числа брать только оттуда, ничего не выдумывать):
- `C:\Users\asukharev\GitHub\iiko-DS\DS\_audit\platform\<slug>.json` — ключи `platforms.md3`,
  `platforms.angular`, `platforms.apple` (числа + цитаты + ссылки), `not_recommended_ru`,
  `verdict_ru`. Имя файла может отличаться от slug: `radio` → `radio-button.json`,
  `hint-tooltip` → `tooltip.json`, `form-field` → `text-field.json`,
  `table-2-lvl` → `table.json`, `snackbar` → `snackbar.json` / `toast.json`,
  `text-ui` → ближайший из имеющихся.
- `C:\Users\asukharev\GitHub\iiko-DS\DS\_audit\rec\data-tech\<slug>.json` — если есть.
- Строки `changes` этой же страницы (`data/<slug>.json`) — мобильные значения ДС.

Пример колонки Material для Button: «Держать подписи короткими именно ради одной
строки: MD3 про rich tooltip — … (tooltip.json)».

## 3. logic_ru — третья колонка «Логика (от себя, без источника)»

3–6 пунктов: практические решения по компоненту на мобиле — что делать и что нельзя.
Без ссылок на источники. (В эталоне это `logic_ru` у button.json.)

## 4. preview_html — блок «На экране», ровно 3 экрана

Собирается хелперами `mock.py`:

```python
import sys; sys.path.insert(0, r"C:\Users\asukharev\GitHub\iiko-DS\DS\_audit\rec")
from mock import *
html = phones(
    screen(status() + head("Новый заказ") + body(search() + lst([...])) + foot(btn("Отмена"), btn("Создать")),
           "Подпись под экраном"),
    ... ещё два ...)
assert check_balance(html) == 0
```

Требования:
- **ровно 3 экрана** (`phones(screen(...), screen(...), screen(...))`);
- три **разных** экрана — разные раскладки и разный состав (например: список с
  поиском, форма/карточка, шторка снизу или диалог); одинаковые «фоны» не годятся;
- **изучаемый компонент присутствует и узнаваем на каждом экране** (или минимум
  на двух, но подпись не должна врать);
- разметка ДС — дословно: классы элементов брать из `examples[].html` этой же
  страницы, остальные блоки — хелперы `mock.py` (`head`, `body`, `foot`, `line`,
  `actions`, `lst`, `search`, `input_field`, `btn`, `iconbtn`, `checkbox`, `radio`,
  `toggle`, `tabs`, `sheet`, `card`, `card_head`, `chips`, `row`, `divider`, `icons`,
  `plain_icon`, `status`). Если нужного блока нет — напиши локальную функцию в своём
  скрипте; `mock.py` не менять;
- все классы в HTML должны существовать: `phone__*` — в `iiko-ds-mobile\prototypes\recommendations\rec.css`,
  `ds-*` — в `iiko-ds-web\components\**` и `iiko-ds-mobile\components\**` (проверить grep);
- подписи под экранами (`caption`) — короткие, по-русски, про то, где компонент живёт.

Строку `preview_html` положить в json как есть (обёртка `<div class="phones">` уже внутри).

## 5. Проверка перед сдачей

- `check_balance(preview_html) == 0`;
- каждый `sel` из `edits` находится в разметке страницы;
- все классы из `preview_html` существуют в CSS ДС или в rec.css;
- json валиден, ключи ровно те, что описаны выше.

## Отчёт

Коротко: список слагов, по каждому — сколько строк с правками, где сомневался и почему.
