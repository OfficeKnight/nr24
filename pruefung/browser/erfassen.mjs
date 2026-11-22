// Lädt jede Adresse in einem frisch gestarteten Browser, ohne etwas anzuklicken.
// Erfasst Anfragen, Cookies, Speicher, Viewport-Angabe, übertragene Bytes und axe-core-Ergebnisse.
// Aufruf mit node browser/erfassen.mjs eingabe.json ausgabe.json
import { readFileSync, writeFileSync } from 'node:fs';
import { createRequire } from 'node:module';
import { chromium } from 'playwright';

const require = createRequire(import.meta.url);
const [, , eingabePfad, ausgabePfad] = process.argv;
const eingabe = JSON.parse(readFileSync(eingabePfad, 'utf-8'));
const axeQuelle = readFileSync(require.resolve('axe-core/axe.min.js'), 'utf-8');
const axeVersion = require('axe-core/package.json').version;
const pwVersion = require('playwright/package.json').version;

const pauseMs = Math.max(1000, eingabe.pause_ms ?? 1000);
const warteMs = eingabe.wartezeit_ms ?? 2000;
const aufloesen = eingabe.aufloesen ?? {};
const hosts = Object.keys(aufloesen);

const startOptionen = { args: [] };
if (hosts.length) {
  startOptionen.args.push('--host-resolver-rules=' + hosts.map(h => `MAP ${h} ${aufloesen[h]}`).join(', '));
  const proxy = process.env.HTTPS_PROXY || process.env.https_proxy;
  if (proxy) {
    startOptionen.proxy = { server: proxy, bypass: hosts.join(',') };
  }
}

const schlafen = ms => new Promise(r => setTimeout(r, ms));
const ergebnis = { playwright: pwVersion, axe: axeVersion, chromium: null, seiten: [] };
let letzterStart = 0;

for (const url of eingabe.urls) {
  const rest = letzterStart + pauseMs - Date.now();
  if (rest > 0) await schlafen(rest);
  letzterStart = Date.now();
  process.stderr.write(`  Browser ${ergebnis.seiten.length + 1}/${eingabe.urls.length}  ${url}\n`);
  const seite = { url, endadresse: null, status: null, fehler: null, anfragen: [], cookies: [],
                  speicher: { local: [], session: [] }, viewport: null, axe: null };
  let browser;
  try {
    browser = await chromium.launch(startOptionen);
    ergebnis.chromium = browser.version();
    const kontext = await browser.newContext({
      ignoreHTTPSErrors: !!eingabe.https_fehler_ignorieren,
      locale: 'de-DE',
      viewport: { width: 1280, height: 800 },
    });
    const page = await kontext.newPage();
    const liste = [];
    page.on('request', r => liste.push({ r, fertig: false, fehlgeschlagen: null }));
    page.on('requestfinished', r => { const e = liste.find(x => x.r === r); if (e) e.fertig = true; });
    page.on('requestfailed', r => {
      const e = liste.find(x => x.r === r);
      if (e) e.fehlgeschlagen = r.failure()?.errorText ?? 'fehlgeschlagen';
    });
    const antwort = await page.goto(url, { waitUntil: 'load', timeout: 45000 });
    seite.status = antwort ? antwort.status() : null;
    try { await page.waitForLoadState('networkidle', { timeout: 8000 }); } catch { /* weiter */ }
    await page.waitForTimeout(warteMs);
    seite.endadresse = page.url();

    // Stand vor jeder weiteren Aktion festhalten
    const stand = liste.slice();
    for (const e of stand) {
      const eintrag = { url: e.r.url(), methode: e.r.method(), typ: e.r.resourceType(),
                        status: null, bytes: 0, fehler: e.fehlgeschlagen };
      try {
        const resp = await e.r.response();
        if (resp) eintrag.status = resp.status();
        if (e.fertig) {
          const g = await e.r.sizes();
          eintrag.bytes = Math.max(0, g.responseBodySize) + Math.max(0, g.responseHeadersSize);
        }
      } catch { /* Größe nicht verfügbar */ }
      seite.anfragen.push(eintrag);
    }
    seite.cookies = (await kontext.cookies()).map(c => ({
      name: c.name, domain: c.domain, pfad: c.path, secure: c.secure, httpOnly: c.httpOnly,
      sameSite: c.sameSite, ablauf: c.expires,
    }));
    try {
      seite.speicher = await page.evaluate(() => ({
        local: Object.keys(window.localStorage), session: Object.keys(window.sessionStorage) }));
    } catch { /* kein Zugriff */ }
    seite.viewport = await page.evaluate(() => {
      const m = document.querySelector('meta[name="viewport" i]');
      return m ? m.getAttribute('content') : null;
    });

    // axe-core wird über das Protokoll eingespielt, damit die CSP der Seite unverändert bleibt
    if (eingabe.axe !== false) {
      await page.evaluate(axeQuelle);
      seite.axe = await page.evaluate(async tags => {
        const r = await window.axe.run(document, {
          runOnly: { type: 'tag', values: tags }, resultTypes: ['violations', 'incomplete'] });
        const knapp = v => ({ id: v.id, impact: v.impact, hilfe: v.help, hilfeUrl: v.helpUrl, tags: v.tags,
          knoten: v.nodes.slice(0, 10).map(n => ({ ziel: n.target.join(' '), html: n.html.slice(0, 200) })),
          anzahl: v.nodes.length });
        return { verstoesse: r.violations.map(knapp), unklar: r.incomplete.map(knapp) };
      }, eingabe.axe_tags);
    }
  } catch (e) {
    seite.fehler = String(e && e.message ? e.message.split('\n')[0] : e);
  } finally {
    if (browser) await browser.close().catch(() => {});
  }
  ergebnis.seiten.push(seite);
}

writeFileSync(ausgabePfad, JSON.stringify(ergebnis), 'utf-8');
