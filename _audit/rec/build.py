"""Generator: one page per DS component -- "how the component changes desktop -> mobile".

Plain-language pages for designers / product / devs: two panels side by side, what changes, why.
No tokens, no sources tables, no measurements on the page (the numbers stay in the data file).

Per-component data: _audit/rec/data/<slug>.json      (page-facing, simple)
Technical notes (sources, platform spec, measurements): _audit/rec/data-tech/<slug>.json

Run:  python build.py
"""
import glob
import html
import json
import os
import re

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", ".."))
OUT = os.path.join(ROOT, "iiko-ds-mobile", "prototypes", "recommendations")

CSS = """/* Оболочка страницы. Своих компонентов у неё нет — свои классы только для каркаса. */
html,body{margin:0;background:#f4f5f7;font-family:'Roboto','Helvetica Neue',Arial,sans-serif;color:#333}
body{padding:24px;box-sizing:border-box}
.wrap{width:100%;max-width:100%;margin:0 auto}
a{color:var(--ds-palette-accent-500)}
.crumbs{font-size:13px;line-height:18px;margin:0 0 14px}
h1{font-size:24px;line-height:32px;font-weight:500;margin:0 0 6px}
.desc{max-width:820px}
.desc{font-size:14px;line-height:20px;color:#424242;margin:0 0 10px;max-width:820px}
.cat{display:inline-flex;align-items:center;gap:8px;font-size:13px;line-height:18px;background:#fff;
     border:1px solid var(--ds-color-stroke-default);border-radius:999px;padding:4px 12px;margin:0 0 20px}
.cat b{font-weight:500}
/* Мобильную панель показываем шириной телефона (375 px), а не «половиной окна»:
   иначе «на всю ширину» элементы рисуются вдвое шире реальности (поле 725 вместо 343)
   и на глаз выглядят раздутыми. Десктопная панель занимает остаток ширины. */
.compare{display:grid;grid-template-columns:minmax(0,1fr) 375px;gap:20px;align-items:start;margin:0 0 20px}
@media (max-width:1100px){.compare{grid-template-columns:1fr}}
.panel[data-mode="mobile"]{width:375px;max-width:100%;box-sizing:border-box;border-radius:20px}
.panel[data-mode="mobile"] .panel__body{padding:12px}
.panel[data-mode="mobile"] .panel__head{padding:8px 12px}
/* Десктопная панель уже половины экрана: широкая горизонтальная раскладка
   (шесть шагов степпера и т.п.) не влезает. Прокрутка по горизонтали внутри
   панели — как в узком окне, вместо выхода за панель и наложения на соседнюю. */
.panel[data-mode="desktop"] .panel__body{overflow-x:auto}
/* Текст подсказки в ДС собран в одну строку — на телефоне он уходит за панель.
   Внутри панелей разрешаем перенос (это же требование мобильной версии). */
.panel .ds-hint-content__label,.panel .ds-hint-container__label{white-space:normal;overflow-wrap:anywhere}
@media (max-width:900px){.compare{grid-template-columns:1fr}}
.panel{background:#fff;border:1px solid var(--ds-color-stroke-default);border-radius:var(--ds-radius-3x);box-sizing:border-box}
.panel__head{display:flex;align-items:baseline;justify-content:space-between;gap:8px;
             padding:10px 16px;border-bottom:1px solid var(--ds-color-stroke-default)}
.panel__title{font-size:14px;line-height:20px;font-weight:500}
.panel__sub{font-size:12px;line-height:16px;color:#757575}
.panel__body{padding:16px}
.ex{margin:0 0 18px}
.ex:last-child{margin-bottom:0}
.ex__title{font-size:12px;line-height:16px;font-weight:500;color:#757575;margin:0 0 8px}
.ex__row{display:flex;flex-wrap:wrap;gap:8px 12px;align-items:center}
.ex__row--col{flex-direction:column;align-items:stretch}
.ex__row--col>*{width:100%}
.ex__inner{display:flex;flex-wrap:wrap;gap:8px 12px;align-items:center}
.card{background:#fff;border:1px solid var(--ds-color-stroke-default);border-radius:var(--ds-radius-3x);
      padding:16px;box-sizing:border-box;margin:0 0 16px}
h2{font-size:16px;line-height:24px;font-weight:500;margin:0 0 10px}
table{border-collapse:collapse;width:100%;font-size:13px;line-height:18px}
th,td{border:1px solid var(--ds-color-stroke-default);padding:8px 10px;text-align:left;vertical-align:top}
th{background:#fafafa;font-weight:500}
td:first-child{width:34%}
/* Колонка «Правка»: поля мобильных размеров. Значение поля применяется к
   компоненту в мобильной панели этой же страницы (см. скрипт в конце). */
td.edit{white-space:nowrap;width:1%}
.edit__input{width:64px;box-sizing:border-box;font:13px/18px 'Roboto','Helvetica Neue',Arial,sans-serif;
             color:#333;padding:4px 6px;border:1px solid var(--ds-color-stroke-default);border-radius:6px;background:#fff}
.edit__input+.edit__input{margin-left:6px}
/* Блок «На экране»: корпус телефона и экран внутри него. Экран помечен
   data-mode="mobile", поэтому в нём действуют мобильные значения и правки из
   колонки «Правка» — компонент видно в окружении интерфейса, а не в панели. */
.phone{width:375px;max-width:100%;padding:8px;box-sizing:border-box;background:#1f1f1f;border-radius:40px;
       box-shadow:0 10px 24px rgba(0,0,0,.18)}
.phones{display:flex;gap:20px;flex-wrap:wrap;align-items:flex-start}
.phones__item{display:flex;flex-direction:column;gap:10px}
.phone__caption{font-size:13px;line-height:18px;color:#757575;margin:0;max-width:375px}
.phone__screen{position:relative;display:flex;flex-direction:column;height:720px;box-sizing:border-box;overflow:hidden;
               background:#f4f5f7;border-radius:32px;font-family:'Roboto','Helvetica Neue',Arial,sans-serif}
.phone__scrim{position:absolute;left:0;right:0;top:0;bottom:0;background:rgba(0,0,0,.32)}
.phone__sheet{position:absolute;left:0;right:0;bottom:0;box-sizing:border-box;padding:16px;background:#fff;
              border-radius:16px 16px 0 0;display:flex;flex-direction:column;gap:8px}
.phone__sheet-title{margin:0;font-size:16px;line-height:24px;font-weight:500;color:#333}
.phone__sheet-text{margin:0 0 4px;font-size:14px;line-height:20px;color:#616161}
.phone__actions{display:flex;flex-direction:column;gap:8px}
.phone__actions .ds-btn{width:100%}
.phone__icons{display:flex;gap:8px}
.phone__card{background:#fff;border:1px solid var(--ds-color-stroke-default);border-radius:12px;padding:16px;box-sizing:border-box}
.phone__card-title{margin:0 0 4px;font-size:16px;line-height:24px;font-weight:500;color:#333}
.phone__card-text{margin:0;font-size:14px;line-height:20px;color:#616161}
.phone__sheet-head{display:flex;align-items:flex-start;justify-content:space-between;gap:8px}
.phone__chips{display:flex;gap:8px;flex-wrap:wrap}
/* Блок «Что говорят платформы»: три колонки, источники ссылками */
.plats{display:grid;grid-template-columns:repeat(3,minmax(0,1fr));gap:16px;margin:0 0 12px}
@media (max-width:1100px){.plats{grid-template-columns:1fr}}
.plat__title{font-size:13px;line-height:18px;font-weight:500;margin:0 0 6px}
.plat__src{font-size:12px;line-height:16px;color:#757575;word-break:break-all;margin:6px 0 0}
.plat ul.list{margin:0 0 6px}
/* «Примерные паттерны поведения»: табы — по одному на паттерн, подпись таба — название
   паттерна. Под табами один столбец: пункты, источники и пример разметкой ДС. */
/* Табы: пока влезают — стоят в строку. Если не влезают — листаются стрелками
   (стрелка слева и справа от ряда); стрелки появляются только при переполнении,
   у края соответствующая стрелка становится недоступной. Полосу прокрутки прячем. */
.pat__bar{display:flex;align-items:center;gap:8px;margin:0 0 16px}
.pat__bar .pat__tabs{margin:0}
.pat__tabs{flex:1 1 auto;min-width:0;flex-wrap:nowrap;overflow-x:auto;overflow-y:hidden;
           scrollbar-width:none}
.pat__tabs::-webkit-scrollbar{height:0}
.pat__tabs .ds-tab{flex:0 0 auto}
.pat__arrow[hidden]{display:none}
.pat__panel{display:block}
.pat__panel[hidden]{display:none}
.pat__panel .list{max-width:900px;margin:0 0 6px}
/* Пример — отдельной плашкой: серая подложка и рамка, чтобы не сливался с текстом
   паттерна. Подпись к примеру — обычным цветом текста, а не бледно-серой. */
.pat__ex{margin:16px 0 0;padding:12px 14px;background:#fafafa;border:1px solid var(--ds-color-stroke-default);border-radius:8px}
.pat__ex .ex__title{font-size:13px;line-height:18px;color:#333;margin:0 0 6px}
.pat__ex-note{font-size:13px;line-height:18px;color:#333;margin:0 0 10px;max-width:900px}
/* Примеры в табах повторяют случай из паттерна: тело экрана 375 с паддингами 16 = 343,
   узкая кнопка для длинной подписи (180 — подпись «Сохранить и отправить на кухню» уже
   не влезает в строку), пунктирная зона нажатия 48 × 48 вокруг иконки. Библиотека не
   правится — это только разметка страницы рекомендаций. */
.pat__ex .ds-btn{width:auto}
.pat__phone{width:343px;max-width:100%;display:flex;flex-direction:column;gap:8px;align-items:stretch}
.pat__phone .ds-btn{width:100%}
.pat__phone-row{flex-direction:row;align-items:center}
.pat__phone-row .ds-btn{flex:1 1 auto;width:auto;min-width:0}
.pat__narrow{max-width:180px;display:flex}
.pat__narrow .ds-btn{height:auto;min-height:44px;padding:12px 16px;white-space:normal;max-width:100%}
/* В ДС ширина задана числом — диалог 500 px, однострочный снекбар 370 px: внутри тела
   экрана 343 px они вылезали за плашку примера. В примерах ширина — по телу экрана. */
.pat__phone .ds-dialog-view,
.pat__phone .ds-dialog-header,
.pat__phone .ds-dialog-content,
.pat__phone .ds-dialog-view__action,
.pat__phone .ds-snackbar { width: 100% }
.pat__narrow .ds-btn__label{white-space:normal;line-height:20px;text-align:center}
.pat__hit{position:relative;display:inline-flex;margin:0 10px}
.pat__hit::before{content:"";position:absolute;left:50%;top:50%;width:48px;height:48px;transform:translate(-50%,-50%);border:1px dashed #9E9E9E;border-radius:8px;pointer-events:none}
details summary{cursor:pointer;font-size:13px;line-height:19px;color:#424244;margin:0 0 4px}
.phone__list{display:flex;flex-direction:column;gap:8px}
/* Строка кнопок: несколько кнопок в одну линию. Ширину берут по содержимому,
   переноса нет — если не влезают, строка прокручивается по горизонтали. */
.phone__line{display:flex;flex-wrap:nowrap;gap:4px;align-items:center;padding:8px 10px;overflow-x:auto;
             background:#fff;border-bottom:1px solid var(--ds-color-stroke-default)}
.phone__status{display:flex;align-items:center;justify-content:space-between;padding:10px 20px 4px;
               font-size:13px;line-height:16px;font-weight:500;color:#333}
.phone__ic{display:inline-flex;gap:4px}
.phone__status .material-icons{font-size:16px}
.phone__head{display:flex;align-items:center;gap:12px;padding:6px 16px 12px;background:#fff;
             border-bottom:1px solid var(--ds-color-stroke-default)}
.phone__head .material-icons{font-size:24px;color:#333}
.phone__title{flex:1;font-size:16px;line-height:24px;font-weight:500;color:#333}
.phone__body{flex:1;display:flex;flex-direction:column;gap:8px;padding:12px 16px}
.phone__row{background:#fff;border:1px solid var(--ds-color-stroke-default);border-radius:8px;
            padding:12px 14px;font-size:14px;line-height:20px;color:#333}
.phone__foot{display:flex;gap:8px;padding:12px 16px 16px;background:#fff;
             border-top:1px solid var(--ds-color-stroke-default)}
.phone__foot .ds-btn{flex:1 1 0}
p{margin:0 0 8px}
p:last-child{margin-bottom:0}
/* Панели и таблицы — на всю ширину, сплошной текст — в читаемую меру */
.point{font-size:13px;line-height:19px;color:#424242;max-width:1100px}
.list{margin:0;padding-left:20px;font-size:13px;line-height:19px;max-width:1100px}
.list li{margin:0 0 4px}
ul.list{list-style:disc}
/* Каркас оболочки: меню компонентов слева, страница компонента справа */
.kit{display:grid;grid-template-columns:260px minmax(0,1fr);gap:20px;align-items:start}
@media (max-width:900px){.kit{grid-template-columns:1fr}}
.nav{background:#fff;border:1px solid var(--ds-color-stroke-default);border-radius:var(--ds-radius-3x);
     padding:8px;box-sizing:border-box;position:sticky;top:24px}
@media (max-width:900px){.nav{position:static}}
.nav__title{font:500 12px/16px 'Roboto','Helvetica Neue',Arial,sans-serif;color:#757575;margin:0;padding:8px 10px}
.nav__item{display:block;width:100%;box-sizing:border-box;text-align:left;background:none;border:0;border-radius:8px;
           cursor:pointer;font:500 14px/20px 'Roboto','Helvetica Neue',Arial,sans-serif;color:#333;padding:8px 10px}
.nav__item+.nav__item{margin-top:2px}
.nav__item:hover{background:#f4f5f7}
.nav__item.is-active{background:#eef4ff;color:var(--ds-palette-accent-500)}
.frame{width:100%;border:0;display:block;min-height:600px;background:transparent}
/* Блок пояснений в колонке страницы ставим по сетке самой страницы компонента:
   внутри фрейма она начинается через 24 px, без этого блок шире карточек над ним
   (замер: карточки страницы 329…1870, блок 305…1894). */
.kit .card{margin:16px 24px 0}
/* ── Артефакт автогена библиотеки ──────────────────────────────
   У 23 текстовых классов в CSS ДС `background` задан тем же токеном, что и
   `color` (следы экспорта Figma: имя узла → класс, заливка текста → background).
   Из-за этого текст рисуется сплошной плашкой — чёрной или белой.
   Каркас страницы нейтрализует это внутри панелей. Сама библиотека не правится.
   ───────────────────────────────────────────────────────────── */
.panel .ds-checkbox-label__support-text,.panel .ds-chips__chip-text,.panel .ds-control-panel-2__month,.panel .ds-control-panel__month,.panel .ds-dialog-header__description,.panel .ds-elements__date,.panel .ds-hint-header__title,.panel .ds-input-number-but-icon__support-text,.panel .ds-list-item__label-down,.panel .ds-list-item__label-up,.panel .ds-list-item__text,.panel .ds-menu-item__label-down,.panel .ds-menu-item__label-up,.panel .ds-menu-item__text,.panel .ds-radio-button-label__support-text,.panel .ds-search__text,.panel .ds-select-item__label-down,.panel .ds-select-item__label-up,.panel .ds-select-item__subtitle,.panel .ds-sidenav-item__l3,.panel .ds-status__content,.panel .ds-text-ui__label-down,.panel .ds-text-ui__label-up,.panel .ds-text-ui__list-item{background:none}
/* ── Тот же автоген, но цветом: у светлого снекбара подпись белая на белом,
   у подписей сайдбара — тёмные токены на тёмной панели ДС. Внутри панелей
   приводим к читаемому виду, библиотеку не правим. ── */
.panel .ds-snackbar--light .ds-snackbar__label{color:var(--ds-color-snackbar-complex-light-text-color,#333)}
.panel .ds-sidenav-item__label,.panel .ds-sidenav-item__l3{color:var(--ds-color-text-inversive,#fff)}
/* Автоген ставит подписям white-space: nowrap — длинный текст в примерах уходит
   за карточку. Внутри панелей перенос разрешён. */
/* Автоген залил обёртку кнопки фона диалога акцентной кнопкой: вокруг каждой
   кнопки получалась синяя рамка. Внутри панелей заливку и тень снимаем. */
.panel .ds-dialog-footer__button{background:none;box-shadow:none}
/* Иконки — лигатуры Google Material Icons (шрифт подключается в шапке страницы;
   так же сделано в прототипах ДС). Слоты ДС уже центрируют содержимое —
   гасим лишнюю высоту строки, размер задаётся в разметке через font-size. */
.panel .material-icons{line-height:1;display:inline-block}
/* Автоген библиотеки не выставил box-sizing: у 44 классов с объявленной
   высотой или минимумом паддинги и рамка добавляются сверху — кадр поля 48 px
   рисуется как 74, строка списка 68 как 84. В прототипах ДС это лечат на самой
   странице (.js-select .ds-select-form__input-frame{box-sizing:border-box}),
   повторяем то же внутри панелей. Библиотека не правится — это находка для ДС. */
.panel .ds-autocomplete-form__input-frame,
.panel .ds-badge--counter,
.panel .ds-badge--point,
.panel .ds-btn--m,
.panel .ds-btn--s,
.panel .ds-btn--xs,
.panel .ds-btn-icon--m,
.panel .ds-btn-icon--s,
.panel .ds-btn-icon--xs,
.panel .ds-card__divider,
.panel .ds-chips-input-2__hint,
.panel .ds-chips-input-2__text,
.panel .ds-chips-input__hint,
.panel .ds-chips-input__text,
.panel .ds-dialog-footer__action,
.panel .ds-dialog-view__action,
.panel .ds-divider,
.panel .ds-divider-line,
.panel .ds-element-menu__image-size,
.panel .ds-element-select__image-size,
.panel .ds-element__image-size,
.panel .ds-input--m .ds-input__frame,
.panel .ds-input--s .ds-input__frame,
.panel .ds-input--xs .ds-input__frame,
.panel .ds-input-datepicker__frame,
.panel .ds-input-number__frame,
.panel .ds-input-timepicker__frame,
.panel .ds-menu-container__button-group,
.panel .ds-picture__crop,
.panel .ds-radio__state,
.panel .ds-scroll__knob,
.panel .ds-search--xs,
.panel .ds-select-container__button-group,
.panel .ds-select-form__input-frame,
.panel .ds-sidenav-header--l2.ds-sidenav-header--expanded,
.panel .ds-slide-toggle__track,
.panel .ds-slide-toggle__track::after,
.panel .ds-snackbar__progress,
.panel .ds-step--bg,
.panel .ds-step__num,
.panel .ds-tabs--lvl2 .ds-tab,
.panel .ds-textarea__hint,
.panel .ds-textarea__input-frame,
.panel .ds-textarea__text {
  box-sizing: border-box;
}

/* В ДС блок действий диалога — столбик с жёсткой высотой 68 px: две кнопки по
   44 + паддинги в него не влезают и вторая выходит за карточку. Внутри панелей
   высота отпущена (минимум — десктопные 68). */
.panel .ds-dialog-view__action,.panel .ds-dialog-footer__action{height:auto;min-height:68px}
/* Автоген библиотеки не подключил у Checkbox и Radio сами контролы: агрегатор
   iiko-ds-web/components/index.css тянет только `*-label.css`, а
   `checkbox.css` / `checkbox-icons.css` / `radio.css` / `radio-icons.css` не
   подключает никто. Без них `.ds-checkbox` остаётся `display:inline`, маркер
   20 × 20 не рисуется, а на экран выходит системный контрол браузера 13 × 13.
   На странице четыре файла подключены явно (см. head); библиотека не правится. */
/* У Button icon блок состояний стоит в библиотеке ВЫШЕ блока «Стиль × Тип» и при
   равной специфичности (0,2,0) проигрывает ему по порядку: недоступная иконка
   рисуется как активная (фон #448AFF, белая иконка). Внутри панелей возвращаем
   состояниям их токены — специфичность .panel + 2 класса. Библиотека не правится. */
.panel .ds-btn-icon:disabled,.panel .ds-btn-icon.ds-btn-icon--disabled{
  background:var(--ds-color-button-icon-disable-background-filled);
  border-color:var(--ds-color-button-icon-disable-border-color);
  color:var(--ds-color-button-icon-disable-icon-color)}
.panel .ds-btn-icon--outlined:disabled,.panel .ds-btn-icon--outlined.ds-btn-icon--disabled{
  background:var(--ds-color-button-icon-disable-background-outlined)}
.panel .ds-btn-icon--text:disabled,.panel .ds-btn-icon--text.ds-btn-icon--disabled{
  background:var(--ds-color-button-icon-disable-background-text);border-color:transparent}
/* Ещё один след автогена — min-height «по размеру нарисованного в Figma фрейма»:
   контейнер меню 418 px, селекта 406, списка 257. Контент из двух-трёх строк
   занимает 140–180 и под ним остаётся пустое поле. Внутри панелей контейнер
   снова hug (min-height:0), библиотека не правится — это находка для ДС. */
.panel .ds-menu-container,.panel .ds-select-container,.panel .ds-list-container{min-height:0}
/* Подпись-подсказка под полем объявлена высотой 16 px (--ds-size-4x), а строка
   текста в ней 19 px: три пикселя срезаются. Внутри панелей высота по контенту. */
.panel .ds-textarea__hint{height:auto}
.panel .ds-dialog-content__label,.panel .ds-dialog-view__label,.panel .ds-dialog-header__label,
.panel .ds-dialog-header__description{white-space:normal;overflow-wrap:anywhere}
"""

