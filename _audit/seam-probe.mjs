// _audit/seam-probe.mjs
// Проверка кромки «безель/рейл» в настоящем Chrome при заданном DPR (--force-device-scale-factor).
// Запуск: node _audit/seam-probe.mjs 1.5   (или 1.25, 2)
import { spawn } from 'node:child_process';
import fs from 'node:fs';
import os from 'node:os';
import path from 'node:path';

const DPR = process.argv[2] || '1.5';
const URL = process.argv[3] || 'file:///C:/Users/asukharev/GitHub/DS/iiko-ds-prototypes/figma-7436-pricelist-edit.html?v=24';
const CHROME = 'C:\\Program Files\\Google\\Chrome\\Application\\chrome.exe';
const PORT = 9600 + Math.floor(Math.random() * 300);
const sleep = (ms) => new Promise((r) => setTimeout(r, ms));
const profile = fs.mkdtempSync(path.join(os.tmpdir(), 'chrome-seam-'));

const chrome = spawn(CHROME, [
  '--headless=new', '--disable-gpu', '--no-first-run', '--no-default-browser-check',
  `--force-device-scale-factor=${DPR}`,
  '--window-size=1000,900',
  `--remote-debugging-port=${PORT}`, '--remote-allow-origins=*', `--user-data-dir=${profile}`, 'about:blank',
], { stdio: 'ignore' });

let ws; let msgId = 0; const pending = new Map();
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
let evaluate;
try {
  await waitFor(async () => (await fetch(`http://127.0.0.1:${PORT}/json/version`)).ok);
  const tab = await (await fetch(`http://127.0.0.1:${PORT}/json/new?${encodeURIComponent(URL)}`, { method: 'PUT' })).json();
  ws = new WebSocket(tab.webSocketDebuggerUrl);
  await new Promise((res, rej) => { ws.onopen = res; ws.onerror = rej; });
  ws.onmessage = (ev) => {
    const m = JSON.parse(ev.data);
    if (m.id && pending.has(m.id)) { const p = pending.get(m.id); pending.delete(m.id); m.error ? p.reject(new Error(JSON.stringify(m.error))) : p.resolve(m.result); }
  };
  evaluate = async (expr) => {
    const r = await send('Runtime.evaluate', { expression: expr, returnByValue: true });
    if (r.exceptionDetails) throw new Error('eval: ' + JSON.stringify(r.exceptionDetails).slice(0, 300));
    return r.result.value;
  };
  await send('Runtime.enable');
  await send('Page.enable');
  await waitFor(async () => (await evaluate('document.readyState')) === 'complete');
  await sleep(1600);
  await evaluate(`document.querySelector('.modes-bar__btn[data-w="1184"]').click(); 'ok'`);
  await sleep(900);
  await evaluate(`window.scrollTo(0, 0); 'ok'`);
  await sleep(400);
  const st = JSON.parse(await evaluate(`JSON.stringify((() => {
    const p = document.querySelector('#panel').getBoundingClientRect();
    const h = document.querySelector('.apph').getBoundingClientRect();
    const n = document.querySelector('.app-snav').getBoundingClientRect();
    return { dpr: window.devicePixelRatio, panelLeft: p.left, panelTop: p.top, hdrBottom: h.bottom, navLeft: n.left, cls: document.body.className };
  })())`));
  console.log(`DPR ${DPR} → window.devicePixelRatio=${st.dpr}, panelLeft=${st.panelLeft.toFixed(1)}, hdrBottom=${st.hdrBottom.toFixed(1)}, navLeft=${st.navLeft.toFixed(1)}, cls=${st.cls}`);
  const clip = { x: st.panelLeft - 24, y: st.hdrBottom - 10, width: 90, height: 230, scale: 1 };
  const shot = async (file) => {
    const s = await send('Page.captureScreenshot', { format: 'png', clip });
    fs.writeFileSync(file, Buffer.from(s.data, 'base64'));
    console.log('saved ' + file);
  };
  await shot(`c:/Users/asukharev/GitHub/DS/_audit/_real_dpr${DPR}_fixed.png`);
  const full = await send('Page.captureScreenshot', { format: 'png' });
  fs.writeFileSync(`c:/Users/asukharev/GitHub/DS/_audit/_real_dpr${DPR}_full.png`, Buffer.from(full.data, 'base64'));
  console.log('saved full');
  await evaluate(`(() => { const n = document.querySelector('.app-snav'); n.style.cssText = 'left:0;bottom:0;width:52px;padding:0;box-sizing:content-box'; return 'ok'; })()`);
  await sleep(400);
  await shot(`c:/Users/asukharev/GitHub/DS/_audit/_real_dpr${DPR}_old.png`);
} catch (e) {
  console.error('Ошибка:', e.message || e);
} finally {
  try { chrome.kill(); } catch {}
}
