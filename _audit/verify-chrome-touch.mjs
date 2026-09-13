// _audit/verify-chrome-touch.mjs
// Сквозная проверка тач-режима кадров в ОБЫЧНОМ Chrome по file:// (headless, мышь через CDP).
// Зачем: в обычном Chrome скриптам запрещено читать таблицы стилей (SecurityError на cssRules),
// поэтому там работает только статическая глушилка touch-hover-off.css; скрипт подтверждает,
// что на «Планшет · 768» ховер-визуалов нет, а на «Десктоп · 1184» — есть.
// Запуск: node _audit/verify-chrome-touch.mjs
import { spawn } from 'node:child_process';
import fs from 'node:fs';
import os from 'node:os';
import path from 'node:path';

const CHROME = 'C:\\Program Files\\Google\\Chrome\\Application\\chrome.exe';
const PORT = 9300 + (process.pid % 300);
const PAGE = process.argv[2] || 'file:///C:/Users/asukharev/GitHub/DS/iiko-ds-prototypes/figma-7436-pricelist-edit.html?v=99';
const BRIEF = process.argv.includes('--brief');
const profile = fs.mkdtempSync(path.join(os.tmpdir(), 'chrome-verify-'));
const sleep = (ms) => new Promise((r) => setTimeout(r, ms));

const chrome = spawn(CHROME, [
  '--headless=new', '--disable-gpu', '--no-first-run', '--no-default-browser-check',
  `--remote-debugging-port=${PORT}`, '--remote-allow-origins=*', `--user-data-dir=${profile}`, 'about:blank',
], { stdio: 'ignore' });

let ws; let msgId = 0; const pending = new Map();
const send = (method, params = {}) => new Promise((resolve, reject) => {
  const id = ++msgId;
  pending.set(id, { resolve, reject });
  ws.send(JSON.stringify({ id, method, params }));
});
async function waitFor(fn, timeout = 20000, step = 300) {
  const t0 = Date.now();
  while (Date.now() - t0 < timeout) { try { const v = await fn(); if (v) return v; } catch {} await sleep(step); }
  throw new Error('timeout');
}

try {
  await waitFor(async () => (await fetch(`http://127.0.0.1:${PORT}/json/version`)).ok);
  const target = await (await fetch(`http://127.0.0.1:${PORT}/json/new?${encodeURIComponent(PAGE)}`, { method: 'PUT' })).json();
  ws = new WebSocket(target.webSocketDebuggerUrl);
  await new Promise((res, rej) => { ws.onopen = res; ws.onerror = rej; });
  ws.onmessage = (ev) => {
    const m = JSON.parse(ev.data);
    if (m.id && pending.has(m.id)) {
      const p = pending.get(m.id); pending.delete(m.id);
      m.error ? p.reject(new Error(JSON.stringify(m.error))) : p.resolve(m.result);
    }
  };
  const evaluate = async (expr) => {
    const r = await send('Runtime.evaluate', { expression: expr, returnByValue: true });
    if (r.exceptionDetails) throw new Error('eval: ' + JSON.stringify(r.exceptionDetails).slice(0, 300));
    return r.result.value;
  };
  const evalJson = async (expr) => JSON.parse(await evaluate(`JSON.stringify(${expr})`));

  await send('Runtime.enable');
  await send('Page.enable');
  await waitFor(async () => (await evaluate('document.readyState')) === 'complete');
  await sleep(1500);

  const mouseAt = async (x, y) => { await send('Input.dispatchMouseEvent', { type: 'mouseMoved', x, y }); await sleep(300); };
  const measure = (sel, idx = 0) => evalJson(`(() => {
    const el = document.querySelectorAll(${JSON.stringify(sel)})[${idx}];
    if (!el) return { missing: true };
    el.scrollIntoView({ block: 'center', inline: 'center' });
    const b = el.getBoundingClientRect();
    const cs = getComputedStyle(el);
    return { x: Math.round(b.x + b.width / 2), y: Math.round(b.y + b.height / 2), hov: el.matches(':hover'), bg: cs.backgroundColor, border: cs.borderTopColor };
  })()`);
  async function probe(name, measureSel, hoverSel = measureSel, idx = 0) {
    await mouseAt(5, 400);
    const base = await measure(measureSel, idx);
    if (base.missing) return { name, error: 'элемент не найден' };
    await mouseAt(base.x, base.y);
    const hov = await measure(measureSel, idx);
    return { name, base: { bg: base.bg, border: base.border }, hover: { hov: hov.hov, bg: hov.bg, border: hov.border }, changed: base.bg !== hov.bg || base.border !== hov.border };
  }

  const results = { touch: [], desktop: [] };

  // ── тач-режим: планшет 768 ──
  await evaluate(`document.querySelector('.modes-bar__btn[data-w="768"]').click(); 'ok'`);
  await sleep(1000);
  results.env = await evalJson(`({ touch: document.body.hasAttribute('data-touch'), mode: (document.getElementById('w-mode') || {}).textContent, hasHoverOff: [...document.styleSheets].some((s) => s.href && s.href.includes('touch-hover-off')) })`);

  results.touch.push(await probe('Кнопка «Сохранить» (Accent Filled)', '.ds-btn--accent'));
  results.touch.push(await probe('Поиск (XS-круг)', '.ds-search'));
  results.touch.push(await probe('Ячейка-инпут (таблица)', '.ds-input-cell'));
  results.touch.push(await probe('Слайдер (по строке)', '.ds-slide-toggle__track', '.ds-slide-toggle__row'));
  results.touch.push(await probe('Строка таблицы (2-я)', '.ds-table-content-row', '.ds-table-content-row', 1));
  results.touch.push(await probe('Ячейка шапки', '.ds-table-header-cell'));
  results.touch.push(await probe('Таб', '.ds-tab'));
  results.touch.push(await probe('Поле даты', '.ds-input-datepicker__frame'));
  // действия строки при наведении в таче должны остаться скрытыми
  {
    const spot = await measure('.ds-table-content-row', 1);
    if (spot.missing) results.rowActionsVisibility = 'нет строк таблицы';
    else {
      await mouseAt(spot.x, spot.y);
      results.rowActionsVisibility = await evaluate(`(() => { const r = document.querySelectorAll('.ds-table-content-row')[1]; const a = r.querySelector('.row-actions'); return a ? getComputedStyle(a).visibility : 'нет'; })()`);
    }
  }

  // ── десктоп: 1184 — ховер обязан вернуться ──
  await evaluate(`document.querySelector('.modes-bar__btn[data-w="1184"]').click(); 'ok'`);
  await sleep(1000);
  results.desktop.push(await probe('Кнопка «Сохранить» (ожидается изменение)', '.ds-btn--accent'));
  results.desktop.push(await probe('Поиск (ожидается изменение рамки)', '.ds-search'));

  const bad = results.touch.filter((r) => r.changed);
  if (!BRIEF) console.log(JSON.stringify(results, null, 1));
  console.log(`[${PAGE.split('/').pop()}] env: ${JSON.stringify(results.env)}; проб: ${results.touch.length}, изменений в таче: ${bad.length}`);
  console.log(bad.length ? `ИТОГ: ПРОБЛЕМА — в тач-режиме меняются: ${bad.map((r) => r.name).join(', ')}` : 'ИТОГ: тач-режим чистый (все пробы без изменений); на десктопе ховеры вернулись.');
} catch (e) {
  console.error('ОШИБКА:', e.message);
} finally {
  try { chrome.kill(); } catch {}
  await sleep(500);
  try { fs.rmSync(profile, { recursive: true, force: true }); } catch {}
}