# Блок «На экране»: экраны в корпусе телефона лежат вне .panel, поэтому правила
# каркаса для .panel до них не доходят. Повторяем для .phone те находки, из-за
# которых компонент внутри экрана выглядит сломанным: замороженные высоты
# контейнеров (меню 418, селект 406, список 257 — контент висит в пустом поле) и
# подпись-подсказка textarea, объявленная высотой 16 px при строке 19 px.
CSS += """
/* Кнопки в шторке: пока они умещаются в строку — стоят в строку, а не в столбик.
   Переносим, если не влезают (labels у кнопок не переносятся). */
.phone__sheet .phone__actions { flex-direction: row; flex-wrap: wrap }
/* Кнопка в ДС тянется на всю ширину — в строке это ломает раскладку: даём ей
   ширину по содержимому, иначе вторая кнопка уходит на следующую строку. */
.phone__sheet .phone__actions .ds-btn { width: auto; flex: 1 1 auto; min-width: 0 }

/* Блок «На экране»: два экрана и рядом колонки «Что» и «Правка» — третья колонка
   ряда, на месте, где раньше стоял третий экран. */
.editrow { display: grid; grid-template-columns: minmax(0, 1fr) 380px; gap: 20px; align-items: start }
@media (max-width: 1250px) { .editrow { grid-template-columns: 1fr } }
.edits table { width: 100% }
.edits td:first-child { width: 62% }
.edits .point { margin-top: 10px; max-width: 380px }

.phone .ds-menu-container,
.phone .ds-select-container,
.phone .ds-list-container { min-height: 0 }
.phone .ds-textarea__hint { height: auto }
/* Подсказка ДС собрана в одну строку (nowrap) — внутри экрана она вылезает за
   корпус. То же правило, что для панелей: разрешаем перенос. */
.phone .ds-hint-content__label,
.phone .ds-hint-container__label { white-space: normal; overflow-wrap: anywhere }
"""

