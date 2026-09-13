// _audit/verify-layout-fix.mjs
// Сквозная проверка фикса вёрстки (переполнение кадра рейлом + скругления углов «экрана»)
// на всех 5 страницах и всех пресетах ширины. Запуск: node _audit/verify-layout-fix.mjs
import { spawn } from 'node:child_process';
import fs from 'node:fs';
import os from 'node:os';
import path from 'node:path';

const CHROME = 'C:\\Program Files\\Google\\Chrome\\Application\\chrome.exe';
const PORT = 9300 + (process.pid % 300);
const sleep = (ms) => new Promise((r) => setTimeout(r, ms));
const profile = fs.mkdtempSync(path.join(os.tmpdir(), 'chrome-layout-'));

const PAGES = [
  ['1276 metro', 'figma-1276-metro-desktop.html'],
  ['1277 metro2', 'figma-1277-metro-step2.html'],
  ['7422 suppliers', 'figma-7422-suppliers.html'],
  ['7431 pricelist', 'figma-7431-pricelist.html'],
  ['7436 edit', 'figma-7436-pricelist-edit.html'],
].map(([name, file]) => [name, `file:///C:/Users/asukharev/GitHub/DS/iiko-ds-prototypes/${file}?v=200`]);

const PRESETS = [1440, 1184, 768, 375];
// ожидаемые радиусы углов «экрана» по устройству (внутренние радиусы подложки)
const EXPECT = { 1440: ['device-desktop', 16, 16], 1184: ['device-desktop', 16, 16], 768: ['device-tablet', 14, 14], 375: ['device-phone', 24, 24] };

const chrome = spawn(CHROME, [
  '--headless=new', '--disable-gpu', '--no-first-run', '--no-default-browser-check',
  `--remote-debugging-port=${PORT}`, '--remote-allow-origins=*', `--user-data-dir=${profile}`, 'about:blank',
], { stdio: 'ignore' });

let ws = null; let msgId = 0; const pending = new Map();
const send = (method, params = {}) => new Promise((resolve, reject) => {
  const id = ++msgId;
  pending.set(id, { resolve, reject });
  ws.send(JSON.stringify({ id, method, params }));
});
async function waitFor(fn, timeout = 20000, step = 250) {
  const t0 = Date.now();
  while (Date.now() - t0 < timeout) { try { const v = await fn(); if (v) return v; } catch {} await sleep(step); }
  throw new Error('timeout');
}
async function connectTab(url) {
  const t = await (await fetch(`http://127.0.0.1:${PORT}/json/new?${encodeURIComponent(url)}`, { method: 'PUT' })).json();
  ws = new WebSocket(t.webSocketDebuggerUrl);
  await new Promise((res, rej) => { ws.onopen = res; ws.onerror = rej; });
  ws.onmessage = (ev) => {
    const m = JSON.parse(ev.data);
    if (m.id && pending.has(m.id)) { const p = pending.get(m.id); pending.delete(m.id); m.error ? p.reject(new Error(JSON.stringify(m.error))) : p.resolve(m.result); }
  };
  await send('Runtime.enable');
  await send('Page.enable');
  return t.id;
}
let evaluate = async () => '';
const evalJson = async (expr) => JSON.parse(await evaluate(`JSON.stringify(${expr})`));

try {
  await waitFor(async () => (await fetch(`http://127.0.0.1:${PORT}/json/version`)).ok);
  let fails = 0;
  for (const [name, url] of PAGES) {
    const tabId = await connectTab(url);
    evaluate = async (expr) => {
      const r = await send('Runtime.evaluate', { expression: expr, returnByValue: true });
      if (r.exceptionDetails) throw new Error('eval: ' + JSON.stringify(r.exceptionDetails).slice(0, 300));
      return r.result.value;
    };
    await waitFor(async () => (await evaluate('document.readyState')) === 'complete');
    await sleep(1200);
    const rows = [];
    for (const w of PRESETS) {
      await evaluate(`document.querySelector('.modes-bar__btn[data-w="${w}"]').click(); 'ok'`);
      await sleep(800);
      const m = await evalJson(`(() => {
        const panel = document.querySelector('#panel');
        const frame = document.querySelector('.frame');
        const hdr = document.querySelector('.apph');
        const nav = document.querySelector('.app-snav');
        const pr = panel.getBoundingClientRect(), fr = frame.getBoundingClientRect();
        const hcs = getComputedStyle(hdr), fcs = getComputedStyle(frame);
        const navOn = panel.classList.contains('app-snav-on');
        return {
          bodyCls: document.body.className.trim(),
          panelW: Math.round(pr.width),
          overlap: Math.round(fr.right - pr.right),
          contentOverflow: Math.round(frame.scrollWidth - frame.clientWidth),
          hdrTL: hcs.borderTopLeftRadius, hdrTR: hcs.borderTopRightRadius,
          frameBL: fcs.borderBottomLeftRadius, frameBR: fcs.borderBottomRightRadius,
          navBL: navOn && nav ? getComputedStyle(nav).borderBottomLeftRadius : 'hidden',
          hdrH: Math.round(hdr.getBoundingClientRect().height),
          navOn,
        };
      })()`);
      const [expCls, expR, expPhoneR] = EXPECT[w];
      const devOk = m.bodyCls.includes(expCls);
      const radiiOk = m.hdrTL === `${expR}px` && m.hdrTR === `${expR}px` && m.frameBL === `${expR}px` && m.frameBR === `${expR}px`;
      const navOk = w > 1160 ? (m.navOn && m.navBL === `${expR}px`) : !m.navOn;
      const ok = m.overlap === 0 && m.contentOverflow <= 0 && devOk && radiiOk && navOk;
      if (!ok) fails++;
      rows.push(`${ok ? 'OK  ' : 'FAIL'} ${String(w).padStart(4)} | overlap=${m.overlap} contentOverflow=${m.contentOverflow} radii=${m.hdrTL}/${m.frameBR} nav=${m.navOn ? 'on(' + m.navBL + ')' : 'off'} hdr=${m.hdrH} cls=${devOk ? 'ok' : m.bodyCls}`);
    }
    console.log(`\n== ${name} ==`);
    rows.forEach((r) => console.log('  ' + r));
    await fetch(`http://127.0.0.1:${PORT}/json/close/${tabId}`);
    ws = null;
  }
  console.log(fails === 0 ? '\nИТОГ: все проверки пройдены.' : `\nИТОГ: провалов — ${fails}.`);
  process.exitCode = fails === 0 ? 0 : 1;
} catch (e) {
  console.error('Ошибка:', e);
  process.exitCode = 2;
} finally {
  try { chrome.kill(); } catch {}
}
