// _audit/build-hover-off.mjs
// Генератор статической «глушилки ховеров» слоя ДС для тач-режима кадров прототипов.
//
// Зачем: обычные Chrome/Edge по file:// запрещают скриптам читать таблицы стилей
// (SecurityError на cssRules), поэтому динамическая глушилка в touch-mode.js там молчит.
// Этот файл — статическая компенсация: для каждого ховер-правила слоя ДС свойства
// возвращаются к базовым значениям, но ТОЛЬКО под body[data-touch] (тач-режим кадра).
// Работает в любом браузере, включая file://; генерируемые файлы ДС не трогает.
//
// Когда перезапускать: после каждой выгрузки слоя ДС из Фигмы —
//   node _audit/build-hover-off.mjs
// и затем поднять ?v=N у ссылки на touch-hover-off.css на страницах-кадрах.
import fs from 'node:fs';
import path from 'node:path';

const ROOT = path.resolve(import.meta.dirname, '..');
const SCAN_DIRS = ['iiko-ds-web', 'iiko-ds-mobile'];
const OUT_FILE = path.join(ROOT, 'iiko-ds-prototypes', 'touch-hover-off.css');
const REL = (p) => path.relative(ROOT, p).replaceAll('\\', '/');

function listCss(dir) {
  const res = [];
  for (const e of fs.readdirSync(dir, { withFileTypes: true })) {
    const p = path.join(dir, e.name);
    if (e.isDirectory()) res.push(...listCss(p));
    else if (e.name.endsWith('.css')) res.push(p);
  }
  return res;
}