_plates = [ln for ln in CSS.split("\n") if ln.startswith(".panel .ds-checkbox-label__support-text")]
if _plates:
    CSS = CSS.replace(_plates[0], _plates[0] + "\n" + _plates[0].replace(".panel ", ".phone "), 1)

# Примеры в табах стоят в колонке паттерна (.pat__panel), а не в .panel или .phone,
# поэтому правила каркаса до них не доходили: текст рисовался сплошной плашкой
# (артефакт автогена — `background` тем же токеном, что `color`), контейнеры меню,
# селекта и списка висели в пустом поле со своей замороженной высотой, а подписи
# светлого снекбара и сайдбара сливались с фоном. Повторяем для .pat__panel те же
# правила каркаса — они накрывают пример при любой обёртке внутри примера.
# Библиотека не правится.
_panel_rules = re.findall(r"(?m)^\.panel [^{]*\{[^}]*\}", CSS)
for _rule in _panel_rules:
    CSS += _rule.replace(".panel ", ".pat__panel ") + "\n"




def preview_card(d):
    """Блок «На экране»: два экрана одного интерфейса + колонки «Что» и «Правка».

    Второй экран помечается `data-preview="edit"` — в него пишутся правки из полей;
    первый остаётся со значениями как рекомендовано, чтобы их можно было сравнить."""
    html = d.get("preview_html")
    if not html:
        return ""
    marker = 'data-mode="mobile">'
    i = html.find(marker)
    j = html.find(marker, i + 1)
    marked = html
    if j != -1:
        marked = html[:j] + 'data-mode="mobile" data-preview="edit">' + html[j + len(marker):]
    panel = edits_panel(d)
    body = ('<div class="editrow"><div>%s</div>%s</div>' % (marked, panel)) if panel else marked
    return '<div class="card">\n    <h2>На экране</h2>\n    %s\n  </div>' % body


