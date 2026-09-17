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
.phones{display:flex;gap:32px;flex-wrap:wrap;align-items:flex-start}
.phones__item{display:flex;flex-direction:column;gap:10px}
.phone__caption{font-size:13px;line-height:18px;color:#757575;margin:0;max-width:375px}
.phone__screen{position:relative;display:flex;flex-direction:column;height:720px;box-sizing:border-box;overflow:hidden;
               background:#f4f5f7;border-radius:32px;font-family:'Roboto','Helvetica Neue',Arial,sans-serif}
/* Затемнение экрана под шторкой — компонент ДС .ds-backdrop (цвет из токена),
   прозрачность 32 % — значение платформ (MD3 scrim / Angular rgba(0,0,0,.32)). */
.phone__scrim{position:absolute;left:0;right:0;top:0;bottom:0;
              background:var(--ds-color-backdrop-background,#333333);opacity:.32}
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
/* Кнопки в строке заполняют её поровну — как группа в мобильном ДС
   (Button_DS/button-group-mob.css: flex 1 1 0). Иконка-кнопка в строке остаётся
   своего размера: правило накрывает только .ds-btn. */
.pat__phone-row .ds-btn{flex:1 1 0;width:auto;min-width:0}
/* Пример «длинная подпись»: кнопка на всю ширину строки, подпись переносится.
   В ДС подпись заперта в одну строку (white-space:nowrap у .ds-btn__label) — в примере
   показываем рекомендованное поведение: перенос вместо усечения. Ширина — та же строка,
   что у остальных кнопок экрана (343 px), отдельного узкого контейнера здесь нет. */
/* Спиннер в примере «Загрузка вместо двойного нажатия»: в ДС состояния загрузки
   нет, поэтому вращение — правило каркаса страницы (иконка — Material Icons). */
@keyframes pat-spin{to{transform:rotate(360deg)}}
.pat__spin{animation:pat-spin .9s linear infinite}
/* Клавиатура в примере «Кнопка ушла под клавиатуру» — элемент системы, не ДС. */
.pat__keyboard{background:#e8eaef;border-radius:8px;padding:6px;display:flex;flex-direction:column;gap:4px}
.pat__keyboard-row{display:flex;gap:4px}
.pat__key{flex:1 1 0;height:22px;background:#fff;border-radius:4px}
.pat__wrap{width:100%;display:flex}
.pat__wrap .ds-btn{width:100%;height:auto;min-height:44px;padding:12px 16px;white-space:normal}
.pat__wrap .ds-btn__label{white-space:normal;line-height:20px;text-align:center;max-width:100%}
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
/* Кружок, имитирующий тач: на мобиле показываем касание пальцем, а не курсор мыши.
   44 px — усреднённый размер подушечки пальца; он же минимум хит-региона у Apple HIG
   («at least 44x44 pt»). Кружок рисуется ПОВЕРХ кнопки (z-index 2), иначе его не видно:
   на мобиле все размеры кнопки — 44 px высоты (Button_DS/button-touch.css).
   Невидимая зона нажатия 48 px остаётся слоем CSS, кружок — только показ. */
.pat__hit{position:relative;display:inline-flex;margin:0 10px}
.pat__hit::before{content:"";position:absolute;left:50%;top:50%;width:44px;height:44px;
                  transform:translate(-50%,-50%);border-radius:50%;pointer-events:none;z-index:2;
                  background:color-mix(in srgb,var(--ds-palette-accent-500,#448AFF) 22%,transparent)}
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
/* Строки внутри макета экрана (у блока нет ДС-компонента — это каркас страницы). */
.phone__kv{display:flex;align-items:center;gap:8px;font-size:14px;line-height:20px;
           color:var(--ds-color-text-ui-text-color,#333)}
.phone__kv .material-icons{color:var(--ds-color-text-secondary,#616161)}
.phone__kv-label{color:var(--ds-color-text-secondary,#616161);white-space:nowrap}
.phone__kv-value{color:var(--ds-color-text-ui-text-color,#333)}
.phone__sep{display:flex;align-items:center;gap:16px;font-size:12px;line-height:16px;
            color:var(--ds-color-text-secondary,#616161)}
.phone__sep .material-icons{color:var(--ds-color-text-secondary,#616161)}
.phone__filter{display:flex;align-items:center;justify-content:space-between;gap:12px}
/* В макете заказа поиск — круглая кнопка у правого края, поэтому мобильную укладку
   поиска «на всю ширину» (iiko-ds-mobile/components/Search_DS) здесь снимаем:
   размер берём компонентный — XS, 36 px (--ds-size-9x). */
.phone__filter .ds-search--xs{width:var(--ds-size-9x);min-width:var(--ds-size-9x);flex:0 0 auto}
.phone__filter .ds-checkbox{flex:0 0 auto}
.phone__filter .ds-checkbox__label{white-space:nowrap}
.phone__card--item{display:flex;align-items:center;gap:8px;padding:12px 16px}
.phone__card-body{flex:1;min-width:0}
.phone__grabber{width:40px;height:4px;border-radius:2px;background:var(--ds-color-stroke-default);margin:0 auto 8px}
/* Поле ввода в макете идёт по ширине тела экрана: в ДС ширина задана числом
   (.ds-textarea 250 px), а сам <textarea> в библиотеке не оформлен — рисуется
   браузерной рамкой и шириной по cols. Библиотеку не правим, гасим в макете. */
.phone__screen .ds-textarea{width:100%}
/* В ДС у блока содержимого нет flex — он сжимается по содержимому поля, а поле
   без оформления тянет браузерную ширину по cols (≈175 px). В макете растягиваем. */
.phone__screen .ds-textarea__input-content{flex:1 1 auto;min-width:0}
.phone__screen .ds-textarea__field{width:100%;box-sizing:border-box;border:0;background:none;
                                   padding:0;font:inherit;color:inherit}
/* Имитация касания вместо курсора мыши внутри мобильного экрана: сам курсор скрыт,
   за указателем идёт кружок 44 px (средняя подушечка пальца, он же минимум хит-региона
   Apple HIG 44×44 pt); при нажатии кружок плотнее. Только для мыши — на тач-устройстве
   кружок не нужен и не включается (та же проверка в скрипте страницы). */
@media (hover:hover) and (pointer:fine){
  .phone__screen,.phone__screen *{cursor:none}
}
.phone__touch{position:absolute;left:0;top:0;width:44px;height:44px;border-radius:50%;
              transform:translate(-50%,-50%);pointer-events:none;z-index:9;display:none;
              background:color-mix(in srgb,var(--ds-palette-accent-500,#448AFF) 22%,transparent)}
.phone__touch--press{background:color-mix(in srgb,var(--ds-palette-accent-500,#448AFF) 38%,transparent)}
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
.nav__item{display:flex;align-items:center;gap:8px;justify-content:space-between;width:100%;box-sizing:border-box;
           text-align:left;background:none;border:0;border-radius:8px;
           cursor:pointer;font:500 14px/20px 'Roboto','Helvetica Neue',Arial,sans-serif;color:#333;padding:8px 10px}
.nav__name{overflow:hidden;text-overflow:ellipsis;white-space:nowrap}
.nav__badge{display:flex;align-items:center;gap:5px;flex:0 0 auto;font:500 11px/14px 'Roboto','Helvetica Neue',Arial,sans-serif;color:#8b95a1}
.nav__badge .material-icons{font-size:13px;line-height:1}
.nav__badge .is-ok{display:flex;align-items:center;gap:2px;color:#0f852c}
.nav__badge .is-later{display:flex;align-items:center;gap:2px;color:#a35b00}
.nav__badge .is-no{display:flex;align-items:center;gap:2px;color:#c62828}
.nav__item.is-done .nav__name{color:#8b95a1}
.nav--pending .nav__item.is-done:not(.is-active){display:none}
.review__filter{display:flex;align-items:center;gap:6px;margin:8px 0 0;cursor:pointer;
  font:400 12px/16px 'Roboto','Helvetica Neue',Arial,sans-serif;color:#5b6d7f}
.review__ds{margin:6px 0 0;font:400 12px/16px 'Roboto','Helvetica Neue',Arial,sans-serif;color:#5b6d7f}
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

/* Блок «На экране»: слева меню паттернов, справа два одинаковых экрана, под ними —
   текст выбранного паттерна. Меню листается, если список выше экранов, и не тянет
   за собой блок. */
.screens{display:grid;grid-template-columns:360px minmax(0,1fr);gap:20px;align-items:start}
@media (max-width:1250px){.screens{grid-template-columns:1fr}}
.screens__menu{display:flex;flex-direction:column;gap:2px;box-sizing:border-box;padding:8px;
               max-height:780px;overflow-y:auto;background:#fff;
               border:1px solid var(--ds-color-stroke-default);border-radius:var(--ds-radius-3x)}
.screens__item{display:block;width:100%;box-sizing:border-box;text-align:left;background:none;border:0;
               border-radius:8px;cursor:pointer;
               font:500 14px/20px 'Roboto','Helvetica Neue',Arial,sans-serif;color:#333;padding:8px 10px}
.screens__item+.screens__item{margin-top:2px}
.screens__item:hover{background:#f4f5f7}
.screens__item--active{background:#eef4ff;color:var(--ds-palette-accent-500)}
/* Текст паттерна под экранами — отдельной плашкой: фон и рамка отличают его от
   остального текста страницы (раньше он читался как обычный абзац и терялся). */
.screens__note{margin:16px 0 0;padding:16px;box-sizing:border-box;
                background:var(--ds-color-shapes-default-variant,#f8f9fc);
                border:1px solid var(--ds-color-stroke-default);border-radius:var(--ds-radius-3x,12px)}
/* Заголовок паттерна над его текстом: под экранами видно, какой пункт меню открыт. */
.screens__note-title{margin:0 0 6px;font-size:16px;line-height:24px;font-weight:500;
                     color:var(--ds-color-text-ui-text-color,#333)}
/* ── Ревью страниц рекомендаций ───────────────────────────────────────────
   Тот же механизм, что в KDS (iiko-ds-prototypes/KDS/ux-proposals.html): три статуса,
   свой комментарий, отметки в меню, «просмотрено», строка прогресса, отчёт xls и
   JSON скачать/загрузить. Отличие — светлая тема страницы и хранение в localStorage
   с ключом по компоненту. ── */
.screens__note-head{display:flex;align-items:flex-start;justify-content:space-between;gap:16px}
.review__row{display:flex;flex-wrap:wrap;gap:8px;align-items:center;justify-content:flex-end}
.review__btn{
  font:500 13px/18px 'Roboto','Helvetica Neue',Arial,sans-serif;padding:6px 10px;border-radius:8px;cursor:pointer;
  border:1px solid var(--ds-color-stroke-default);background:#fff;color:#333;
  display:inline-flex;align-items:center;gap:6px}
.review__btn .material-icons{font-size:16px;line-height:1}
.review__btn:hover{background:#f4f5f7}
.review__btn.is-on[data-st="accepted"]{background:#e7f5eb;border-color:#0f852c;color:#0f852c}
.review__btn.is-on[data-st="later"]{background:#fff4e5;border-color:#ea7806;color:#a35b00}
.review__btn.is-on[data-st="rejected"]{background:#fdecea;border-color:#c62828;color:#c62828}
.menu__reset{display:flex;align-items:center;justify-content:center;gap:6px;width:100%;box-sizing:border-box;
  margin:0 0 8px;padding:6px 10px;border:1px solid var(--ds-color-stroke-default);border-radius:8px;
  background:#fff;color:#616161;cursor:pointer;font:500 12px/16px 'Roboto','Helvetica Neue',Arial,sans-serif}
.menu__reset:hover{background:#f4f5f7;border-color:#b0b8c2;color:#333}
.menu__reset .material-icons{font-size:16px;line-height:1}
.review__sep{width:1px;height:18px;background:var(--ds-color-stroke-default);margin:0 2px}
.review__btn--clear{color:#616161}
.review__btn--clear:hover{background:#f4f5f7;border-color:#b0b8c2;color:#333}
.review__saved{display:inline-block;font:500 12px/16px 'Roboto','Helvetica Neue',Arial,sans-serif;color:#7b8794;vertical-align:middle;white-space:nowrap}
.edit__head .review__saved{margin-left:8px}
.th-sub{font:400 11px/14px 'Roboto','Helvetica Neue',Arial,sans-serif;color:#7b8794;text-transform:none}
.review__saved.is-on{color:#0f852c}
/* Экспеншн-панель: у части карточек заголовок нажимается и содержимое скрывается.
   Сейчас так свёрнуты «Почему так», «Итог» и «Общее для всех компонентов». */
.card__head{display:flex;align-items:center;gap:8px;cursor:pointer}
.card__head h2{margin:0}
.card__head:hover .card__chev{color:#333}
.card__chev{margin-left:auto;font-size:20px;line-height:1;color:#7b8794;transition:transform .15s ease}
.card.is-collapsed .card__chev{transform:rotate(-90deg)}
.card.is-collapsed .card__body{display:none}
.card__body{margin-top:12px}
.review__note{margin:6px 0 0;font:400 12px/16px 'Roboto','Helvetica Neue',Arial,sans-serif;color:#0f852c;min-height:16px}
.review__who{flex:0 0 100%;display:block;margin:0 0 8px;font:500 12px/16px 'Roboto','Helvetica Neue',Arial,sans-serif;color:#5b6d7f}
.review__who input{margin-top:4px;width:100%;box-sizing:border-box;padding:6px 8px;border:1px solid #c9d1dc;border-radius:8px;font:400 13px/18px 'Roboto','Helvetica Neue',Arial,sans-serif;color:#1b1f24}
.review__buttons{flex:0 0 100%;display:flex;flex-wrap:wrap;gap:6px;align-items:center;justify-content:flex-start}
.review__comment-block{margin-top:12px}
.review__comment-label{margin:0 0 4px;font:500 13px/18px 'Roboto','Helvetica Neue',Arial,sans-serif;color:#616161}
.review__comment{display:block;width:100%;box-sizing:border-box;min-height:72px;resize:vertical;
  background:#fff;border:1px solid var(--ds-color-stroke-default);border-radius:8px;
  font:400 14px/20px 'Roboto','Helvetica Neue',Arial,sans-serif;padding:8px 10px;color:#333}
.review__comment:focus{outline:none;border-color:var(--ds-palette-accent-500,#448AFF)}
.review__comment-actions{display:flex;justify-content:flex-end;align-items:center;gap:10px;margin-top:6px}
.review__tools{display:flex;flex-wrap:wrap;gap:8px;align-items:center;margin-bottom:8px}
.review__tools > button,.review__buttons > button,.json-menu__btn{
  font:500 12px/16px 'Roboto','Helvetica Neue',Arial,sans-serif;padding:4px 10px;border-radius:8px;cursor:pointer;
  border:1px solid var(--ds-color-stroke-default);background:#fff;color:#333;display:inline-flex;align-items:center;gap:4px}
.review__tools > button:hover,.review__buttons > button:hover,.json-menu__btn:hover{background:#f4f5f7}
.review__tools .material-icons{font-size:16px;line-height:1}
.json-menu{position:relative}
.json-menu__list{position:absolute;z-index:60;top:calc(100% + 4px);left:0;min-width:130px;padding:4px;
  background:#fff;border:1px solid var(--ds-color-stroke-default);border-radius:8px;
  box-shadow:0 10px 24px rgba(0,0,0,.14);display:flex;flex-direction:column;gap:2px}
.json-menu__list[hidden]{display:none}
.json-menu__list button{font:500 12px/16px 'Roboto','Helvetica Neue',Arial,sans-serif;text-align:left;
  padding:6px 8px;border:0;border-radius:6px;background:transparent;color:#333;cursor:pointer}
.json-menu__list button:hover{background:#f4f5f7}
.review__progress{padding:4px 2px 8px;font:400 13px/18px 'Roboto','Helvetica Neue',Arial,sans-serif;color:#616161}
.review__progress b{color:#333;font-weight:500}
.review__progress .is-ok{color:#0f852c}
.review__progress .is-later{color:#a35b00}
.review__progress .is-no{color:#c62828}
.review__progress .material-icons{font-size:16px;line-height:1;vertical-align:-3px}
/* Пункт меню паттерна: заголовок + иконка статуса + метка комментария (как в KDS) */
.screens__item{display:flex;align-items:center;gap:8px}
.item__t{flex:1 1 auto;min-width:0}
.item__st{flex:0 0 auto;width:16px;text-align:center}
.item__st .material-icons{font-size:16px;line-height:1}
.item__st.is-accepted{color:#0f852c}
.item__st.is-later{color:#ea7806}
.item__st.is-rejected{color:#c62828}
.item__cm{flex:0 0 auto;display:none;color:var(--ds-palette-accent-500,#448AFF)}
.item__cm .material-icons{font-size:16px;line-height:1}
.screens__item.is-viewed{color:#9e9e9e}
/* Шапка колонки «Правка»: заголовок и кнопка сохранения значений */
.edit__head{white-space:nowrap}
.edit__head .review__btn{margin-left:8px;vertical-align:middle}
.screens__note:empty{display:none}
.screens__sets[hidden]{display:none}
/* Кнопки в теле экрана и в шторке: колонка, ширина по содержимому; кнопка
   на всю строку получает модификатор ДС .ds-btn--full-width (мобильный слой,
   Button_DS/button-group-mob.css), своей обёртки у каркаса нет. */
.btnbox{display:flex;flex-direction:column;gap:8px;align-items:flex-start}
/* Одна кнопка в слоте заполняет строку (на мобиле кнопка идёт на всю ширину
   строки), группа делит строку поровну; иконка-кнопка и примеры в собственной
   обёртке (.pat__hit, .pat__narrow) не растягиваются. */
.btnbox > .ds-btn{width:100%}
.btnbox .ds-btn-group{width:100%}
/* Нижняя панель шторки — как в приложении: сумма слева, кнопки справа. */
.sheetbar{display:flex;align-items:center;justify-content:space-between;gap:12px}
.sheetbar__sum{font:500 16px/24px 'Roboto','Helvetica Neue',Arial,sans-serif;color:#333;white-space:nowrap}
.sheetbar .btnbox{flex:0 0 auto}
/* Старый вид блока «На экране» (экраны + колонки «Что» и «Правка») — пока он остался
   у остальных компонентов: правила нужны, пока их страницы не пересобраны новым видом. */
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
# То же — для макета экрана: внутри телефона стоят те же компоненты ДС, и им нужны
# те же правила (снять заливку-плашку, замороженные ширины и браузерные рамки полей),
# что и в панелях. Библиотека не правится.
for _rule in _panel_rules:
    CSS += _rule.replace(".panel ", ".phone__screen ") + "\n"




def review_row(vid):
    """Статусы паттерна — «Одобряем» / «Отложить» / «Не подходит» (как в KDS)."""
    out = []
    for st, icon, label in (("accepted", "check_circle", "Одобряем"),
                            ("later", "schedule", "Отложить"),
                            ("rejected", "cancel", "Не подходит")):
        out.append('<button class="review__btn" type="button" data-st="%s" data-pat="%s">'
                   '<span class="material-icons">%s</span>%s</button>' % (st, vid, icon, label))
    out.append('<span class="review__sep"></span>')
    out.append('<button class="review__btn review__btn--clear" type="button" data-pat-clear="%s" '
               'title="Убрать мою оценку, комментарий и отметку просмотра у этого паттерна">'
               '<span class="material-icons">restart_alt</span>Сбросить</button>' % vid)
    return '<span class="review__row">%s</span>' % "".join(out)


def review_comment(vid):
    """Поле «Свой комментарий» — сразу под «Источниками»."""
    return ('<div class="review__comment-block" data-pat="%s">'
            '<p class="review__comment-label">Свой комментарий</p>'
            '<textarea class="review__comment" rows="3" '
            'placeholder="Что дополнить или почему паттерн не подходит…"></textarea>'
            '<div class="review__comment-actions">'
            '<span class="review__saved" data-cmt-state title="Комментарий сохраняется сам"></span>'
            '</div></div>' % vid)


def screens_card(d):
    """Карточка «На экране»: меню паттернов, два одинаковых экрана и текст под ними.

    Экраны — один и тот же интерфейс дважды: слева значения как рекомендовано для
    мобилы, справа тот же экран с правками из 4-й колонки таблицы «Что меняется»
    (`data-preview="edit"` — в него пишутся поля «Правка»). Кнопки в экране стоят в
    теле (низ карточки и колонка вариаций) и в шторке, все места помечены
    `data-buttons`; при выборе паттерна в них подставляются кнопки из его примера —
    одинаково на обоих экранах. Текст выбранного паттерна показывается ниже экранов.
    """
    groups = list(d.get("patterns_ru") or [])
    if not groups:
        groups = list(d.get("platform_notes_ru") or [])
        if d.get("logic_ru"):
            groups.append({"title": "Логика (от себя, без источника)", "items": d["logic_ru"]})
    html = d.get("preview_html") or ""
    if not groups or not html:
        return ""
    slug = d.get("slug") or "c"
    if html.count('data-mode="mobile"') > 1:
        stage = html                      # два экрана уже в разметке (старый вид данных)
        # Правки из 4-й колонки применяются к правому экрану — помечаем именно второй.
        stage = stage.replace('data-mode="mobile"', 'data-mode="mobile" data-preview="edit"', 2)
        stage = stage.replace('data-mode="mobile" data-preview="edit"',
                              'data-mode="mobile"', 1)
        # Кнопки в старых данных лежат в контейнерах-классах: помечаем их слотами, как
        # в новых (data-buttons), чтобы пример выбранного паттерна вставал на их место.
        stage = re.sub(r'class="(phone__actions)"', r'class="\1" data-buttons="screen"', stage)
        stage = re.sub(r'class="(phone__foot)"', r'class="\1" data-buttons="sheet"', stage)
    else:
        second = html.replace('data-mode="mobile">', 'data-mode="mobile" data-preview="edit">', 1)
        item = '<div class="phones__item">%s<p class="phone__caption">%s</p></div>'
        stage = ('<div class="phones">'
                 + item % (html, "Как рекомендовано для мобилы")
                 + item % (second, "Тот же экран с правками из 4-й колонки")
                 + '</div>')
    items = ['<button class="screens__item screens__item--active" type="button" role="tab" '
             'aria-selected="true" data-view="base">Основные</button>']
    sets = []
    for i, g in enumerate(groups):
        vid = "pat-%s-%d" % (slug, i)
        items.append('<button class="screens__item" type="button" role="tab" aria-selected="false" '
                     'data-view="%s" data-pat="%s"><span class="item__t">%s</span>'
                     '<span class="item__st"></span>'
                     '<span class="item__cm" title="Есть комментарий">'
                     '<span class="material-icons">chat_bubble_outline</span></span></button>'
                     % (vid, vid, esc(g.get("title", ""))))
        items_txt = "".join("<li>%s</li>" % esc(x) for x in (g.get("items") or [])
                             if not str(x).startswith("Что делают системы"))
        src = g.get("src")
        src_html = ('<p class="plat__src">%s</p>' % esc(src)) if src else ""
        lead = ('<p class="pat__ex-note">%s</p>' % esc(g["example_ru"])) if g.get("example_ru") else ""
        # Текст под экранами — с заголовком самого паттерна: иначе непонятно, к какому
        # пункту меню относится то, что читаешь (пункт меню виден, а заголовок не читался).
        title = esc(g.get("title", ""))
        title_html = ('<h3 class="screens__note-title">%s</h3>' % title) if title else ""
        review = review_row(vid)                    # статусы справа от заголовка
        comment = review_comment(vid)               # свой комментарий — под «Источниками»
        head_html = ('<div class="screens__note-head">%s%s</div>' % (title_html, review)
                     if title_html else review)
        note = head_html + lead + ('<ul class="list">%s</ul>' % items_txt) + src_html + comment
        ex = g.get("example_html") or ""
        ex_sheet = g.get("example_html_sheet") or ex   # шторке можно дать свой пример
        # Набор кнопок показываем в контейнерах экрана, а пример-состояние (галочки,
        # список, диалог) — вместо тела экрана: он не про кнопки, и в узкой строке
        # кнопок выглядел бы мусором.
        _classes = re.findall(r'class="([^"]*)"', ex)
        _tokens = [t for c in _classes for t in c.split()]
        ex_kind = "body" if any(t.startswith("ds-") and not t.startswith("ds-btn") for t in _tokens) else "slot"
        parts = ""
        if ex:
            parts = ('<div data-part="screen">%s</div><div data-part="sheet">%s</div>'
                     '<div data-part="body">%s</div>' % (ex, ex_sheet, ex))
        sets.append('<div data-set="%s" data-kind="%s">%s<div data-part="note">%s</div></div>'
                    % (vid, ex_kind, parts, note))
    return ('<div class="card">\n    <h2>На экране</h2>\n'
            '    <div class="screens">\n'
            '      <div class="screens__menu" role="tablist">%s</div>\n'
            '      <div class="screens__stage">%s</div>\n'
            '    </div>\n'
            '    <div class="screens__note" data-note></div>\n'
            '    <div class="screens__sets" hidden>%s</div>\n  </div>'
            % ('<div class="review__progress" data-rev-progress></div>'
               '<button class="menu__reset" type="button" data-reset-patterns '
               'title="Сбросить оценки всех паттернов этого компонента: статусы, комментарии и отметки просмотра. Значения колонки «Правка» останутся">'
               '<span class="material-icons">restart_alt</span>Сбросить оценки паттернов</button>'
               + "".join(items),
               stage, "".join(sets)))


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
    """Что меняется на мобиле: Desktop и Mobile плюс 4-я колонка «Правка» — поля, которые
    применяются только к правому экрану блока «На экране» (левый остаётся с рекомендованными
    для мобилы значениями)."""
    body, has_edit = [], False
    for c in d["changes"]:
        inputs = edits_of(c)
        if inputs:
            has_edit = True
        body.append('<tr><td>%s</td><td>%s</td><td>%s</td><td class="edit">%s</td></tr>'
                    % (esc(c["what"]), esc(c["desktop"]), esc(c["mobile"]), inputs))
    head = ('<table><tr><th>Что</th><th>Desktop</th><th>Mobile<br><span class="th-sub">рекомендованные</span></th>'
            '<th class="edit__head"><span>Правка</span>'
            '<span class="review__saved" data-edits-state title="Значения сохраняются сами"></span>'
            '</th></tr>')
    note = ('<p class="point" style="margin-top:10px">Правка применяется к правому экрану в блоке '
            '«На экране». Левый — значения как рекомендовано для мобилы.</p>') if has_edit else ""
    return head + "".join(body) + "</table>" + note


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

%(screens)s

  <div class="card">
    <h2>Что меняется на мобиле</h2>
    %(changes)s
    %(behaviour)s
  </div>

  <div class="card" data-fold="%(slug)s-why">
    <div class="card__head" role="button" tabindex="0" aria-expanded="true">
      <h2>Почему так</h2><span class="material-icons card__chev">expand_more</span>
    </div>
    <div class="card__body">
      <p class="point">%(why)s%(why_link)s</p>
    </div>
  </div>

  <div class="card" data-fold="%(slug)s-result">
    <div class="card__head" role="button" tabindex="0" aria-expanded="true">
      <h2>Итог</h2><span class="material-icons card__chev">expand_more</span>
    </div>
    <div class="card__body">
      %(result)s
    </div>
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
/* Меню блока «На экране»: «Основные» — дефолтные кнопки на экранах, пункт паттерна —
   кнопки из его примера (и текст этого паттерна под экранами). Меняем только места
   с data-buttons и текст; оба экрана получают одно и то же, а правки из 4-й колонки
   остаются только на правом экране. */
(function () {
  var items = [].slice.call(document.querySelectorAll('.screens__item'));
  if (!items.length) return;
  var slots = [].slice.call(document.querySelectorAll('[data-buttons]'));
  var note = document.querySelector('[data-note]');
  var base = slots.map(function (s) { return s.innerHTML; });
  var baseNote = note ? note.innerHTML : '';
  /* У компонентов с примерами-состояниями (галочки, списки, диалоги) кнопок в примере нет:
     там показываем пример вместо тела экрана — в теле одна вариация компонента, в шторке
     другая, и шторку не трогаем: компонент должен быть виден в обоих местах. */
  var bodies = [].slice.call(document.querySelectorAll('.phone__body'));
  var baseBodies = bodies.map(function (b) { return b.innerHTML; });
  /* Режим на каждый паттерн свой: он записан в наборе (data-kind). Запасной вариант —
     если пример-состояние, а тел экранов нет, показываем в кнопках. */
  var useBody = false;
  function setMode(kind) { useBody = (kind === 'body'); }
  function showBody(html) {
    bodies.forEach(function (b, i) { b.innerHTML = (html === undefined || html === null || html === '') ? baseBodies[i] : html; });
  }
  var sets = {}, kinds = {};
  [].slice.call(document.querySelectorAll('.screens__sets [data-set]')).forEach(function (set) {
    var parts = {};
    [].slice.call(set.querySelectorAll('[data-part]')).forEach(function (p) {
      parts[p.getAttribute('data-part')] = p.innerHTML;
    });
    sets[set.getAttribute('data-set')] = parts;
    kinds[set.getAttribute('data-set')] = set.getAttribute('data-kind') || 'slot';
  });
  items.forEach(function (it) {
    it.addEventListener('click', function () {
      var set = sets[it.getAttribute('data-view')];
      items.forEach(function (o) {
        var on = o === it;
        o.classList.toggle('screens__item--active', on);
        o.setAttribute('aria-selected', on ? 'true' : 'false');
      });
      setMode(set ? kinds[it.getAttribute('data-view')] : '');
      slots.forEach(function (slot, i) {
        if (useBody) return;
        var kind = slot.getAttribute('data-buttons');
        slot.innerHTML = (set && set[kind] !== undefined) ? set[kind] : base[i];
      });
      if (note) note.innerHTML = (set && set.note !== undefined) ? set.note : baseNote;
      showBody(useBody ? (set ? set.body : '') : '');
    });
  });
})();
/* Открыта внутри оболочки (или любого фрейма) — сообщаем родителю свою высоту и
   убираем свой нижний отступ. Под file:// оболочка не может заглянуть в этот
   документ (Chrome считает каждый файл отдельным origin), поэтому высоту она
   получает сообщением, а не замером. Открытая отдельной вкладкой страница ведёт
   себя как раньше: ничего не гасит и никому не сообщает. */
(function () {
  if (window.parent === window) return;
  var SLUG = '%(slug)s';
  function tame() {
    var crumb = document.querySelector('.crumbs');
    if (crumb) crumb.style.display = 'none';
    if (document.body) document.body.style.paddingBottom = '0';
    var wrap = document.querySelector('.wrap');
    if (wrap && wrap.lastElementChild) wrap.lastElementChild.style.marginBottom = '0';
    /* Свои полосы прокрутки гасим сами: пока страница показывает свою полосу,
       её ширина 15 px сужает текст, высота считается «с полосой», фрейм
       подстраивается под неё — и под блоком пояснений остаётся лишний отступ
       (замер под file://: 69 px вместо 17). Под http то же самое делала оболочка,
       но она не может заглянуть в документ под file://. */
    document.documentElement.style.overflow = 'hidden';
    if (document.body) document.body.style.overflow = 'hidden';
  }
  function report() {
    tame();
    var wrap = document.querySelector('.wrap');
    var last = wrap ? wrap.lastElementChild : null;
    /* Высоту берём только по низу последнего блока. documentElement.scrollHeight
       тут не годится: он никогда не меньше окна фрейма, поэтому после первой же
       перестраховки фрейм оставался на 52 px выше содержимого и под блоком
       пояснений вырастал лишний отступ (замер под file://: 69 px вместо 17). */
    var bottom = last ? Math.ceil(last.getBoundingClientRect().bottom + (window.scrollY || 0))
                      : Math.ceil(document.documentElement.scrollHeight);
    try {
      parent.postMessage({ ds: 'page-height', slug: SLUG, height: bottom,
                           full: Math.ceil(document.documentElement.scrollHeight) }, '*');
    } catch (e) {}
  }
  window.addEventListener('load', report);
  window.addEventListener('resize', report);
  if (document.fonts && document.fonts.ready) document.fonts.ready.then(report);
  [0, 120, 400, 1000, 2000, 4000].forEach(function (t) { setTimeout(report, t); });
  if (window.ResizeObserver) { try { new ResizeObserver(report).observe(document.body); } catch (e) {} }
})();
/* Курсор мыши на мобильных экранах заменён кружком, имитирующим касание пальцем:
   он идёт за указателем внутри телефона, при нажатии становится плотнее. На тач-
   устройствах не включается (там настоящий палец). Размер — 44 px. */
(function () {
  if (!window.matchMedia || !window.matchMedia('(hover:hover) and (pointer:fine)').matches) return;
  [].slice.call(document.querySelectorAll('.phone__screen')).forEach(function (screen) {
    var dot = document.createElement('div');
    dot.className = 'phone__touch';
    screen.appendChild(dot);
    function place(e) {
      var r = screen.getBoundingClientRect();
      dot.style.left = (e.clientX - r.left) + 'px';
      dot.style.top = (e.clientY - r.top) + 'px';
      dot.style.display = 'block';
    }
    screen.addEventListener('pointermove', place);
    screen.addEventListener('pointerover', place);
    screen.addEventListener('pointerleave', function () { dot.style.display = 'none'; });
    screen.addEventListener('pointerdown', function () { dot.classList.add('phone__touch--press'); });
    screen.addEventListener('pointerup', function () { dot.classList.remove('phone__touch--press'); });
  });
})();
/* ── Ревью страницы: статусы паттернов, свой комментарий, отметки в меню, «просмотрено»
   и отчёт. Механизм тот же, что в KDS (iiko-ds-prototypes/KDS/ux-proposals.html):
   решения лежат в localStorage, меню показывает статусы, отчёт скачивается файлом.
   Ключи хранилища — по компоненту (SLUG). ── */
(function () {
  var SLUG = '%(slug)s';
  var ROUND = 1;                      /* номер круга ревью: новый круг — новые ключи */
  var LABEL = { accepted: 'Одобряем', later: 'Отложить', rejected: 'Не подходит' };
  var ICON = { accepted: 'check_circle', later: 'schedule', rejected: 'cancel' };
  /* Кто смотрит: у каждого человека свои решения, комментарии, правки и отметки просмотра
     (имя выбирается в меню компонентов). Один человек — один файл решений, поэтому мнения
     четырёх дизайнеров и двух ответственных не затирают друг друга. */
  var PERSON = '';
  try { PERSON = localStorage.getItem('rec-person') || ''; } catch (e) { PERSON = ''; }
  function keyOf(what) { return 'rec-' + what + '-' + SLUG + '-v1' + (PERSON ? ':' + PERSON : ''); }
  var REVIEW = {}, SEEN = {}, EDITS = {};
  function loadAll() {
    try { REVIEW = JSON.parse(localStorage.getItem(keyOf('review')) || '{}') || {}; } catch (e) { REVIEW = {}; }
    try { SEEN = JSON.parse(localStorage.getItem(keyOf('seen')) || '{}') || {}; } catch (e) { SEEN = {}; }
    try { EDITS = JSON.parse(localStorage.getItem(keyOf('edits')) || '{}') || {}; } catch (e) { EDITS = {}; }
  }
  loadAll();
  function saveReview() { try { localStorage.setItem(keyOf('review'), JSON.stringify(REVIEW)); } catch (e) {} }
  function saveSeen() { try { localStorage.setItem(keyOf('seen'), JSON.stringify(SEEN)); } catch (e) {} }
  function saveEdits() { try { localStorage.setItem(keyOf('edits'), JSON.stringify(EDITS)); } catch (e) {} }
  function entry(id) { return REVIEW[id] || {}; }
  function compName() { return document.querySelector('h1') ? document.querySelector('h1').textContent.trim() : SLUG; }
  function noteOfScore() { return document.querySelector('[data-note]'); }
  function activePat() {
    var it = document.querySelector('.screens__item--active[data-pat]');
    return it ? it.getAttribute('data-pat') : '';
  }
  /* Меню: иконка статуса, метка комментария, отметка «просмотрено», строка прогресса. */
  function paintMenu() {
    var n = { accepted: 0, later: 0, rejected: 0 }, seen = 0, total = 0;
    [].slice.call(document.querySelectorAll('.screens__item[data-pat]')).forEach(function (it) {
      var id = it.getAttribute('data-pat'), e = entry(id);
      total++;
      if (SEEN[id]) { seen++; it.classList.add('is-viewed'); } else { it.classList.remove('is-viewed'); }
      var st = it.querySelector('.item__st');
      if (st) {
        st.className = 'item__st' + (e.st ? ' is-' + e.st : '');
        st.innerHTML = e.st ? '<span class="material-icons">' + ICON[e.st] + '</span>' : '';
      }
      var cm = it.querySelector('.item__cm');
      if (cm) cm.style.display = e.note ? '' : 'none';
      if (e.st) n[e.st]++;
    });
    var pr = document.querySelector('[data-rev-progress]');
    if (pr) pr.innerHTML = 'Просмотрено <b>' + seen + '/' + total + '</b> · ' +
      '<span class="is-ok"><span class="material-icons">check_circle</span> ' + n.accepted + '</span> · ' +
      '<span class="is-later"><span class="material-icons">schedule</span> ' + n.later + '</span> · ' +
      '<span class="is-no"><span class="material-icons">cancel</span> ' + n.rejected + '</span>';
  }
  /* Текст паттерна: подсветка выбранного статуса и сохранённый комментарий. */
  function paintNote() {
    var note = noteOfScore();
    if (!note) return;
    var id = activePat(), e = entry(id);
    [].slice.call(note.querySelectorAll('.review__btn[data-st]')).forEach(function (b) {
      b.classList.toggle('is-on', b.getAttribute('data-st') === e.st);
    });
    var ta = note.querySelector('.review__comment');
    if (ta && !ta.__touched) ta.value = e.note || '';
  }
  function paint() { paintMenu(); paintNote(); showStates(); postSummary(); }
  /* Сводка для меню оболочки: сколько паттернов просмотрено и что решено.
     Идёт с задержкой, чтобы частые перерисовки не спамили родителя. */
  var sumT = null;
  function postSummary() {
    if (sumT) return;
    sumT = setTimeout(function () {
      sumT = null;
      var n = { accepted: 0, later: 0, rejected: 0 }, seen = 0, total = 0;
      [].slice.call(document.querySelectorAll('.screens__item[data-pat]')).forEach(function (it) {
        var id = it.getAttribute('data-pat'), e = entry(id);
        total++;
        if (SEEN[id]) seen++;
        if (e.st) n[e.st]++;
      });
      try {
        parent.postMessage({ ds: 'rec-summary', slug: SLUG, total: total, seen: seen,
                             accepted: n.accepted, later: n.later, rejected: n.rejected }, '*');
      } catch (e) {}
    }, 400);
  }
  /* Кнопок сохранения нет: и комментарий, и значения колонки «Правка» пишутся сами —
     через короткую паузу после ввода и сразу при уходе из поля. Пометка «Сохранено»
     тихо стоит рядом и подсвечивается зелёным в момент записи. */
  var tmr = {};
  function mark(el, on) {
    if (!el) return;
    el.textContent = on ? 'Сохранено' : '';
    el.classList.toggle('is-on', !!on);
    if (!on) return;
    clearTimeout(el.__t);
    el.__t = setTimeout(function () { el.classList.remove('is-on'); }, 1800);
  }
  function commitComment(block) {
    if (!block) return;
    var pid = block.getAttribute('data-pat');
    var ta = block.querySelector('.review__comment');
    var e = entry(pid), v = ta ? ta.value.trim() : '';
    if ((e.note || '') !== v) {
      REVIEW[pid] = { st: e.st || '', note: v };
      saveReview(); paintMenu();
    }
    mark(block.querySelector('[data-cmt-state]'), true);
  }
  function commitEdits() {
    editRows().forEach(function (r) { EDITS[r.id] = { value: r.value, at: new Date().toISOString() }; });
    saveEdits();
    mark(document.querySelector('[data-edits-state]'), true);
  }
  function showStates() {
    var block = noteOfScore() ? noteOfScore().querySelector('.review__comment-block') : null;
    if (block) mark(block.querySelector('[data-cmt-state]'), true);
    mark(document.querySelector('[data-edits-state]'), true);
  }
  function download(name, text, mime) {
    var blob = new Blob([text], { type: (mime || 'text/plain') + ';charset=utf-8' });
    var a = document.createElement('a');
    a.href = URL.createObjectURL(blob);
    a.download = name;
    document.body.appendChild(a); a.click(); a.remove();
    setTimeout(function () { URL.revokeObjectURL(a.href); }, 2000);
  }
  function esc(v) {
    return String(v).replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;');
  }
  /* Правки 4-й колонки: значения полей (пишутся сами) — уходят в отчёт. */
  function editRows() {
    var rows = [];
    [].slice.call(document.querySelectorAll('.edit__input')).forEach(function (f) {
      var tr = f.closest('tr');
      if (!tr) return;
      var td = tr.querySelectorAll('td');
      rows.push({
        id: f.getAttribute('data-id'),
        what: td[0] ? td[0].textContent.trim() : '',
        desktop: td[1] ? td[1].textContent.trim() : '',
        mobile: td[2] ? td[2].textContent.trim() : '',
        value: f.value
      });
    });
    return rows;
  }
  function buildXls() {
    var rows = '';
    [].slice.call(document.querySelectorAll('.screens__item[data-pat]')).forEach(function (it) {
      var e = entry(it.getAttribute('data-pat'));
      rows += '<tr><td>' + esc(it.querySelector('.item__t').textContent.trim()) + '</td><td>' +
        esc(e.st ? LABEL[e.st] : 'Не рассмотрено') + '</td><td>' + esc((e.note || '').replace(/\\n/g, ' ')) +
        '</td><td>' + (e.st === 'accepted' ? 'да' : '—') + '</td></tr>';
    });
    var er = '';
    editRows().forEach(function (r) {
      er += '<tr><td>' + esc(r.what) + '</td><td>' + esc(r.desktop) + '</td><td>' + esc(r.mobile) +
        '</td><td>' + esc(r.value) + '</td></tr>';
    });
    return '<html xmlns:o="urn:schemas-microsoft-com:office:office" ' +
      'xmlns:x="urn:schemas-microsoft-com:office:excel" xmlns="http://www.w3.org/TR/REC-html40">' +
      '<head><meta charset="utf-8"><meta name="ProgId" content="Excel.Sheet"><style>' +
      'table{border-collapse:collapse;font-family:Calibri,Arial,sans-serif;font-size:11pt}' +
      'th,td{border:1px solid #c9d1dc;padding:4px 8px;vertical-align:top;text-align:left}' +
      'th{background:#eef3f9;font-weight:bold}h2{font-family:Calibri,Arial,sans-serif}</style></head><body>' +
      '<h2>Компонент: ' + esc(document.querySelector('h1') ? document.querySelector('h1').textContent.trim() : SLUG) +
      ' · ' + new Date().toLocaleString('ru-RU') + '</h2>' +
      '<table><tr><th>Паттерн</th><th>Решение</th><th>Свой комментарий</th><th>Одобрен</th></tr>' + rows + '</table>' +
      '<h2>Правки по компоненту (4-я колонка)</h2>' +
      '<table><tr><th>Что</th><th>Desktop</th><th>Mobile (рекомендованные)</th><th>Правка (значение)</th></tr>' + er + '</table>' +
      '</body></html>';
  }
  document.addEventListener('click', function (ev) {
    var t = ev.target;
    var st = t.closest ? t.closest('.review__btn[data-st]') : null;
    if (st && st.closest('[data-note]')) {
      var id = st.getAttribute('data-pat');
      var cur = entry(id);
      REVIEW[id] = { st: (cur.st === st.getAttribute('data-st') ? '' : st.getAttribute('data-st')), note: cur.note || '' };
      saveReview(); paint(); return;
    }
    var rp = t.closest ? t.closest('[data-reset-patterns]') : null;
    if (rp) { resetPatterns(); return; }
    var pc = t.closest ? t.closest('[data-pat-clear]') : null;
    if (pc) {
      var pid = pc.getAttribute('data-pat-clear');
      delete REVIEW[pid];
      delete SEEN[pid];
      saveReview(); saveSeen();
      var nb = noteOfScore() ? noteOfScore().querySelector('.review__comment') : null;
      if (nb) { nb.value = ''; nb.__touched = false; }
      paint();
      return;
    }
    var item = t.closest ? t.closest('.screens__item[data-pat]') : null;
    if (item) {
      SEEN[item.getAttribute('data-pat')] = 1;
      saveSeen();
      setTimeout(function () { paint(); }, 0);
      return;
    }
    var list = document.querySelector('[data-rev-json-list]');
    if (list && !list.hidden && !t.closest('.json-menu')) list.hidden = true;
  });
  /* Отчёт и перенос решений запускает оболочка (кнопки стоят в меню компонентов):
     она присылает сообщение, страница делает работу и отвечает текстом для строки-подсказки. */
  function exportXls() { download(SLUG + '.' + (PERSON || 'гость') + '.xls', buildXls(), 'application/vnd.ms-excel'); return 'Отчёт xls скачан (' + (PERSON || 'гость') + ')'; }
  /* Файл решений одного человека: из таких файлов потом собирается сводная таблица. */
  function payload() {
    return {
      version: 2, round: ROUND, component: SLUG,
      componentName: document.querySelector('h1') ? document.querySelector('h1').textContent.trim() : SLUG,
      person: PERSON || 'гость', savedAt: new Date().toISOString(),
      decisions: REVIEW, seen: SEEN, edits: EDITS
    };
  }
  var K_RE = /^rec-(review|seen|edits)-(.+)-v1(:.*)?$/;
  function suffix() { return PERSON ? ':' + PERSON : ''; }
  function normDecisions(src) {
    var out = {};
    Object.keys(src || {}).forEach(function (k) {
      var v = src[k] || {}, o = {};
      if (v.st === 'accepted' || v.st === 'later' || v.st === 'rejected') o.st = v.st;
      if (typeof v.note === 'string' && v.note) o.note = v.note;
      if (o.st || o.note) out[k] = o;
    });
    return out;
  }
  function normSeen(src) {
    var out = {};
    Object.keys(src || {}).forEach(function (k) { if (src[k]) out[k] = 1; });
    return out;
  }
  function normEdits(src) {
    var out = {};
    Object.keys(src || {}).forEach(function (k) { if (src[k] && src[k].value !== undefined) out[k] = src[k]; });
    return out;
  }
  /* Все компоненты, по которым у текущего человека что-то есть: ключи хранилища
     собираем сами, страницы других компонентов для этого не нужны. */
  function layerOfAll() {
    var comps = {}, want = suffix(), i, k, m, s2;
    try {
      for (i = 0; i < localStorage.length; i++) {
        k = localStorage.key(i) || '';
        m = k.match(K_RE);
        if (!m || (m[3] || '') !== want) continue;
        s2 = m[2];
        comps[s2] = comps[s2] || { decisions: {}, seen: {}, edits: {} };
        try { comps[s2][m[1] === 'review' ? 'decisions' : m[1]] = JSON.parse(localStorage.getItem(k) || '{}') || {}; } catch (e) {}
      }
    } catch (e) {}
    if (!comps[SLUG]) comps[SLUG] = { decisions: REVIEW, seen: SEEN, edits: EDITS };
    comps[SLUG].componentName = compName();
    return comps;
  }
  function exportJson() {
    var who = PERSON || 'гость';
    download(SLUG + '.' + who + '.json', JSON.stringify(payload(), null, 2), 'application/json');
    return 'Мои решения (' + who + ') по компоненту «' + compName() + '» скачаны файлом';
  }
  function exportJsonAll() {
    var who = PERSON || 'гость', comps = layerOfAll();
    download('rec-review-all.' + who + '.json', JSON.stringify({
      version: 3, kind: 'rec-review-all', round: ROUND, person: who,
      savedAt: new Date().toISOString(), components: comps
    }, null, 2), 'application/json');
    return 'Решения (' + who + ') по всем компонентам (' + Object.keys(comps).length + ') скачаны файлом';
  }
  /* Загрузка файла: один компонент или сразу все. Кладём в слой ТЕКУЩЕГО человека —
     так чужой (или свой прежний) файл становится основой, которую можно править точечно. */
  function importAll(data) {
    var comps = data.components || {}, want = suffix(), n = 0;
    Object.keys(comps).forEach(function (s2) {
      var c = comps[s2] || {};
      try {
        localStorage.setItem('rec-review-' + s2 + '-v1' + want, JSON.stringify(normDecisions(c.decisions)));
        localStorage.setItem('rec-seen-' + s2 + '-v1' + want, JSON.stringify(normSeen(c.seen)));
        localStorage.setItem('rec-edits-' + s2 + '-v1' + want, JSON.stringify(normEdits(c.edits)));
        n++;
      } catch (e) {}
    });
    loadAll(); paint();
    return 'Загружено компонентов: ' + n + ' (слой ' + (PERSON || 'без имени') + ', автор файла: ' + (data.person || '—') + ')';
  }
  /* Положить свои решения в репозиторий: сервер пишет _audit/rec/review/<компонент>.<человек>.json.
     Если страница открыта не через сервер (file://), предложим скачать файл. */
  function saveToRepo() {
    if (typeof fetch !== 'function') { exportJsonAll(); return Promise.resolve('Сервер недоступен — файл скачан'); }
    var who = PERSON || 'гость', comps = layerOfAll(), slugs = Object.keys(comps);
    var jobs = slugs.map(function (s2) {
      var c = comps[s2];
      return fetch('/__rec-review', {
        method: 'POST', headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          version: 3, round: ROUND, component: s2, componentName: c.componentName || s2,
          person: who, savedAt: new Date().toISOString(),
          decisions: c.decisions, seen: c.seen, edits: c.edits
        })
      }).then(function (r) { return r.json(); });
    });
    return Promise.all(jobs).then(function (res) {
      var ok = res.filter(function (r) { return r && r.ok; }).length;
      if (!ok) throw new Error('сервер отказал');
      var first = (res.filter(function (r) { return r && r.path; })[0] || {}).path || '';
      return 'Мои решения (' + who + ') записаны: файлов ' + ok + ' из ' + slugs.length +
             (first ? ', например ' + first : '');
    }, function () { exportJsonAll(); return 'Сервер не принял — файл скачан'; });
  }
  function importJson(text) {
    var data = JSON.parse(text);
    if (data && data.components) return importAll(data);
    REVIEW = normDecisions(data.decisions);
    EDITS = normEdits(data.edits);
    SEEN = normSeen(data.seen);
    saveReview(); saveEdits(); saveSeen(); paint();
    return 'Решения по компоненту «' + compName() + '» загружены из файла' + (data.person ? ' (автор файла: ' + data.person + ')' : '');
  }
  /* Оценки всех паттернов компонента: статусы, комментарии и отметки просмотра.
     Значения колонки «Правка» — отдельная работа, их не трогаем. */
  function resetPatterns() {
    if (!confirm('Сбросить оценки всех паттернов компонента «' + compName() + '»' + (PERSON ? ' (' + PERSON + ')' : '') +
                 '? Статусы, комментарии и отметки «просмотрено» очистятся. Значения колонки «Правка» останутся.')) return '';
    REVIEW = {}; SEEN = {};
    saveReview(); saveSeen();
    var ta = noteOfScore() ? noteOfScore().querySelector('.review__comment') : null;
    if (ta) { ta.value = ''; ta.__touched = false; }
    paint();
    return 'Оценки паттернов компонента «' + compName() + '» сброшены';
  }
  /* Значения колонки «Правка»: поля возвращаются к рекомендованным, живой просмотр чистится. */
  function resetEdits() {
    if (!confirm('Сбросить значения колонки «Правка» по компоненту «' + compName() + '»' + (PERSON ? ' (' + PERSON + ')' : '') +
                 '? Поля вернутся к рекомендованным значениям. Оценки паттернов и комментарии останутся.')) return '';
    EDITS = {};
    saveEdits();
    [].slice.call(document.querySelectorAll('.edit__input')).forEach(function (f) {
      f.value = f.getAttribute('value') || '';
      f.__touched = false;
    });
    var live = document.getElementById('live');
    if (live) live.textContent = '';
    paint();
    return 'Значения «Правка» по компоненту «' + compName() + '» сброшены';
  }
  function setPerson(name) {
    PERSON = String(name || '').trim();
    try { localStorage.setItem('rec-person', PERSON); } catch (e) {}
    loadAll();
    var ta = noteOfScore() ? noteOfScore().querySelector('.review__comment') : null;
    if (ta) ta.__touched = false;
    paint();
    return PERSON ? 'Решения ' + PERSON : 'Решения без имени';
  }
  window.addEventListener('message', function (ev) {
    var d = ev.data || {};
    if (d.ds !== 'review') return;
    if (d.person !== undefined && d.person !== PERSON) {
      PERSON = String(d.person || '').trim();
      try { localStorage.setItem('rec-person', PERSON); } catch (e) {}
      loadAll();
      var ta0 = noteOfScore() ? noteOfScore().querySelector('.review__comment') : null;
      if (ta0) ta0.__touched = false;
      paint();
    }
    function done(text) {
      if (!text) return;
      try { parent.postMessage({ ds: 'review-done', kind: d.kind, text: text }, '*'); } catch (e) {}
    }
    try {
      if (d.kind === 'xls') done(exportXls());
      else if (d.kind === 'json') done(exportJson());
      else if (d.kind === 'json-all') done(exportJsonAll());
      else if (d.kind === 'import-text') done(importJson(d.text || '{}'));
      else if (d.kind === 'reset') done(resetEdits());
      else if (d.kind === 'person') done(setPerson(d.person));
      else if (d.kind === 'save-repo') saveToRepo().then(done, function (e) { done('Не получилось: ' + e.message); });
    } catch (e) { done('Не получилось: ' + e.message); }
  });
  document.addEventListener('input', function (ev) {
    var t = ev.target;
    if (!t || !t.classList) return;
    if (t.classList.contains('review__comment')) {
      t.__touched = true;
      var block = t.closest('.review__comment-block');
      mark(block ? block.querySelector('[data-cmt-state]') : null, false);
      clearTimeout(t.__t);
      t.__t = setTimeout(function () { commitComment(block); }, 700);
      return;
    }
    if (t.classList.contains('edit__input')) {
      mark(document.querySelector('[data-edits-state]'), false);
      clearTimeout(tmr.edits);
      tmr.edits = setTimeout(commitEdits, 700);
    }
  });
  /* Уход из поля (blur не всплывает — слушаем на перехвате): пишем сразу, без паузы. */
  document.addEventListener('blur', function (ev) {
    var t = ev.target;
    if (!t || !t.classList) return;
    if (t.classList.contains('review__comment')) {
      clearTimeout(t.__t);
      commitComment(t.closest('.review__comment-block'));
      return;
    }
    if (t.classList.contains('edit__input')) { clearTimeout(tmr.edits); commitEdits(); }
  }, true);
  var active = document.querySelector('.screens__item--active[data-pat]');
  if (active) { SEEN[active.getAttribute('data-pat')] = 1; saveSeen(); }
  paint();
})();
</script>
<script>
/* Складные карточки: «Почему так», «Итог», «Общее для всех компонентов».
   Заголовок нажимается, состояние запоминается (по умолчанию свёрнуто). */
(function () {
  function setFold(c, open) {
    c.classList.toggle('is-collapsed', !open);
    var h = c.querySelector('.card__head');
    if (h) h.setAttribute('aria-expanded', open ? 'true' : 'false');
  }
  [].slice.call(document.querySelectorAll('.card[data-fold]')).forEach(function (c) {
    var id = 'rec-fold:' + c.getAttribute('data-fold'), saved = null;
    try { saved = localStorage.getItem(id); } catch (e) {}
    setFold(c, saved === null ? false : saved === '1');
    var head = c.querySelector('.card__head');
    if (!head) return;
    function toggle() {
      var open = c.classList.contains('is-collapsed');
      setFold(c, open);
      try { localStorage.setItem(id, open ? '1' : '0'); } catch (e) {}
    }
    head.addEventListener('click', toggle);
    head.addEventListener('keydown', function (ev) {
      if (ev.key === 'Enter' || ev.key === ' ') { ev.preventDefault(); toggle(); }
    });
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
        "screens": screens_card(d),
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
        '<button class="nav__item" type="button" data-slug="%s" data-parts="%d">'
        '<span class="nav__name">%s</span><span class="nav__badge"></span></button>'
        % (esc(d["slug"]), len(d.get("patterns_ru") or []), esc(d["component"]))
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
<!-- Иконки — лигатуры Material Icons, как на страницах компонентов: без этой строки
     «expand_more» и «restart_alt» рисуются словами. -->
<link rel="stylesheet" href="https://fonts.googleapis.com/icon?family=Material+Icons">
</head>
<body>
<div class="wrap">
  <h1>Компоненты: Desktop → Mobile</h1>
  <div class="kit">
    <nav class="nav" aria-label="Компоненты">
      <div class="review__tools">
        <label class="review__who">Кто смотрит
          <input type="text" list="rec-people" placeholder="имя" maxlength="40" data-shell-person
                 title="Под этим именем сохраняются ваши решения: статусы, комментарии, правки">
        </label>
        <datalist id="rec-people"></datalist>
        <div class="review__buttons">
          <button type="button" data-shell-rev="xls" title="Отчёт для Excel по текущему компоненту: паттерны, решения, комментарии, правки">Отчёт xls</button>
          <div class="json-menu">
            <button type="button" class="json-menu__btn" data-shell-rev="json-menu">JSON<span class="material-icons">expand_more</span></button>
            <div class="json-menu__list" data-shell-json-list hidden>
              <button type="button" data-shell-rev="json">Скачать по текущему компоненту</button>
              <button type="button" data-shell-rev="json-all">Скачать по всем компонентам</button>
              <button type="button" data-shell-rev="import">Загрузить решения из файла</button>
            </div>
          </div>
          <button type="button" data-shell-rev="save-repo" title="Записать мои решения по всем компонентам в репозиторий: _audit/rec/review/&lt;компонент&gt;.&lt;имя&gt;.json — по файлу на компонент"><span class="material-icons">save</span>В репозиторий</button>
          <button type="button" data-shell-rev="reset" title="Сбросить значения колонки «Правка» по текущему компоненту (оценки паттернов не трогает)"><span class="material-icons">restart_alt</span>Сброс правок</button>
          <input type="file" accept=".json,application/json" data-shell-file hidden>
        </div>
        <label class="review__filter"><input type="checkbox" data-shell-only-pending>
          <span>Только не пройденные</span></label>
        <p class="review__ds" data-ds-progress></p>
      </div>
      <p class="review__note" data-shell-note></p>
      <p class="nav__title">Компоненты · %(count)d</p>
      %(items)s
    </nav>
    <div>
      <iframe class="frame" id="frame" title="Страница компонента"></iframe>
        <div class="card" data-fold="shared">
        <div class="card__head" role="button" tabindex="0" aria-expanded="true">
          <h2>Общее для всех компонентов</h2><span class="material-icons card__chev">expand_more</span>
        </div>
        <div class="card__body">
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

/* Панель отчётов в меню компонентов: кнопки не работают сами — они шлют команду
   странице компонента в фрейме (она знает решения и поля правок) и показывают ответ. */
(function () {
  var note = document.querySelector('[data-shell-note]');
  function say(text) {
    if (!note) return;
    note.textContent = text || '';
    if (!text) return;
    clearTimeout(note.__t);
    note.__t = setTimeout(function () { note.textContent = ''; }, 4000);
  }
  var who = document.querySelector('[data-shell-person]');
  function personName() { return who ? String(who.value || '').trim() : ''; }
  if (who) {
    try { who.value = localStorage.getItem('rec-person') || ''; } catch (e) {}
    who.addEventListener('change', function () { live = {}; post('person'); showPeople(); renderNav(); });
    if (who.value) post('person');
  }
  /* Имена, под которыми уже что-то сохраняли, — подсказкой в поле. */
  function showPeople() {
    var dl = document.getElementById('rec-people');
    if (!dl) return;
    var names = [], i, k;
    try {
      for (i = 0; i < localStorage.length; i++) {
        k = localStorage.key(i) || '';
        if (k.indexOf('rec-review-') === 0 && k.indexOf(':') > 0) {
          var n = k.slice(k.indexOf(':') + 1);
          if (n && names.indexOf(n) < 0) names.push(n);
        }
      }
    } catch (e) {}
    if (personName() && names.indexOf(personName()) < 0) names.push(personName());
    dl.innerHTML = names.map(function (n) { return '<option value="' + n.replace(/[<>"&]/g, '') + '"></option>'; }).join('');
  }
  /* ── Бейджи у компонентов и общий прогресс: слои текущего человека читаем
     прямо из localStorage, а по открытому компоненту — из его же сводки. ── */
  var live = {};
  function layerOf(slug) {
    var su = personName() ? ':' + personName() : '';
    var out = { seen: 0, accepted: 0, later: 0, rejected: 0 };
    if (live[slug]) {
      out.seen = live[slug].seen; out.accepted = live[slug].accepted;
      out.later = live[slug].later; out.rejected = live[slug].rejected;
      return out;
    }
    try {
      var dec = JSON.parse(localStorage.getItem('rec-review-' + slug + '-v1' + su) || '{}') || {};
      var sn = JSON.parse(localStorage.getItem('rec-seen-' + slug + '-v1' + su) || '{}') || {};
      Object.keys(dec).forEach(function (k) {
        var st = (dec[k] || {}).st;
        if (st === 'accepted' || st === 'later' || st === 'rejected') out[st]++;
      });
      Object.keys(sn).forEach(function (k) { if (sn[k]) out.seen++; });
    } catch (e) {}
    return out;
  }
  function renderNav() {
    var decided = 0, seenAll = 0, partsAll = 0;
    items.forEach(function (it) {
      var slug = it.getAttribute('data-slug');
      var total = parseInt(it.getAttribute('data-parts') || '0', 10) || 0;
      var s = layerOf(slug), b = it.querySelector('.nav__badge');
      function c(cls, icon, v) { return v ? '<span class="' + cls + '"><span class="material-icons">' + icon + '</span>' + v + '</span>' : ''; }
      if (b) b.innerHTML = c('is-ok', 'check_circle', s.accepted) + c('is-later', 'schedule', s.later) +
                           c('is-no', 'cancel', s.rejected) + '<span>' + s.seen + '/' + total + '</span>';
      it.classList.toggle('is-done', total > 0 && s.seen >= total);
      if (s.accepted + s.later + s.rejected > 0) decided++;
      seenAll += s.seen; partsAll += total;
    });
    var pr = document.querySelector('[data-ds-progress]');
    if (pr) pr.textContent = 'Решено по ' + decided + ' из ' + items.length + ' компонентов · паттернов просмотрено ' +
      seenAll + ' из ' + partsAll + (personName() ? ' (слой ' + personName() + ')' : '');
  }
  var onlyPending = document.querySelector('[data-shell-only-pending]');
  if (onlyPending) {
    try { onlyPending.checked = localStorage.getItem('rec-only-pending') === '1'; } catch (e) {}
    function applyFilter() { document.querySelector('.nav').classList.toggle('nav--pending', onlyPending.checked); }
    onlyPending.addEventListener('change', function () {
      try { localStorage.setItem('rec-only-pending', onlyPending.checked ? '1' : '0'); } catch (e) {}
      applyFilter();
    });
    applyFilter();
  }
  function activeSlug() {
    var it = items.filter(function (i) { return /is-active/.test(i.className); })[0] || items[0];
    return it ? it.getAttribute('data-slug') : '';
  }
  document.querySelector('.review__tools').addEventListener('click', function (ev) {
    var b = ev.target.closest ? ev.target.closest('[data-shell-rev]') : null;
    if (!b) return;
    var kind = b.getAttribute('data-shell-rev');
    if (kind === 'json-menu') {
      var l = document.querySelector('[data-shell-json-list]');
      if (l) l.hidden = !l.hidden;
      return;
    }
    if (kind === 'import') { var f = document.querySelector('[data-shell-file]'); if (f) f.click(); return; }
    post(kind);
  });
  function hasReview() {
    try { return !!(frame.contentDocument && frame.contentDocument.querySelector('[data-note]')); }
    catch (e) { return true; }   /* под file:// документ фрейма не прочитать — просто отправляем */
  }
  function post(kind, text) {
    if (!hasReview()) { say('На этой странице ревью ещё нет — страница компонента не пересобрана'); return; }
    try {
      frame.contentWindow.postMessage({ ds: 'review', kind: kind, text: text || '', person: personName() }, '*');
    } catch (e) { say('Не получилось передать команду странице компонента'); }
  }
  window.addEventListener('message', function (ev) {
    var d = ev.data || {};
    if (d.ds === 'rec-summary') { live[d.slug] = d; renderNav(); return; }
    if (d.ds !== 'review-done') return;
    say((activeSlug() ? activeSlug() + ': ' : '') + (d.text || ''));
  });
  var f = document.querySelector('[data-shell-file]');
  if (f) f.addEventListener('change', function () {
    var file = this.files && this.files[0];
    if (!file) return;
    var r = new FileReader();
    r.onload = function () { post('import-text', String(r.result)); f.value = ''; };
    r.readAsText(file);
  });
})();

frame.addEventListener('load', function () {
  fit(); watch();
  live = {};
  if (personName()) post('person');
  showPeople(); renderNav();
});
/* Высоту фрейма сообщает сама страница компонента (postMessage). Под file://
   оболочка не может прочитать её документ: Chrome считает каждый локальный файл
   отдельным origin, замер молча падал в catch, фрейм оставался 600 px со своими
   полосами прокрутки, а страница внутри — обрезанной; полоса фрейма сужала её
   ещё на 15 px, из-за чего блок пояснений выглядел шире карточек. */
window.addEventListener('message', function (ev) {
  var m = ev.data;
  if (!m || m.ds !== 'page-height' || !m.slug) return;
  var cur = (frame.getAttribute('src') || '').split('.html')[0];
  if (m.slug !== cur) return;                    /* сообщение от прошлой страницы */
  var h = Math.max(Number(m.height) || 0, 600);
  frame.style.height = Math.ceil(h) + 'px';
});
window.addEventListener('resize', fit);
window.addEventListener('hashchange', function () { activate((location.hash || '').replace('#', ''), false); });
items.forEach(function (i) {
  i.addEventListener('click', function () {
    activate(i.getAttribute('data-slug'));
    window.scrollTo(0, 0);
  });
});
activate((location.hash || '').replace('#', '') || items[0].getAttribute('data-slug'), false);
renderNav();
</script>
<script>
/* Складные карточки: «Почему так», «Итог», «Общее для всех компонентов».
   Заголовок нажимается, состояние запоминается (по умолчанию свёрнуто). */
(function () {
  function setFold(c, open) {
    c.classList.toggle('is-collapsed', !open);
    var h = c.querySelector('.card__head');
    if (h) h.setAttribute('aria-expanded', open ? 'true' : 'false');
  }
  [].slice.call(document.querySelectorAll('.card[data-fold]')).forEach(function (c) {
    var id = 'rec-fold:' + c.getAttribute('data-fold'), saved = null;
    try { saved = localStorage.getItem(id); } catch (e) {}
    setFold(c, saved === null ? false : saved === '1');
    var head = c.querySelector('.card__head');
    if (!head) return;
    function toggle() {
      var open = c.classList.contains('is-collapsed');
      setFold(c, open);
      try { localStorage.setItem(id, open ? '1' : '0'); } catch (e) {}
    }
    head.addEventListener('click', toggle);
    head.addEventListener('keydown', function (ev) {
      if (ev.key === 'Enter' || ev.key === ' ') { ev.preventDefault(); toggle(); }
    });
  });
})();
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