function stripNoise(css) {
  return css
    .replace(/^\uFEFF/, '')
    .replace(/@(import|charset|namespace)[^;]*;/g, '')
    .replace(/\/\*[\s\S]*?\*\//g, ' ');   // комментарии — и между правилами, и внутри объявлений
}

// Возвращает [{media, selector, decls}] — верхний уровень + рекурсия в @media/@supports.
function parseRules(css, media = []) {
  const rules = [];
  let i = 0;
  while (i < css.length) {
    if (css.startsWith('/*', i)) { const end = css.indexOf('*/', i + 2); i = end === -1 ? css.length : end + 2; continue; }
    const ws = css.slice(i).match(/^\s+/);
    if (ws) { i += ws[0].length; continue; }
    const ob = css.indexOf('{', i);
    if (ob === -1) break;
    const prelude = css.slice(i, ob).trim();
    if (prelude.startsWith('@')) {
      let depth = 1, j = ob + 1;
      while (j < css.length && depth > 0) { if (css[j] === '{') depth++; else if (css[j] === '}') depth--; j++; }
      const inner = css.slice(ob + 1, j - 1);
      if (prelude.startsWith('@media') || prelude.startsWith('@supports')) rules.push(...parseRules(inner, [...media, prelude]));
      i = j;
      continue;
    }
    const cb = css.indexOf('}', ob);
    const body = css.slice(ob + 1, cb === -1 ? css.length : cb);
    rules.push({ media, selector: prelude, decls: parseDecls(body) });
    i = cb === -1 ? css.length : cb + 1;
  }
  return rules;
}

function parseDecls(body) {
  const out = [];
  for (const part of body.split(';')) {
    const p = part.trim();
    if (!p) continue;
    const idx = p.indexOf(':');
    if (idx === -1) continue;
    out.push({ prop: p.slice(0, idx).trim(), value: p.slice(idx + 1).trim() });
  }
  return out;
}

// Анализ селектора: компаунды + префикс до последнего компаунда.
// Компаунд — атомарная часть без комбинаторов (.ds-a.ds-b, .ds-input__frame, .ds-tab--active…).
function analyze(selector) {
  const compounds = [];
  let buf = '', lastSep = -1, depth = 0;
  for (let i = 0; i < selector.length; i++) {
    const ch = selector[i];
    if (ch === '[' || ch === '(') depth++;
    else if (ch === ']' || ch === ')') depth--;
    if (depth === 0 && (ch === ' ' || ch === '>' || ch === '+' || ch === '~')) {
      if (buf) { compounds.push(buf); buf = ''; }
      lastSep = i;
      continue;
    }
    buf += ch;
  }
  if (buf) compounds.push(buf);
  return { compounds, prefix: selector.slice(0, lastSep + 1), last: compounds[compounds.length - 1] || '' };
}

// доноры: целевой компаунд → правила, адресующие тот же элемент (для восстановления значений)
const providers = new Map();
const hoverRules = [];
const warnings = [];
let scanOrder = 0;

for (const dir of SCAN_DIRS) {
  const abs = path.join(ROOT, dir);
  if (!fs.existsSync(abs)) continue;
  for (const file of listCss(abs)) {
    const rules = parseRules(stripNoise(fs.readFileSync(file, 'utf8')));
    for (const r of rules) {
      for (const part of r.selector.split(',').map((s) => s.trim()).filter(Boolean)) {
        const a = analyze(part);
        if (!a.last) continue;
        const target = a.last.replace(/:hover/g, '');
        if (part.includes(':hover')) {
          hoverRules.push({ media: r.media, selector: part, decls: r.decls, file: REL(file), target, prefix: a.prefix, hoverInTarget: a.last.includes(':hover') });
        } else {
          if (!providers.has(target)) providers.set(target, []);
          const units = unitsOf(a.last);
          providers.get(target).push({ selector: part, prefix: a.prefix, decls: r.decls, order: scanOrder++, compound: a.last, weight: units.length });
        }
      }
      scanOrder++;
    }
  }
}

// компенсация → Map(prop → value)
const out = new Map();
let skipped = 0, fallbackUsed = 0, providerHits = 0;

// пары «шорткат ↔ длинная форма»: если точного свойства нет — искать парное
const PROP_FAMILIES = {
  background: ['background', 'background-color'],
  'background-color': ['background-color', 'background'],
  border: ['border', 'border-color'],
  'border-color': ['border-color', 'border'],
  outline: ['outline', 'outline-color'],
  'outline-color': ['outline-color', 'outline'],
};

// первичные значения — для модификаторов-обёрток без собственной базы
const INITIAL = {
  background: 'transparent',
  'background-color': 'transparent',
  'border-color': 'currentcolor',
  border: 'none',
  'box-shadow': 'none',
};

// Разбор компаунда на простые юниты (.ds-a.ds-b:state → ['.ds-a', '.ds-b', ':state'])
function unitsOf(compound) {
  return compound.split(/(?=[.#:\[])/).filter(Boolean);
}
// BEM-основа юнита: .ds-tab--active → .ds-tab, .ds-tab__part → .ds-tab
function stemOf(unit) {
  const m = unit.match(/^(\.[\w-]+?)(?:__[\w-]+|--[\w-]+)?$/);
  return m ? m[1] : unit;
}
// Подходит ли правило-донор (его целевой компаунд key) элементу с компаундом target:
// точное совпадение, точный поднабор юнитов или базовый BEM-класс любого юнита target.
function fits(target, key) {
  if (key === target) return true;
  const tu = unitsOf(target);
  return unitsOf(key).every((k) => tu.includes(k) || (k.startsWith('.') && k === stemOf(k) && tu.some((t) => t === k || t.startsWith(k + '--') || t.startsWith(k + '__'))));
}
function providerList(target) {
  const res = [];
  for (const [key, list] of providers) if (fits(target, key)) res.push(...list);
  // сначала менее специфичные доноры (меньше юнитов), затем точные — так значения перекрываются правильно
  return res.sort((a, b) => a.weight - b.weight || a.order - b.order);
}

// «часть-триггер» ховер-правила: условие наведения без контекстных фильтров.
// Например «.row:hover .input:checked + .track» → триггер «.row:hover »;
// если :hover стоит в целевом компаунде (одиночный селектор) — триггер пустой.
function triggerPartOf(h) {
  if (h.hoverInTarget) return '';
  const parts = [];
  let buf = '';
  for (let i = 0; i < h.prefix.length; i++) {
    const ch = h.prefix[i];
    if (ch === ' ' || ch === '>' || ch === '+' || ch === '~') { if (buf) { parts.push({ text: buf, end: i }); buf = ''; } continue; }
    buf += ch;
  }
  if (buf) parts.push({ text: buf, end: h.prefix.length });
  for (const p of parts) {
    if (p.text.includes(':hover')) {
      let j = p.end;
      while (j < h.prefix.length && ' >+~'.includes(h.prefix[j])) j++;
      return h.prefix.slice(0, j);
    }
  }
  return '';
}

for (const h of hoverRules) {
  const trigger = triggerPartOf(h);
  for (const d of h.decls) {
    let done = 0;
    for (const p of providerList(h.target)) {
      for (const candidateProp of PROP_FAMILIES[d.prop] || [d.prop]) {
        let value = null, found = false;
        for (const pd of p.decls) if (pd.prop === candidateProp) { value = pd.value; found = true; }
        if (!found) continue;
        if (value === d.value) { done++; break; }
        const compSel = (trigger + p.prefix + h.target + (h.hoverInTarget ? ':hover' : '')).trim().replace(/\s+/g, ' ');
        if (!out.has(compSel)) out.set(compSel, new Map());
        out.get(compSel).set(candidateProp, value);
        done++; providerHits++;
        break;
      }
    }
    if (!done) {
      if (INITIAL[d.prop] !== undefined) {
        const compSel = (trigger + h.target + (h.hoverInTarget ? ':hover' : '')).trim().replace(/\s+/g, ' ');
        if (!out.has(compSel)) out.set(compSel, new Map());
        out.get(compSel).set(d.prop, INITIAL[d.prop]);
        fallbackUsed++;
      } else {
        warnings.push(`${h.file}: «${h.selector}» → нет правила-донора для «${d.prop}»`);
        skipped++;
      }
    }
  }
}

const lines = [];
lines.push('/* touch-hover-off.css — СТАТИЧЕСКАЯ глушилка ховеров для тач-режима кадров (body[data-touch]).');
lines.push('   Сгенерировано: node _audit/build-hover-off.mjs (после обновлений слоя ДС — перезапускать).');
lines.push('   Руками не править; файл не перезаписывается выгрузкой из Фигмы. Обновления из Фигмы его не трогают.');
lines.push('   Нужен там, где браузер запрещает скриптам читать таблицы стилей (обычный Chrome/Edge по file://):');
lines.push('   там динамическая глушилка touch-mode.js бессильна, а этот файл работает — это обычный CSS. */');
lines.push('');

let emitted = 0;
for (const [selector, props] of out.entries()) {
  if (!props.size) continue;
  const decls = [...props.entries()].map(([p, v]) => `  ${p}: ${v};`).join('\n');
  lines.push(`body[data-touch] ${selector} {`);
  lines.push(decls);
  lines.push('}');
  emitted++;
}

fs.writeFileSync(OUT_FILE, lines.join('\n') + '\n', 'utf8');

console.log(`Файлов проверено: ${SCAN_DIRS.map((d) => listCss(path.join(ROOT, d)).length).reduce((a, b) => a + b, 0)}`);
console.log(`Ховер-правил найдено: ${hoverRules.length}`);
console.log(`Компенсаций записано: ${emitted} (в ${REL(OUT_FILE)})`);
console.log(`Из правил-доноров: ${providerHits}; первичные значения (обёртки без донора): ${fallbackUsed}`);
console.log(`Пропущено без донора и без первичного: ${skipped}`);
for (const w of warnings.slice(0, 30)) console.log('  ⚠ ' + w);