def platforms_card(d):
    """Блок «Примерные паттерны поведения»: табы — по одному на паттерн.

    Если у компонента есть `patterns_ru`, каждый паттерн становится табом: подпись
    таба — название паттерна, под табами — три пункта, строка «Источники: …» и, если
    он задан, пример разметкой ДС (`example_html`; `example_ru` — подпись к примеру).
    Если паттернов нет, табами становится прежний текст (`platform_notes_ru` плюс
    колонка «Логика»), чтобы блок не пропадал. Разметка примеров вставляется как есть —
    это штатные классы ДС, библиотека не правится.
    """
    groups = list(d.get("patterns_ru") or [])
    if not groups:
        groups = list(d.get("platform_notes_ru") or [])
        if d.get("logic_ru"):
            groups.append({"title": "Логика (от себя, без источника)", "items": d["logic_ru"]})
    if not groups:
        return ""
    slug = d.get("slug") or "c"
    tabs, panels = [], []
    for i, g in enumerate(groups):
        pid = "pat-%s-%d" % (slug, i)
        tabs.append('<button class="ds-tab%s" type="button" role="tab" data-pat="%s">%s</button>'
                    % (" ds-tab--active" if i == 0 else "", pid, esc(g.get("title", ""))))
        items = "".join("<li>%s</li>" % esc(x) for x in (g.get("items") or []))
        src = g.get("src")
        src_html = ('<p class="plat__src">%s</p>' % esc(src)) if src else ""
        ex_html = ""
        if g.get("example_html"):
            note = ('<p class="pat__ex-note">%s</p>' % esc(g["example_ru"])) if g.get("example_ru") else ""
            ex_html = ('<div class="ex pat__ex"><p class="ex__title">Пример</p>%s'
                       '<div class="ex__row"><div class="ex__inner">%s</div></div></div>'
                       % (note, g["example_html"]))
        panels.append('<div class="pat__panel" data-pat-panel="%s"%s>'
                      '<ul class="list">%s</ul>%s%s</div>'
                      % (pid, "" if i == 0 else " hidden", items, src_html, ex_html))
    arrow = ('<button class="ds-btn-icon ds-btn-icon--m ds-btn-icon--neutral ds-btn-icon--text pat__arrow'
             ' pat__arrow--%s" type="button" aria-label="%s" hidden>'
             '<span class="ds-btn-icon__icon"><span class="material-icons" style="font-size:24px">%s</span></span></button>')
    return ('<div class="card">\n    <h2>Примерные паттерны поведения</h2>\n'
            '    <div class="pat__bar">%s'
            '<div class="ds-tabs ds-tabs--lvl2 pat__tabs" role="tablist">%s</div>%s</div>\n'
            '    <div class="pat__body">%s</div>\n  </div>'
            % (arrow % ("left", "Предыдущие паттерны", "chevron_left"), "".join(tabs),
               arrow % ("right", "Следующие паттерны", "chevron_right"), "".join(panels)))


def found_card(d):
    """Карточка «Найдено в ДС» — то, что режим не решает и мы не правим в библиотеке."""
    html = d.get("found_html")
    if not html:
        return ""
    return '<div class="card">\n  <h2>Найдено в ДС (в библиотеке не правим)</h2>\n  %s\n</div>' % html


def esc(value):
    return html.escape(str(value))


# ── Версия сборки ─────────────────────────────────────────────
# Браузер кэширует CSS по адресу. Если правится DС или modes.css, страница без
# параметра версии может отрисоваться старым файлом — ровно так «мобильное
# поле» выглядело десктопным. Поэтому в ссылки на CSS и в iframe оболочки
# подставляется `?v=<максимальный mtime CSS>`, и правка любого файла ломает кэш.
def build_version():
    newest = 0.0
    for root in (os.path.join(HERE, "..", "..", "iiko-ds-web"), os.path.join(HERE, "..", "..", "iiko-ds-mobile")):
        for dirpath, dirnames, filenames in os.walk(root):
            for f in filenames:
                if f.endswith(".css"):
                    newest = max(newest, os.path.getmtime(os.path.join(dirpath, f)))
    for f in os.listdir(HERE):
        if f.endswith(".css"):
            newest = max(newest, os.path.getmtime(os.path.join(HERE, f)))
    return str(int(newest))


VER = build_version()

def panel(side, d):
    """side: 'desktop' | 'mobile'."""
    mode = side
    title = "Desktop" if side == "desktop" else "Mobile"
    sub = esc(d["panels"][side]["sub_ru"])
    body = []
    for ex in d["examples"]:
        markup = ex.get("html_mobile") if (side == "mobile" and ex.get("html_mobile")) else ex["html"]
        row_cls = "ex__row ex__row--col" if ex.get("stack") else "ex__row"
        # Пример оборачивается в нейтральный контейнер: правило каркаса
        # `.ex__row--col > * { width: 100% }` иначе перебивало собственную ширину
        # компонента (например, панель меню 240 px), и на странице десктоп
        # выглядел как мобила. Теперь каркас растягивает обёртку, а компонент
        # внутри сохраняет свою ширину и мобильные правила работают по нему.
        body.append(
            '<div class="ex"><p class="ex__title">%s</p><div class="%s"><div class="ex__inner">%s</div></div></div>'
            % (esc(ex["title_ru"]), row_cls, markup)
        )
    return (
        '<div class="panel" data-mode="%s"><div class="panel__head"><span class="panel__title">%s</span>'
        '<span class="panel__sub">%s</span></div><div class="panel__body">%s</div></div>'
        % (mode, title, sub, "".join(body))
    )


def edits_of(c):
    """Поля правки строки — тем же тегом, что и на странице."""
    cells = []
    for e in c.get("edit") or []:
        sync = e.get("sync")
        sync_attrs = ""
        if sync:
            sync_attrs = ' data-sync-field="%s" data-sync-a="%s" data-sync-b="%s"' % (
                esc(sync["field"]), sync["a"], sync["b"])
        cells.append('<input class="edit__input" type="number" step="1" value="%s" '
                     'data-id="%s" data-sel="%s" data-css="%s"%s aria-label="%s">'
                     % (e["v"], esc(e.get("id", "")), esc(e["sel"]), esc(e["css"]),
                        sync_attrs, esc(c["what"])))
    return "".join(cells)


def changes_table(d):
    """Колонка Mobile — рекомендованное значение: источник, не правится.
    Поля правки стоят не здесь, а в блоке «На экране» — рядом с экранами."""
    body = []
    for c in d["changes"]:
        body.append("<tr><td>%s</td><td>%s</td><td>%s</td></tr>"
                    % (esc(c["what"]), esc(c["desktop"]), esc(c["mobile"])))
    head = "<table><tr><th>Что</th><th>Desktop</th><th>Mobile</th></tr>"
    return head + "".join(body) + "</table>"


def edits_panel(d):
    """Две колонки рядом с экранами: «Что» — строка таблицы, «Правка» — её поля.
    Правка применяется только ко второму экрану: первый показывает значения
    как рекомендовано, второй — то, что введено руками."""
    rows = []
    for c in d["changes"]:
        inputs = edits_of(c)
        if not inputs:
            continue
        rows.append('<tr><td>%s</td><td class="edit">%s</td></tr>' % (esc(c["what"]), inputs))
    if not rows:
        return ""
    return ('<div class="edits"><table><tr><th>Что</th><th>Правка</th></tr>%s</table>'
            '<p class="point">Правка применяется к правому экрану. Левый — значения '
            'как рекомендовано.</p></div>' % "".join(rows))


def page(d):
    style_link = "".join(
        '<a href="%s">%s</a>' % (esc(u), esc(u.split("/")[2])) for u in d.get("why_sources", [])
    )
    why_link = (" <span class=\"panel__sub\">(%s)</span>" % style_link) if style_link else ""
    return ("""<!DOCTYPE html>
<html lang="ru">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>%(component)s — Desktop и Mobile</title>
<link rel="stylesheet" href="../../../iiko-ds-web/font.css?v=%(ver)s">
<link rel="stylesheet" href="../../../iiko-ds-web/tokens.css?v=%(ver)s">
<link rel="stylesheet" href="../../modes.css?v=%(ver)s">
<link rel="stylesheet" href="../../components/index.css?v=%(ver)s">
<link rel="stylesheet" href="../../../iiko-ds-web/styles.css?v=%(ver)s">
<link rel="stylesheet" href="../../../iiko-ds-web/components/index.css?v=%(ver)s">
<!-- Автоген не подключил эти четыре файла в агрегаторе библиотеки — без них
     Checkbox и Radio рисуются системным контролом браузера (13 × 13 вместо
     маркера 20 × 20). Подключаем их явно на странице; библиотека не правится. -->
<link rel="stylesheet" href="../../../iiko-ds-web/components/Checkbox_DS/checkbox.css?v=%(ver)s">
<link rel="stylesheet" href="../../../iiko-ds-web/components/Checkbox_DS/checkbox-icons.css?v=%(ver)s">
<link rel="stylesheet" href="../../../iiko-ds-web/components/Radio-Button_DS/radio.css?v=%(ver)s">
<link rel="stylesheet" href="../../../iiko-ds-web/components/Radio-Button_DS/radio-icons.css?v=%(ver)s">
<link rel="stylesheet" href="rec.css?v=%(ver)s">
<style id="live"></style>   <!-- сюда попадают правки из колонки «Правка» -->
<link rel="stylesheet" href="https://fonts.googleapis.com/icon?family=Material+Icons">
</head>
<body>
<div class="wrap">
  <p class="crumbs"><a href="index.html#%(slug)s">← Все компоненты</a></p>
  <h1>%(component)s</h1>
  <p class="desc">%(desc)s</p>
  <p class="cat"><b>%(cat)s</b> · %(cat_note)s</p>

  <div class="compare">
%(desktop_panel)s
%(mobile_panel)s
  </div>

%(preview)s

%(platforms)s

  <div class="card">
    <h2>Что меняется на мобиле</h2>
    %(changes)s
    %(behaviour)s
  </div>

  <div class="card">
    <h2>Почему так</h2>
    <p class="point">%(why)s%(why_link)s</p>
  </div>

  <div class="card">
    <h2>Итог</h2>
    %(result)s
  </div>
%(found)s
</div>
<script>
/* Поля «Правка»: введённое число применяется к компоненту во ВТОРОМ экране блока
   «На экране» (он помечен data-preview="edit"); первый экран остаётся со
   значениями как рекомендовано — их и сравниваем. Правило пишется в
   <style id="live">, поэтому работает и для псевдоэлементов (тач-зона).
   В шаблоне поля «@» заменяется на введённое число. Пока поле не тронуто,
   правило не пишется — экраны остаются как есть. */
(function () {
  var live = document.getElementById('live');
  var fields = [].slice.call(document.querySelectorAll('.edit__input'));
  if (!live || !fields.length) return;
  var byId = {};
  fields.forEach(function (f) { if (f.getAttribute('data-id')) byId[f.getAttribute('data-id')] = f; });
  function rebuild() {
    var rules = [];
    fields.forEach(function (f) {
      if (!f.__touched) return;
      var v = f.value === '' ? f.getAttribute('value') : f.value;
      rules.push('[data-mode="mobile"][data-preview="edit"].phone__screen ' + f.getAttribute('data-sel') +
                 '{' + f.getAttribute('data-css').split('@').join(v) + '}');
    });
    live.textContent = rules.join(String.fromCharCode(10));
  }
  /* Связанное значение пересчитывается по линейной формуле t = a * v + b
     (например высота 40 → паддинг 0.5 * 40 - 10 = 10) и сразу видно в поле. */
  function syncFields(f) {
    var target = f.getAttribute('data-sync-field');
    if (!target || !byId[target]) return;
    var a = parseFloat(f.getAttribute('data-sync-a'));
    var b = parseFloat(f.getAttribute('data-sync-b'));
    var v = parseFloat(f.value);
    if (isNaN(a) || isNaN(v)) return;
    var t = byId[target];
    t.value = Math.round((a * v + b) * 100) / 100;
    t.__touched = true;
  }
  fields.forEach(function (f) {
    f.addEventListener('input', function () {
      f.__touched = true;
      syncFields(f);
      rebuild();
    });
  });
})();
/* Табы блока «Примерные паттерны поведения»: показывается паттерн выбранного таба,
   остальные скрыты. Своих компонентов не заводим — только переключение видимости
   готовых блоков, поэтому на странице видно ровно тот случай, что назван в табе. */
(function () {
  var bars = [].slice.call(document.querySelectorAll('.pat__tabs'));
  bars.forEach(function (bar) {
    var tabs = [].slice.call(bar.querySelectorAll('.ds-tab'));
    var panels = [].slice.call(document.querySelectorAll('.pat__panel'));
    tabs.forEach(function (t) {
      t.addEventListener('click', function () {
        tabs.forEach(function (o) { o.classList.toggle('ds-tab--active', o === t); });
        panels.forEach(function (p) {
          p.hidden = p.getAttribute('data-pat-panel') !== t.getAttribute('data-pat');
        });
      });
    });
  });
})();
/* Стрелки у ряда табов: ряд листается на шесть десятых его ширины (но не меньше
   160 px). Стрелки видны только когда табы не влезают, и та из них, в сторону которой
   листать нечего, становится недоступной — видно, что список кончился. */
(function () {
  [].slice.call(document.querySelectorAll('.pat__bar')).forEach(function (bar) {
    var row = bar.querySelector('.pat__tabs');
    var left = bar.querySelector('.pat__arrow--left');
    var right = bar.querySelector('.pat__arrow--right');
    if (!row || !left || !right) return;
    function step() { return Math.max(160, Math.round(row.clientWidth * 0.6)); }
    function sync() {
      var rest = row.scrollWidth - row.clientWidth;
      var over = rest > 1;
      left.hidden = right.hidden = !over;
      if (!over) return;
      left.disabled = row.scrollLeft <= 1;
      right.disabled = row.scrollLeft >= rest - 1;
    }
    left.addEventListener('click', function () { row.scrollLeft -= step(); setTimeout(sync, 260); });
    right.addEventListener('click', function () { row.scrollLeft += step(); setTimeout(sync, 260); });
    row.addEventListener('scroll', sync);
    window.addEventListener('resize', sync);
    setTimeout(sync, 50);
  });
})();
</script>
</body>
</html>
""" % {
        "component": esc(d["component"]),
        "slug": esc(d["slug"]),
        "desc": esc(d["desc_ru"]),
        "cat": esc(d["category_ru"]),
        "cat_note": esc(d["category_note_ru"]),
        "desktop_panel": panel("desktop", d),
        "mobile_panel": panel("mobile", d),
        "changes": changes_table(d),
        "behaviour": d.get("behaviour_html", ""),
        "platforms": platforms_card(d),
        "preview": preview_card(d),
        # как и *_html: в данных есть <code> и <b>, при esc() они рисовались текстом
        "why": d["why_ru"],
        "why_link": why_link,
        "result": d["result_html"],
        "found": found_card(d),
        "ver": VER,
    })


def index_page(all_data):
    """Оболочка: слева меню компонентов, справа страница выбранного компонента."""
    items = "".join(
        '<button class="nav__item" type="button" data-slug="%s">%s</button>'
        % (esc(d["slug"]), esc(d["component"]))
        for d in all_data
    )
    return """<!DOCTYPE html>
<html lang="ru">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Компоненты: Desktop → Mobile</title>
<link rel="stylesheet" href="../../../iiko-ds-web/font.css?v=%(ver)s">
<link rel="stylesheet" href="../../../iiko-ds-web/tokens.css?v=%(ver)s">
<link rel="stylesheet" href="../../modes.css?v=%(ver)s">
<link rel="stylesheet" href="../../../iiko-ds-web/components/index.css?v=%(ver)s">
<link rel="stylesheet" href="rec.css?v=%(ver)s">
</head>
<body>
<div class="wrap">
  <h1>Компоненты: Desktop → Mobile</h1>
  <div class="kit">
    <nav class="nav" aria-label="Компоненты">
      <p class="nav__title">Компоненты · %(count)d</p>
      %(items)s
    </nav>
    <div>
      <iframe class="frame" id="frame" title="Страница компонента"></iframe>
        <div class="card">
        <h2>Общее для всех компонентов</h2>
        <p class="point">Что меняется у каждого компонента на мобиле и почему. Выберите компонент в меню слева —
        страница откроется справа, десктоп и мобила стоят рядом (в Figma так нельзя: режим там глобальный на файл).</p>
        <p class="point"><b>Про следы автогена в CSS библиотеки.</b> У части текстовых классов <code>background</code> задан тем же
        токеном, что и <code>color</code> — текст рисуется сплошной плашкой; у подписей стоит <code>white-space: nowrap</code>;
        обёртка кнопки диалога залита акцентным цветом кнопки; у светлого снекбара подпись белая на белом фоне; подписи сайдбара
        тёмные на тёмной панели. Внутри панелей каркас страницы это нейтрализует и описывает в карточке «Найдено в ДС» на каждой
        затронутой странице. Сама библиотека не правится — перечисленное отдаётся владельцу ДС как находки.</p>
        <p class="point"><b>Про box-sizing.</b> Ни у одного класса библиотеки с объявленной высотой нет <code>box-sizing: border-box</code> —
        паддинги и рамка прибавляются сверху, и кадр поля 48 px рисуется как 74, строка списка 68 — как 84. В самих прототипах ДС
        это лечат на странице (<code>.js-select .ds-select-form__input-frame{box-sizing:border-box;height:48px}</code>); в каркасе
        повторено то же для 44 классов библиотеки и 53 правил мобильного слоя. Библиотека не правится.</p>
        <p class="point"><b>Про иконки.</b> Иконки на страницах — лигатуры шрифта <code>Material Icons</code>
        (<code>&lt;span class="material-icons"&gt;имя&lt;/span&gt;</code>, размер через <code>font-size</code> слота ДС), как в прототипах ДС.
        Шрифт подключается в шапке страницы с Google Fonts; своих SVG-заглушек в примерах нет.</p>
        <p class="point"><b>Про Checkbox и Radio.</b> Агрегатор библиотеки <code>iiko-ds-web/components/index.css</code> подключает у них только
        <code>*-label.css</code>, а сами контролы — <code>checkbox.css</code>, <code>checkbox-icons.css</code>, <code>radio.css</code>,
        <code>radio-icons.css</code> — не подключает никто. Без них на экран выходит системный контрол браузера 13 × 13 вместо маркера ДС
        20 × 20 и без цветов состояний. На странице четыре файла подключены явно (библиотека не правится) — это находка для ДС.</p>
        <p class="point"><b>Про min-height и состояния Button icon.</b> Ещё два следа автогена в библиотеке: у контейнеров <code>min-height</code>
        взят по размеру нарисованного в Figma фрейма (меню 418 px, селект 406, список 257 — под контентом остаётся пустое поле), а у Button icon
        блок состояний стоит <b>выше</b> блока «Стиль × Тип» и при равной специфичности проигрывает ему — недоступная иконка рисуется как активная
        (фон <code>#448AFF</code>, белая иконка). Внутри панелей каркас это нейтрализует, библиотека не правится.</p>
      </div>
    </div>
  </div>
</div>
<script>
var VER = '%(ver)s';
var frame = document.getElementById('frame');
var items = Array.prototype.slice.call(document.querySelectorAll('.nav__item'));

function fit() {
  try {
    var d = frame.contentDocument;
    if (!d) return;
    if (!d.getElementById('embedded-fix')) {
      var st = d.createElement('style');
      st.id = 'embedded-fix';
      st.textContent = '.crumbs{display:none}html,body{overflow:hidden}';   /* ссылка «Все компоненты» внутри оболочки не нужна;
                                                             прокрутка тоже: фрейм обрезан по последнему блоку */
      d.head.appendChild(st);
    }
    /* Высоту фрейма обрезаем по низу последнего блока страницы, а не по
       scrollHeight: у той страницы снизу свои 24 px padding и 16 px отступ
       последней карточки, и они прибавлялись к отступу блока пояснений
       (получалось 57 px вместо 16 px — как между блоками на самой странице).
       Заодно у body своя высота по содержимому (у documentElement
       scrollHeight «залипает» на высоте фрейма и не уменьшается). */
    var wrap = d.querySelector('.wrap');
    var last = wrap ? wrap.lastElementChild : null;
    var bottom = last ? last.getBoundingClientRect().bottom + (d.documentElement.scrollTop || 0)
                      : (d.body ? d.body.scrollHeight : d.documentElement.scrollHeight);
    frame.style.height = Math.max(Math.ceil(bottom), 600) + 'px';
  } catch (e) { /* другой origin — оставляем min-height из CSS */ }
}

function activate(slug, updateHash) {
  var current = items.filter(function (i) { return i.getAttribute('data-slug') === slug; })[0] || items[0];
  if (!current) return;
  slug = current.getAttribute('data-slug');
  items.forEach(function (i) { i.className = (i === current) ? 'nav__item is-active' : 'nav__item'; });
  if (frame.getAttribute('src') !== slug + '.html?v=' + VER) frame.setAttribute('src', slug + '.html?v=' + VER);
  if (updateHash !== false) {
    try { history.replaceState(null, '', '#' + slug); } catch (e) { location.hash = slug; }
  }
}

// Высота фрейма пересчитывается не только на load: к моменту load шрифты
// Google (Roboto и Material Icons) ещё не пришли, поэтому на части страниц
// высота оставалась «старой» и под блоком пояснений вырастал лишний отступ.
// Замер до правки: 57 px на 35 страницах, 76 на dialog и 93 на sidenav —
// то есть отступ до блока зависел от того, какой компонент выбран в меню.
// Теперь высота считается снова после загрузки шрифтов и при каждом
// изменении размера содержимого страницы.
function watch() {
  try {
    var d = frame.contentDocument;
    if (!d || !d.body) return;
    if (d.fonts && d.fonts.ready) d.fonts.ready.then(fit);
    setTimeout(fit, 300);
    if (window.ResizeObserver) {
      if (frame.__ro) { try { frame.__ro.disconnect(); } catch (e) {} }
      frame.__ro = new ResizeObserver(fit);
      frame.__ro.observe(d.body);
    }
  } catch (e) { /* другой origin — высота остаётся из CSS */ }
}

frame.addEventListener('load', function () { fit(); watch(); });
window.addEventListener('resize', fit);
window.addEventListener('hashchange', function () { activate((location.hash || '').replace('#', ''), false); });
items.forEach(function (i) {
  i.addEventListener('click', function () {
    activate(i.getAttribute('data-slug'));
    window.scrollTo(0, 0);
  });
});
activate((location.hash || '').replace('#', '') || items[0].getAttribute('data-slug'), false);
</script>
</body>
</html>
""" % {"items": items, "count": len(all_data), "ver": VER}


def main():
    os.makedirs(OUT, exist_ok=True)
    with open(os.path.join(OUT, "rec.css"), "w", encoding="utf-8", newline="\n") as f:
        f.write(CSS)
    js = os.path.join(OUT, "rec.js")
    if os.path.exists(js):
        os.remove(js)
    data = []
    for path in sorted(glob.glob(os.path.join(HERE, "data", "*.json"))):
        with open(path, encoding="utf-8") as f:
            data.append(json.load(f))
    data.sort(key=lambda d: d["component"].lower())
    for d in data:
        with open(os.path.join(OUT, d["slug"] + ".html"), "w", encoding="utf-8", newline="\n") as f:
            f.write(page(d))
        print("page:", d["slug"] + ".html")
    with open(os.path.join(OUT, "index.html"), "w", encoding="utf-8", newline="\n") as f:
        f.write(index_page(data))
    print("index.html, components:", len(data))


if __name__ == "__main__":
    main()
