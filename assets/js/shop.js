/*
 * Notebook Reparatur 24, shop.js
 * Warenkorb, Zähler, Suche mit Vorschlägen, Katalogfilter und Sortierung, Kasse,
 * Formulare, Anfrage-Assistent und Menü. Vanilla JS ohne Abhängigkeiten.
 * Daten kommen aus window.NR24 (assets/js/daten.js), Pfade darin sind relativ zur Wurzel,
 * die Wurzel steht in <html data-root="…">. Nichts wird an einen Server übertragen.
 */
(function () {
  'use strict';

  var KORB_SCHLUESSEL = 'nr24-warenkorb';
  var KASSE_SCHLUESSEL = 'nr24-kasse';
  var MENGE_MIN = 1;
  var MENGE_MAX = 99;
  var MELDUNG_DAUER = 6000;
  var VORSCHLAEGE_MAX = 6;
  var SUCHE_MIN_ZEICHEN = 2;
  var EMAIL_MUSTER = /^[^\s@]+@[^\s@]+\.[^\s@]{2,}$/;
  var KATALOG_PARAMETER = ['kategorie', 'hersteller', 'zustand', 'preis_min', 'preis_max', 'lieferbar', 'sort'];

  var ROOT = '';
  var ARTIKEL = [];
  var NACH_ID = {};
  var VERSAND = [];
  var ZAHLARTEN = [];
  var MWST = 19;

  var warenkorbAnsicht = null;
  var kasseAnsicht = null;
  var ansageEl = null;
  var ansageTimer = null;
  var meldungTimer = null;
  var meldungSetzTimer = null;
  var korbNotfall = null;
  var idZaehler = 0;

  /* ---------- Hilfsfunktionen ---------- */

  function alle(wurzel, selektor) {
    return Array.prototype.slice.call((wurzel || document).querySelectorAll(selektor));
  }

  function esc(wert) {
    return String(wert == null ? '' : wert).replace(/[&<>"']/g, function (z) {
      return { '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' }[z];
    });
  }

  /* Text escapen und Platzhalter in eckigen Klammern wie der Build markieren. */
  function text(wert) {
    return esc(wert).replace(/\[[^\[\]]+\]/g, function (t) { return '<span class="ph">' + t + '</span>'; });
  }

  function cssWert(wert) {
    if (window.CSS && typeof window.CSS.escape === 'function') { return window.CSS.escape(wert); }
    return String(wert).replace(/["\\]/g, '\\$&');
  }

  var preisFormat = null;
  try {
    preisFormat = new Intl.NumberFormat('de-DE', { style: 'currency', currency: 'EUR' });
  } catch (e) {
    preisFormat = null;
  }

  function preis(betrag) {
    var wert = Math.round(Number(betrag || 0) * 100) / 100;
    if (preisFormat) { return preisFormat.format(wert); }
    var teile = wert.toFixed(2).split('.');
    return teile[0].replace(/\B(?=(\d{3})+(?!\d))/g, '.') + ',' + teile[1] + '\u00a0€';
  }

  function cent(betrag) {
    return Math.round(Number(betrag || 0) * 100);
  }

  function mengeBegrenzen(wert) {
    var n = parseInt(wert, 10);
    if (!isFinite(n) || isNaN(n)) { n = MENGE_MIN; }
    return Math.min(MENGE_MAX, Math.max(MENGE_MIN, n));
  }

  function neueId(praefix) {
    idZaehler += 1;
    return praefix + '-' + idZaehler;
  }

  function fokus(el) {
    if (!el) { return; }
    if (!el.hasAttribute('tabindex') && !/^(A|BUTTON|INPUT|SELECT|TEXTAREA)$/.test(el.tagName)) {
      el.setAttribute('tabindex', '-1');
    }
    try { el.focus(); } catch (e) { /* nichts */ }
  }

  function speicherLesen(art, schluessel) {
    try {
      var s = window[art];
      return s ? s.getItem(schluessel) : null;
    } catch (e) {
      return null;
    }
  }

  function speicherSchreiben(art, schluessel, wert) {
    try {
      var s = window[art];
      if (!s) { return false; }
      s.setItem(schluessel, wert);
      return true;
    } catch (e) {
      return false;
    }
  }

  function urlParameter() {
    try { return new URLSearchParams(window.location.search); } catch (e) { return null; }
  }

  function sicher(fn) {
    try {
      fn();
    } catch (e) {
      if (window.console && console.warn) { console.warn('nr24 shop.js', e); }
    }
  }

  /* ---------- Daten ---------- */

  function datenLaden() {
    var wurzel = document.documentElement.getAttribute('data-root');
    ROOT = wurzel == null ? '' : String(wurzel);
    if (ROOT && ROOT.charAt(ROOT.length - 1) !== '/') { ROOT += '/'; }

    var d = window.NR24 && typeof window.NR24 === 'object' ? window.NR24 : {};
    ARTIKEL = Array.isArray(d.artikel) ? d.artikel.filter(function (a) {
      return a && typeof a.id === 'string' && typeof a.name === 'string';
    }) : [];
    NACH_ID = {};
    ARTIKEL.forEach(function (a) {
      a.preis = Number(a.preis) || 0;
      NACH_ID[a.id] = a;
    });
    VERSAND = Array.isArray(d.versand) ? d.versand.filter(function (v) { return v && v.id; }) : [];
    ZAHLARTEN = Array.isArray(d.zahlarten) ? d.zahlarten.filter(function (z) { return z && z.id; }) : [];
    MWST = typeof d.mwst === 'number' && d.mwst >= 0 ? d.mwst : 19;
  }

  function versandNach(id) {
    for (var i = 0; i < VERSAND.length; i += 1) {
      if (VERSAND[i].id === id) { return VERSAND[i]; }
    }
    return null;
  }

  function zahlartNach(id) {
    for (var i = 0; i < ZAHLARTEN.length; i += 1) {
      if (ZAHLARTEN[i].id === id) { return ZAHLARTEN[i]; }
    }
    return null;
  }

  function zustandSatz(a) {
    if (a.art === 'reparatur') {
      return (a.zustand || 'Dienstleistung') + ' · ' + (a.verfuegbar ? 'sofort buchbar' : 'derzeit nicht buchbar');
    }
    return (a.zustand || '') + ' · ' + (a.verfuegbar ? 'sofort lieferbar' : 'derzeit nicht lieferbar');
  }

  function bildSrcset(srcset) {
    return String(srcset || '').split(',').map(function (teil) {
      return ROOT + teil.trim();
    }).join(', ');
  }

  /* Produktkarte exakt wie im Markup-Vertrag (Bauplan 8). */
  function karteHtml(a, ebene) {
    var h = ebene || 'h2';
    var url = esc(ROOT + a.url);
    var bild;
    if (a.bild && a.bild.src) {
      bild = '<img class="produkt__bild" src="' + esc(ROOT + a.bild.src) + '"' +
        (a.bild.srcset ? ' srcset="' + esc(bildSrcset(a.bild.srcset)) + '"' : '') +
        ' sizes="(min-width: 1024px) 280px, (min-width: 600px) 45vw, 90vw"' +
        ' width="' + esc(a.bild.w || 800) + '" height="' + esc(a.bild.h || 600) + '"' +
        ' loading="lazy" decoding="async" alt="' + esc(a.bild.alt || a.name) + '">';
    } else {
      bild = '<span class="bildrahmen produkt__bild" role="img" aria-label="' + esc(a.name) + '">' +
        '<svg class="ico" aria-hidden="true"><use href="#i-display"></use></svg></span>';
    }
    return '<article class="produkt" data-id="' + esc(a.id) + '" data-name="' + esc(a.name) + '"' +
      ' data-preis="' + esc(a.preis.toFixed(2)) + '" data-hersteller="' + esc(a.hersteller || '') + '"' +
      ' data-zustand="' + esc(a.zustand || '') + '" data-kategorie="' + esc(a.kategorie || '') + '"' +
      ' data-rang="' + esc(a.rang == null ? 999 : a.rang) + '" data-verfuegbar="' + (a.verfuegbar ? '1' : '0') + '">' +
      '<a class="produkt__bildlink" href="' + url + '" tabindex="-1" aria-hidden="true">' + bild + '</a>' +
      '<div class="produkt__text">' +
      '<p class="produkt__kategorie">' + text(a.kategorie_name || '') + '</p>' +
      '<' + h + ' class="produkt__name"><a href="' + url + '">' + text(a.name) + '</a></' + h + '>' +
      (a.teilenummer ? '<p class="produkt__nummer teilenummer">' + esc(a.teilenummer) + '</p>' : '') +
      '<p class="produkt__zustand">' + text(zustandSatz(a)) + '</p>' +
      '</div>' +
      '<div class="produkt__fuss">' +
      '<p class="produkt__preis preis">' + preis(a.preis) + '</p>' +
      '<button class="knopf knopf--primaer knopf--klein" type="button" data-wk-add="' + esc(a.id) + '"' +
      ' aria-label="' + esc(a.name) + ' in den Warenkorb legen">' +
      '<svg class="ico" aria-hidden="true"><use href="#i-korb"></use></svg><span>In den Warenkorb</span></button>' +
      '</div>' +
      '</article>';
  }

  /* ---------- Ansagen und Meldung ---------- */

  function ansageAnlegen() {
    if (ansageEl || !document.body) { return; }
    ansageEl = document.createElement('div');
    ansageEl.className = 'sr-only';
    ansageEl.setAttribute('aria-live', 'polite');
    ansageEl.setAttribute('data-ansage', '');
    document.body.appendChild(ansageEl);
  }

  /* Leise Ansage für Screenreader (Mengen, Vorschläge), ohne sichtbare Meldung. */
  function ansage(satz, verzoegerung) {
    if (!ansageEl) { ansageAnlegen(); }
    if (!ansageEl) { return; }
    clearTimeout(ansageTimer);
    ansageTimer = setTimeout(function () {
      ansageEl.textContent = '';
      setTimeout(function () { ansageEl.textContent = satz; }, 40);
    }, verzoegerung || 0);
  }

  function meldungPlanen() {
    var el = document.getElementById('meldung');
    clearTimeout(meldungTimer);
    meldungTimer = setTimeout(function () {
      if (!el) { return; }
      var gefragt = el.contains(document.activeElement);
      try { gefragt = gefragt || el.matches(':hover'); } catch (e) { /* nichts */ }
      if (gefragt) {
        meldungPlanen();
        return;
      }
      el.innerHTML = '';
    }, MELDUNG_DAUER);
  }

  /* Sichtbare Meldung in #meldung (role="status"). Der Fokus bleibt, wo er ist. */
  function meldung(html) {
    var el = document.getElementById('meldung');
    if (!el) { return; }
    clearTimeout(meldungTimer);
    clearTimeout(meldungSetzTimer);
    el.innerHTML = '';
    meldungSetzTimer = setTimeout(function () {
      el.innerHTML = html;
      meldungPlanen();
    }, 40);
  }

  /* ---------- Warenkorb ---------- */

  function korbLesen() {
    var roh = korbNotfall !== null ? korbNotfall : speicherLesen('localStorage', KORB_SCHLUESSEL);
    var liste = [];
    if (roh) {
      try {
        var obj = JSON.parse(roh);
        if (obj && Array.isArray(obj.pos)) { liste = obj.pos; }
      } catch (e) {
        liste = [];
      }
    }
    var nachId = {};
    var ergebnis = [];
    liste.forEach(function (p) {
      if (!p || typeof p.id !== 'string') { return; }
      if (ARTIKEL.length && !NACH_ID[p.id]) { return; }
      var menge = mengeBegrenzen(p.menge);
      if (nachId[p.id]) {
        nachId[p.id].menge = mengeBegrenzen(nachId[p.id].menge + menge);
        return;
      }
      var neu = { id: p.id, menge: menge };
      nachId[p.id] = neu;
      ergebnis.push(neu);
    });
    return ergebnis;
  }

  function korbSchreiben(liste) {
    var roh = JSON.stringify({ v: 1, pos: liste.map(function (p) { return { id: p.id, menge: mengeBegrenzen(p.menge) }; }) });
    korbNotfall = speicherSchreiben('localStorage', KORB_SCHLUESSEL, roh) ? null : roh;
    korbGeaendert();
  }

  function korbPositionen() {
    return korbLesen().filter(function (p) { return !!NACH_ID[p.id]; });
  }

  function korbHinzufuegen(id, menge) {
    var liste = korbLesen();
    var dazu = mengeBegrenzen(menge);
    var gefunden = null;
    liste.forEach(function (p) { if (p.id === id) { gefunden = p; } });
    var vorher = gefunden ? gefunden.menge : 0;
    if (gefunden) {
      gefunden.menge = Math.min(MENGE_MAX, gefunden.menge + dazu);
    } else {
      liste.push({ id: id, menge: dazu });
    }
    korbSchreiben(liste);
    return { vorher: vorher, nachher: gefunden ? gefunden.menge : dazu, gekappt: vorher + dazu > MENGE_MAX };
  }

  function korbMengeSetzen(id, menge) {
    var liste = korbLesen();
    liste.forEach(function (p) { if (p.id === id) { p.menge = mengeBegrenzen(menge); } });
    korbSchreiben(liste);
  }

  function korbEntfernen(id) {
    korbSchreiben(korbLesen().filter(function (p) { return p.id !== id; }));
  }

  function zaehlerSetzen() {
    var summe = 0;
    korbLesen().forEach(function (p) { summe += p.menge; });
    alle(document, '[data-wk-zaehler]').forEach(function (el) {
      el.textContent = String(summe);
      el.setAttribute('data-anzahl', String(summe));
    });
  }

  function korbGeaendert() {
    sicher(zaehlerSetzen);
    if (warenkorbAnsicht) { sicher(warenkorbAnsicht.zeichnen); }
    if (kasseAnsicht) { sicher(kasseAnsicht.korbGeaendert); }
  }

  /* Summen in einem Bereich setzen. versandPreis gilt nur, wenn der Korb nicht leer ist. */
  function summenSetzen(bereich, versandPreis) {
    var pos = korbPositionen();
    var zwischen = 0;
    pos.forEach(function (p) { zwischen += cent(NACH_ID[p.id].preis) * p.menge; });
    var versand = pos.length ? cent(versandPreis) : 0;
    var gesamt = zwischen + versand;
    var mwst = Math.round(gesamt - gesamt / (1 + MWST / 100));
    var werte = {
      '[data-wk-zwischensumme]': zwischen,
      '[data-wk-versand]': versand,
      '[data-wk-gesamt]': gesamt,
      '[data-wk-mwst]': mwst
    };
    Object.keys(werte).forEach(function (sel) {
      alle(bereich, sel).forEach(function (el) { el.textContent = preis(werte[sel] / 100); });
    });
    alle(bereich, '.wk-summe__mwst dt').forEach(function (dt) {
      dt.textContent = 'enthaltene MwSt. (' + MWST + ' %)';
    });
  }

  function artikelName(id, ausloeser) {
    if (NACH_ID[id]) { return NACH_ID[id].name; }
    var karte = ausloeser && ausloeser.closest ? ausloeser.closest('[data-name]') : null;
    return karte ? karte.getAttribute('data-name') : 'Der Artikel';
  }

  function hinzugefuegtMelden(id, menge, ergebnis, ausloeser) {
    var name = artikelName(id, ausloeser);
    var satz;
    if (ergebnis.gekappt) {
      satz = 'Von ' + name + ' liegen jetzt ' + ergebnis.nachher + ' Stück im Warenkorb, das ist die Höchstmenge.';
    } else if (menge > 1) {
      satz = name + ' (' + menge + ' Stück) wurde in den Warenkorb gelegt.';
    } else {
      satz = name + ' wurde in den Warenkorb gelegt.';
    }
    meldung('<span>' + text(satz) + '</span> <a href="' + esc(ROOT + 'warenkorb/') + '">Zum Warenkorb</a>');
  }

  function einkaufenBinden() {
    document.addEventListener('click', function (e) {
      var ziel = e.target && e.target.closest ? e.target : null;
      if (!ziel) { return; }

      var add = ziel.closest('[data-wk-add]');
      if (add) {
        e.preventDefault();
        var id = add.getAttribute('data-wk-add');
        var ergebnis = korbHinzufuegen(id, 1);
        hinzugefuegtMelden(id, 1, ergebnis, add);
        return;
      }

      var minus = ziel.closest('[data-menge-minus]');
      var plus = ziel.closest('[data-menge-plus]');
      if (minus || plus) {
        var menge = (minus || plus).closest('.menge');
        var feld = menge ? menge.querySelector('.menge__feld, input') : null;
        if (!feld) { return; }
        var wert = mengeBegrenzen(feld.value) + (plus ? 1 : -1);
        feld.value = String(mengeBegrenzen(wert));
        ansage('Menge ' + feld.value);
      }
    });

    document.addEventListener('submit', function (e) {
      var form = e.target;
      if (!form || !form.hasAttribute || !form.hasAttribute('data-wk-form')) { return; }
      e.preventDefault();
      var id = form.getAttribute('data-wk-form');
      var feld = form.querySelector('[name="menge"]');
      var menge = mengeBegrenzen(feld ? feld.value : 1);
      if (feld) { feld.value = String(menge); }
      var ergebnis = korbHinzufuegen(id, menge);
      hinzugefuegtMelden(id, menge, ergebnis, form);
    });

    /* Mengenfelder außerhalb des Warenkorbs auf 1 bis 99 begrenzen. */
    document.addEventListener('change', function (e) {
      var feld = e.target;
      if (!feld || !feld.classList || !feld.classList.contains('menge__feld') || feld.hasAttribute('data-wk-menge')) { return; }
      feld.value = String(mengeBegrenzen(feld.value));
    });

    window.addEventListener('storage', function (e) {
      if (e.key === KORB_SCHLUESSEL || e.key === null) {
        korbNotfall = null;
        korbGeaendert();
      }
    });
  }

  /* ---------- Warenkorbseite ---------- */

  function positionHtml(a) {
    var id = esc(a.id);
    var name = esc(a.name);
    var bild = a.bild && a.bild.src
      ? '<img class="wk-position__bild" src="' + esc(ROOT + a.bild.src) + '" width="' + esc(a.bild.w || 400) +
        '" height="' + esc(a.bild.h || 300) + '" alt="">'
      : '<span class="bildrahmen wk-position__bild" aria-hidden="true"><svg class="ico" aria-hidden="true"><use href="#i-display"></use></svg></span>';
    return '<li class="wk-position" data-id="' + id + '">' + bild +
      '<div class="wk-position__text"><a class="wk-position__name" href="' + esc(ROOT + a.url) + '">' + text(a.name) + '</a>' +
      (a.teilenummer ? '<p class="wk-position__nummer teilenummer">' + esc(a.teilenummer) + '</p>' : '') +
      '<p class="wk-position__einzel">Einzelpreis ' + preis(a.preis) + '</p></div>' +
      '<div class="menge"><button class="menge__knopf" type="button" data-wk-minus aria-label="Menge von ' + name + ' verringern">' +
      '<svg class="ico" aria-hidden="true"><use href="#i-minus"></use></svg></button>' +
      '<label class="sr-only" for="wk-menge-' + id + '">Menge von ' + name + '</label>' +
      '<input class="menge__feld eingabe" id="wk-menge-' + id + '" type="number" inputmode="numeric" min="1" max="99" value="1" data-wk-menge>' +
      '<button class="menge__knopf" type="button" data-wk-plus aria-label="Menge von ' + name + ' erhöhen">' +
      '<svg class="ico" aria-hidden="true"><use href="#i-plus"></use></svg></button></div>' +
      '<p class="wk-position__summe preis"></p>' +
      '<button class="knopf-text wk-position__entfernen" type="button" data-wk-entfernen aria-label="' + name + ' entfernen">' +
      '<svg class="ico" aria-hidden="true"><use href="#i-x"></use></svg><span>Entfernen</span></button>' +
      '</li>';
  }

  function warenkorbSeite(wurzel) {
    var leer = wurzel.querySelector('[data-wk-leer]');
    var inhalt = wurzel.querySelector('[data-wk-inhalt]');
    var liste = wurzel.querySelector('[data-wk-liste]');
    if (!liste) { return null; }
    var vorlage = document.createElement('ul');

    function zeichnen() {
      var pos = korbPositionen();
      var istLeer = pos.length === 0;
      if (leer) { leer.hidden = !istLeer; }
      if (inhalt) { inhalt.hidden = istLeer; }

      var vorhanden = {};
      alle(liste, ':scope > .wk-position').forEach(function (li) { vorhanden[li.getAttribute('data-id')] = li; });
      var vorher = null;
      pos.forEach(function (p) {
        var a = NACH_ID[p.id];
        var li = vorhanden[p.id];
        if (li) {
          delete vorhanden[p.id];
        } else {
          vorlage.innerHTML = positionHtml(a);
          li = vorlage.firstElementChild;
        }
        var feld = li.querySelector('[data-wk-menge]');
        if (feld && String(parseInt(feld.value, 10)) !== String(p.menge)) { feld.value = String(p.menge); }
        var summe = li.querySelector('.wk-position__summe');
        if (summe) { summe.textContent = preis(cent(a.preis) * p.menge / 100); }
        var soll = vorher ? vorher.nextElementSibling : liste.firstElementChild;
        if (soll !== li) { liste.insertBefore(li, soll); }
        vorher = li;
      });
      Object.keys(vorhanden).forEach(function (id) { vorhanden[id].parentNode.removeChild(vorhanden[id]); });

      summenSetzen(wurzel, VERSAND.length ? VERSAND[0].preis : 0);
      var versandDt = wurzel.querySelector('[data-wk-versand]');
      if (versandDt && VERSAND.length && versandDt.previousElementSibling) {
        versandDt.previousElementSibling.textContent = 'Versand (' + VERSAND[0].name + ')';
      }
    }

    function idVon(el) {
      var li = el.closest('.wk-position');
      return li ? li.getAttribute('data-id') : null;
    }

    function mengeAendern(id, menge) {
      var neu = mengeBegrenzen(menge);
      korbMengeSetzen(id, neu);
      ansage('Menge von ' + artikelName(id) + ' ist jetzt ' + neu + '.', 300);
    }

    wurzel.addEventListener('click', function (e) {
      var el = e.target.closest ? e.target.closest('[data-wk-minus], [data-wk-plus], [data-wk-entfernen]') : null;
      if (!el || !wurzel.contains(el)) { return; }
      var id = idVon(el);
      if (!id) { return; }
      if (el.hasAttribute('data-wk-entfernen')) {
        var li = el.closest('.wk-position');
        var naechste = li.nextElementSibling || li.previousElementSibling;
        var naechsteId = naechste ? naechste.getAttribute('data-id') : null;
        var name = artikelName(id);
        korbEntfernen(id);
        var ziel = naechsteId ? liste.querySelector('.wk-position[data-id="' + cssWert(naechsteId) + '"] .wk-position__name') : null;
        if (ziel) {
          fokus(ziel);
        } else if (leer) {
          fokus(leer.querySelector('h2, h3') || leer);
        }
        meldung('<span>' + text(name + ' wurde aus dem Warenkorb entfernt.') + '</span>');
        return;
      }
      var feld = el.closest('.wk-position').querySelector('[data-wk-menge]');
      var aktuell = mengeBegrenzen(feld ? feld.value : 1);
      mengeAendern(id, aktuell + (el.hasAttribute('data-wk-plus') ? 1 : -1));
    });

    wurzel.addEventListener('change', function (e) {
      var feld = e.target;
      if (!feld.hasAttribute || !feld.hasAttribute('data-wk-menge')) { return; }
      var id = idVon(feld);
      var neu = mengeBegrenzen(feld.value);
      feld.value = String(neu);
      if (id) { mengeAendern(id, neu); }
    });

    wurzel.addEventListener('keydown', function (e) {
      var feld = e.target;
      if (e.key !== 'Enter' || !feld.hasAttribute || !feld.hasAttribute('data-wk-menge')) { return; }
      e.preventDefault();
      var id = idVon(feld);
      var neu = mengeBegrenzen(feld.value);
      feld.value = String(neu);
      if (id) { mengeAendern(id, neu); }
    });

    zeichnen();
    return { zeichnen: zeichnen };
  }

  /* ---------- Validierung ---------- */

  function labelText(el) {
    var label = null;
    if (el.id) { label = document.querySelector('label[for="' + cssWert(el.id) + '"]'); }
    if (!label) { label = el.closest('label'); }
    if (!label) { return el.name || ''; }
    var kopie = label.cloneNode(true);
    alle(kopie, '.feld__pflicht, .feld__optional, .sr-only, input, select, textarea').forEach(function (k) {
      k.parentNode.removeChild(k);
    });
    return kopie.textContent.replace(/\s+/g, ' ').trim();
  }

  function legendText(gruppe) {
    var legend = gruppe.querySelector('legend');
    if (!legend) { return ''; }
    var kopie = legend.cloneNode(true);
    alle(kopie, '.feld__pflicht, .feld__optional').forEach(function (k) { k.parentNode.removeChild(k); });
    return kopie.textContent.replace(/\s+/g, ' ').trim();
  }

  function fehlerElementFuer(el) {
    var ids = (el.getAttribute('aria-describedby') || '').split(/\s+/);
    for (var i = 0; i < ids.length; i += 1) {
      var kandidat = ids[i] ? document.getElementById(ids[i]) : null;
      if (kandidat && kandidat.classList.contains('feld__fehler')) { return kandidat; }
    }
    return el.id ? document.getElementById(el.id + '-fehler') : null;
  }

  function versteckt(el, bereich) {
    var h = el.closest('[hidden]');
    return !!h && h !== bereich && bereich.contains(h);
  }

  function feldMeldung(el) {
    var wert = String(el.value || '').trim();
    var eigene = el.getAttribute('data-fehler');
    var name = labelText(el);
    if (el.type === 'checkbox') {
      if (el.required && !el.checked) { return eigene || 'Bitte bestätigen Sie „' + name + '“.'; }
      return '';
    }
    if (!wert) {
      if (el.required) { return eigene || 'Bitte füllen Sie das Feld „' + name + '“ aus.'; }
      return '';
    }
    if (el.type === 'email' && !EMAIL_MUSTER.test(wert)) {
      return eigene || 'Bitte geben Sie eine gültige E-Mail-Adresse an.';
    }
    var muster = el.getAttribute('pattern');
    if (muster) {
      var passt = true;
      try { passt = new RegExp('^(?:' + muster + ')$').test(wert); } catch (e) { passt = true; }
      if (!passt) { return eigene || 'Bitte prüfen Sie die Eingabe im Feld „' + name + '“.'; }
    }
    return '';
  }

  function gruppeMeldung(gruppe) {
    var felder = alle(gruppe, 'input[type="checkbox"], input[type="radio"]');
    var gewaehlt = felder.some(function (f) { return f.checked; });
    if (gewaehlt) { return ''; }
    var eigene = gruppe.getAttribute('data-fehler');
    if (eigene) { return eigene; }
    var radios = felder.length && felder[0].type === 'radio';
    return 'Bitte wählen Sie ' + (radios ? 'eine Angabe' : 'mindestens eine Angabe') + ' bei „' + legendText(gruppe) + '“.';
  }

  function radioMeldung(radios, bereich) {
    if (radios.some(function (r) { return r.checked; })) { return ''; }
    if (!radios.some(function (r) { return r.required; })) { return ''; }
    var eigene = radios[0].getAttribute('data-fehler');
    if (eigene) { return eigene; }
    var name = radios[0].name;
    if (name === 'versand') { return 'Bitte wählen Sie eine Versandart.'; }
    if (name === 'zahlung') { return 'Bitte wählen Sie eine Zahlart.'; }
    var gruppe = radios[0].closest('fieldset');
    return 'Bitte wählen Sie eine Angabe bei „' + (gruppe ? legendText(gruppe) : (bereich && legendText(bereich)) || name) + '“.';
  }

  /* Liefert alle Prüfpunkte eines Bereichs in Dokumentreihenfolge. */
  function pruefpunkte(bereich) {
    var punkte = [];
    var gesehen = [];
    alle(bereich, 'input, select, textarea').forEach(function (el) {
      if (el.disabled || el.type === 'hidden' || el.type === 'submit' || el.type === 'button' || el.type === 'reset') { return; }
      if (versteckt(el, bereich)) { return; }
      var gruppe = el.closest('[data-pflicht-gruppe]');
      if (gruppe && bereich.contains(gruppe)) {
        if (gesehen.indexOf(gruppe) !== -1) { return; }
        gesehen.push(gruppe);
        punkte.push({
          markiert: [gruppe],
          fehlerEl: gruppe.querySelector('.feld__fehler') || fehlerElementFuer(gruppe),
          ziel: gruppe.querySelector('input, select, textarea'),
          meldung: function () { return gruppeMeldung(gruppe); }
        });
        return;
      }
      if (el.type === 'radio') {
        var schluessel = 'radio:' + el.name;
        if (gesehen.indexOf(schluessel) !== -1) { return; }
        gesehen.push(schluessel);
        var radios = alle(bereich, 'input[type="radio"][name="' + cssWert(el.name) + '"]').filter(function (r) {
          return !versteckt(r, bereich);
        });
        punkte.push({
          markiert: radios,
          fehlerEl: fehlerElementFuer(radios[0]),
          ziel: radios[0],
          meldung: function () { return radioMeldung(radios, bereich); }
        });
        return;
      }
      punkte.push({
        markiert: [el],
        fehlerEl: fehlerElementFuer(el),
        ziel: el,
        meldung: function () { return feldMeldung(el); }
      });
    });
    return punkte;
  }

  function punktMarkieren(punkt, satz) {
    punkt.markiert.forEach(function (el) {
      if (satz) { el.setAttribute('aria-invalid', 'true'); } else { el.removeAttribute('aria-invalid'); }
    });
    if (punkt.fehlerEl) {
      punkt.fehlerEl.textContent = satz || '';
      punkt.fehlerEl.hidden = !satz;
    }
  }

  function fehlerlisteEntfernen(bereich) {
    alle(bereich, '[data-fehlerliste]').forEach(function (l) {
      if (l.parentNode) { l.parentNode.removeChild(l); }
    });
  }

  function fehlerlisteZeigen(bereich, fehler) {
    fehlerlisteEntfernen(bereich);
    var box = document.createElement('div');
    box.className = 'fehlerliste';
    box.setAttribute('role', 'alert');
    box.setAttribute('tabindex', '-1');
    box.setAttribute('data-fehlerliste', '');
    var titel = 'Bitte korrigieren Sie ' + (fehler.length === 1 ? 'eine Angabe.' : fehler.length + ' Angaben.');
    box.innerHTML = '<p>' + esc(titel) + '</p><ul>' + fehler.map(function (f) {
      if (!f.ziel.id) { f.ziel.id = neueId('feld'); }
      return '<li data-fuer="' + esc(f.ziel.id) + '"><a href="#' + esc(f.ziel.id) + '">' + esc(f.satz) + '</a></li>';
    }).join('') + '</ul>';
    var erstes = bereich.firstElementChild;
    if (erstes && /^(LEGEND|H1|H2|H3)$/.test(erstes.tagName)) {
      erstes.parentNode.insertBefore(box, erstes.nextSibling);
    } else {
      bereich.insertBefore(box, erstes);
    }
    box.addEventListener('click', function (e) {
      var link = e.target.closest ? e.target.closest('a[href^="#"]') : null;
      if (!link) { return; }
      var ziel = document.getElementById(link.getAttribute('href').slice(1));
      if (ziel) {
        e.preventDefault();
        fokus(ziel);
      }
    });
    return box;
  }

  /* Prüft einen Bereich. Mit anzeigen=true werden Fehler markiert und die Fehlerliste fokussiert. */
  function bereichPruefen(bereich, anzeigen) {
    var fehler = [];
    pruefpunkte(bereich).forEach(function (punkt) {
      var satz = punkt.meldung();
      if (anzeigen) { punktMarkieren(punkt, satz); }
      if (satz) { fehler.push({ ziel: punkt.ziel, satz: satz }); }
    });
    if (anzeigen) {
      if (fehler.length) {
        fokus(fehlerlisteZeigen(bereich, fehler));
      } else {
        fehlerlisteEntfernen(bereich);
      }
    }
    return fehler.length === 0;
  }

  /* Bereits markierte Fehler beim Korrigieren sofort aufheben. */
  function liveKorrekturBinden(form) {
    function pruefen(e) {
      var el = e.target;
      if (!el || !el.closest) { return; }
      var bereich = el.closest('[data-schritt]') || form;
      var gruppe = el.closest('[data-pflicht-gruppe]');
      var betroffen = gruppe && gruppe.getAttribute('aria-invalid') === 'true';
      betroffen = betroffen || el.getAttribute('aria-invalid') === 'true';
      if (!betroffen) { return; }
      pruefpunkte(bereich).forEach(function (punkt) {
        if (punkt.markiert.indexOf(el) === -1 && punkt.markiert.indexOf(gruppe) === -1) { return; }
        if (punkt.meldung()) { return; }
        punktMarkieren(punkt, '');
        alle(bereich, '[data-fehlerliste] li[data-fuer="' + cssWert(punkt.ziel.id || '') + '"]').forEach(function (li) {
          var liste = li.closest('[data-fehlerliste]');
          li.parentNode.removeChild(li);
          if (liste && !liste.querySelector('li')) { liste.parentNode.removeChild(liste); }
        });
      });
    }
    form.addEventListener('input', pruefen);
    form.addEventListener('change', pruefen);
  }

  /* ---------- Schritte (Kasse und Anfrage) ---------- */

  function schrittMaschine(form, optionen) {
    var schritte = alle(form, '[data-schritt]').sort(function (a, b) {
      return Number(a.getAttribute('data-schritt')) - Number(b.getAttribute('data-schritt'));
    });
    var anzeigen = alle(form, '[data-schritt-anzeige]');
    var leiste = form.querySelector('.schritte');
    var aktuell = 1;
    var letzter = schritte.length ? Number(schritte[schritte.length - 1].getAttribute('data-schritt')) : 1;

    function schritt(n) {
      for (var i = 0; i < schritte.length; i += 1) {
        if (Number(schritte[i].getAttribute('data-schritt')) === n) { return schritte[i]; }
      }
      return null;
    }

    function zeige(n, mitFokus) {
      n = Math.max(1, Math.min(letzter, n));
      aktuell = n;
      schritte.forEach(function (s) { s.hidden = Number(s.getAttribute('data-schritt')) !== n; });
      anzeigen.forEach(function (li) {
        var m = Number(li.getAttribute('data-schritt-anzeige'));
        if (m === n) { li.setAttribute('aria-current', 'step'); } else { li.removeAttribute('aria-current'); }
        li.classList.toggle('ist-erledigt', m < n);
      });
      if (optionen && optionen.beimZeigen) { optionen.beimZeigen(n); }
      if (mitFokus) {
        var el = schritt(n);
        var titel = el ? (el.querySelector('.schritt__titel') || el.querySelector('legend') || el) : null;
        if (leiste && leiste.getBoundingClientRect().top < 0) {
          try { leiste.scrollIntoView({ block: 'start' }); } catch (e) { leiste.scrollIntoView(true); }
        }
        if (titel) {
          titel.setAttribute('tabindex', '-1');
          try { titel.focus({ preventScroll: !!(leiste && leiste.getBoundingClientRect().top >= 0) }); } catch (e) { titel.focus(); }
        }
      }
    }

    function weiter() {
      var el = schritt(aktuell);
      if (el && !bereichPruefen(el, true)) { return false; }
      if (aktuell < letzter) { zeige(aktuell + 1, true); }
      return true;
    }

    form.addEventListener('click', function (e) {
      var knopf = e.target.closest ? e.target.closest('[data-weiter], [data-zurueck], [data-gehe-zu]') : null;
      if (!knopf || !form.contains(knopf)) { return; }
      e.preventDefault();
      if (knopf.hasAttribute('data-weiter')) {
        weiter();
      } else if (knopf.hasAttribute('data-zurueck')) {
        zeige(aktuell - 1, true);
      } else {
        var ziel = Number(knopf.getAttribute('data-gehe-zu'));
        if (ziel >= 1 && ziel <= aktuell) { zeige(ziel, true); }
      }
    });

    return {
      zeige: zeige,
      weiter: weiter,
      schritt: schritt,
      aktuell: function () { return aktuell; },
      letzter: letzter
    };
  }

  /* ---------- Kasse ---------- */

  function kasseSeite(form) {
    var leer = document.querySelector('[data-kasse-leer]');
    var bestellen = alle(form, 'button[type="submit"], input[type="submit"]');
    var lieferUmschalter = form.querySelector('[data-lieferadresse-umschalter]');
    var lieferBereich = form.querySelector('[data-lieferadresse]');
    var bereit = false;

    function sperren() {
      bestellen.forEach(function (k) {
        k.disabled = true;
        k.setAttribute('aria-disabled', 'true');
      });
    }

    function wert(name) {
      var el = form.elements[name];
      if (!el) { return ''; }
      if (el.type === 'checkbox') { return el.checked; }
      return String(el.value || '').trim();
    }

    function gewaehlt(name) {
      var el = form.querySelector('input[name="' + name + '"]:checked');
      return el ? el.value : '';
    }

    function gewaehlterVersand() {
      return versandNach(gewaehlt('versand')) || VERSAND[0] || null;
    }

    function summen() {
      var v = gewaehlterVersand();
      summenSetzen(form, v ? v.preis : 0);
      var dd = form.querySelector('[data-wk-versand]');
      if (dd && v && dd.previousElementSibling) { dd.previousElementSibling.textContent = 'Versand (' + v.name + ')'; }
    }

    function lieferadresseZeigen() {
      if (lieferUmschalter && lieferBereich) { lieferBereich.hidden = !lieferUmschalter.checked; }
    }

    function zeilen(liste) {
      return '<p>' + liste.filter(function (z) { return z; }).map(text).join('<br>') + '</p>';
    }

    function uebersichtFuellen() {
      var adresse = form.querySelector('[data-uebersicht-adresse]');
      if (adresse) {
        var html = zeilen([
          (wert('vorname') + ' ' + wert('nachname')).trim(),
          wert('firma'),
          wert('strasse'),
          (wert('plz') + ' ' + wert('ort')).trim(),
          wert('land'),
          wert('email'),
          wert('telefon') ? 'Telefon ' + wert('telefon') : ''
        ]);
        if (wert('liefer_abweichend')) {
          html += '<p><strong>Lieferadresse</strong></p>' + zeilen([
            (wert('liefer_vorname') + ' ' + wert('liefer_nachname')).trim(),
            wert('liefer_strasse'),
            (wert('liefer_plz') + ' ' + wert('liefer_ort')).trim()
          ]);
        }
        adresse.innerHTML = html;
      }
      var versand = form.querySelector('[data-uebersicht-versand]');
      if (versand) {
        var v = gewaehlterVersand();
        versand.innerHTML = v ? '<p>' + text(v.name) + ', ' + esc(preis(v.preis)) + '</p>' : '<p>Keine Versandart gewählt</p>';
      }
      var zahlung = form.querySelector('[data-uebersicht-zahlung]');
      if (zahlung) {
        var z = zahlartNach(gewaehlt('zahlung'));
        zahlung.innerHTML = z ? '<p>' + text(z.name) + '</p>' : '<p>Keine Zahlart gewählt</p>';
      }
      var positionen = form.querySelector('[data-uebersicht-positionen]');
      if (positionen) {
        positionen.innerHTML = korbPositionen().map(function (p) {
          var a = NACH_ID[p.id];
          return '<li><span>' + p.menge + ' × ' + text(a.name) + '</span><span class="preis">' +
            esc(preis(cent(a.preis) * p.menge / 100)) + '</span></li>';
        }).join('');
      }
      summen();
    }

    function speichern() {
      if (!bereit) { return; }
      var werte = {};
      alle(form, 'input[name], select[name], textarea[name]').forEach(function (el) {
        if (el.name === 'agb' || el.type === 'submit' || el.type === 'button') { return; }
        if (el.type === 'radio') {
          if (el.checked) { werte[el.name] = el.value; }
        } else if (el.type === 'checkbox') {
          werte[el.name] = el.checked;
        } else {
          werte[el.name] = el.value;
        }
      });
      speicherSchreiben('sessionStorage', KASSE_SCHLUESSEL, JSON.stringify({ v: 1, schritt: maschine.aktuell(), werte: werte }));
    }

    function wiederherstellen() {
      var roh = speicherLesen('sessionStorage', KASSE_SCHLUESSEL);
      if (!roh) { return 1; }
      var daten = null;
      try { daten = JSON.parse(roh); } catch (e) { daten = null; }
      if (!daten || !daten.werte || typeof daten.werte !== 'object') { return 1; }
      Object.keys(daten.werte).forEach(function (name) {
        var w = daten.werte[name];
        alle(form, '[name="' + cssWert(name) + '"]').forEach(function (el) {
          if (el.name === 'agb') { return; }
          if (el.type === 'radio') {
            el.checked = el.value === w;
          } else if (el.type === 'checkbox') {
            el.checked = w === true;
          } else if (typeof w === 'string') {
            el.value = w;
          }
        });
      });
      return Number(daten.schritt) || 1;
    }

    var maschine = schrittMaschine(form, {
      beimZeigen: function (n) {
        if (n === 4) { uebersichtFuellen(); }
        sperren();
        speichern();
      }
    });

    function korbGeaendert() {
      var istLeer = korbPositionen().length === 0;
      if (leer) { leer.hidden = !istLeer; }
      form.hidden = istLeer;
      summen();
      if (maschine.aktuell() === 4) { uebersichtFuellen(); }
    }

    form.addEventListener('submit', function (e) {
      e.preventDefault();
      sperren();
      if (maschine.aktuell() < maschine.letzter) { maschine.weiter(); }
    });

    form.addEventListener('change', function (e) {
      var el = e.target;
      if (el === lieferUmschalter) { lieferadresseZeigen(); }
      if (el.name === 'versand') { summen(); }
      if (el.name === 'agb') { sperren(); }
      speichern();
    });

    form.addEventListener('input', speichern);

    form.addEventListener('keydown', function (e) {
      if (e.key !== 'Enter') { return; }
      var el = e.target;
      if (!el || el.tagName === 'TEXTAREA' || el.tagName === 'BUTTON' || el.tagName === 'A' || el.tagName === 'SELECT') { return; }
      if (el.tagName !== 'INPUT') { return; }
      e.preventDefault();
      if (maschine.aktuell() < maschine.letzter) { maschine.weiter(); }
    });

    liveKorrekturBinden(form);
    sperren();

    var ziel = wiederherstellen();
    lieferadresseZeigen();
    for (var n = 1; n < ziel; n += 1) {
      var el = maschine.schritt(n);
      if (el && !bereichPruefen(el, false)) {
        ziel = n;
        break;
      }
    }
    bereit = true;
    maschine.zeige(ziel, false);
    korbGeaendert();

    return { korbGeaendert: korbGeaendert };
  }

  /* ---------- Formulare (Kontakt, Anfrage) ---------- */

  function zusammenfassungHtml(form) {
    var zeilenListe = [];
    var gruppen = [];
    alle(form, 'input[name], select[name], textarea[name]').forEach(function (el) {
      if (el.type === 'submit' || el.type === 'button' || el.type === 'hidden') { return; }
      if (el.name === 'datenschutz' || el.name === 'agb') { return; }
      if (el.type === 'radio' || el.type === 'checkbox') {
        var gruppe = el.closest('.feld-gruppe') || el.closest('fieldset');
        var schluessel = el.name;
        if (gruppen.indexOf(schluessel) !== -1) { return; }
        gruppen.push(schluessel);
        var gewaehlt = alle(form, 'input[name="' + cssWert(el.name) + '"]:checked').map(function (f) {
          return labelText(f);
        });
        if (gewaehlt.length) {
          zeilenListe.push([gruppe ? legendText(gruppe) : labelText(el), gewaehlt.join(', ')]);
        }
        return;
      }
      var wertText = el.tagName === 'SELECT' && el.selectedIndex >= 0 ? el.options[el.selectedIndex].text : el.value;
      wertText = String(wertText || '').trim();
      if (!wertText || (el.tagName === 'SELECT' && !el.value)) { return; }
      zeilenListe.push([labelText(el), wertText]);
    });
    if (!zeilenListe.length) { return ''; }
    return '<h3 class="sr-only">Ihre Angaben</h3><dl>' + zeilenListe.map(function (z) {
      return '<dt>' + esc(z[0]) + '</dt><dd>' + esc(z[1]).replace(/\n/g, '<br>') + '</dd>';
    }).join('') + '</dl>';
  }

  function erfolgZeigen(form) {
    var erfolg = null;
    var eltern = form.parentNode;
    if (eltern) {
      erfolg = alle(eltern, ':scope > [data-formular-erfolg]')[0] || eltern.querySelector('[data-formular-erfolg]');
    }
    if (!erfolg) { return; }
    var ziel = erfolg.querySelector('[data-erfolg-zusammenfassung]');
    if (ziel) { ziel.innerHTML = zusammenfassungHtml(form); }
    fehlerlisteEntfernen(form);
    form.hidden = true;
    erfolg.hidden = false;
    if (!erfolg.hasAttribute('tabindex')) { erfolg.setAttribute('tabindex', '-1'); }
    fokus(erfolg);
    try { erfolg.scrollIntoView({ block: 'start' }); } catch (e) { /* nichts */ }
  }

  function formular(form) {
    var maschine = null;
    if (form.hasAttribute('data-assistent')) {
      maschine = schrittMaschine(form, {});
      var p = urlParameter();
      var vorwahl = p ? String(p.get('hersteller') || '').toLowerCase().replace(/\s+/g, '') : '';
      if (vorwahl) {
        var radio = form.querySelector('input[name="hersteller"][value="' + cssWert(vorwahl) + '"]');
        if (radio) { radio.checked = true; }
      }
      maschine.zeige(1, false);
    }

    form.addEventListener('submit', function (e) {
      e.preventDefault();
      if (maschine) {
        if (maschine.aktuell() < maschine.letzter) {
          maschine.weiter();
          return;
        }
        if (!bereichPruefen(maschine.schritt(maschine.aktuell()), true)) { return; }
      } else if (!bereichPruefen(form, true)) {
        return;
      }
      erfolgZeigen(form);
    });

    liveKorrekturBinden(form);
  }

  /* ---------- Suche ---------- */

  function norm(wert) {
    var s = String(wert == null ? '' : wert).toLowerCase();
    try { s = s.normalize('NFD').replace(/[\u0300-\u036f]/g, ''); } catch (e) { /* nichts */ }
    return s.replace(/ß/g, 'ss').replace(/[\s\-\u2010\u2011_]+/g, '');
  }

  var heuhaufen = {};

  function heu(a) {
    if (!heuhaufen[a.id]) {
      heuhaufen[a.id] = [a.name, a.teilenummer, (a.modelle || []).join('|'), a.hersteller, a.kategorie_name]
        .map(norm).join('|');
    }
    return heuhaufen[a.id];
  }

  function suchen(anfrage) {
    var ganz = norm(anfrage);
    var woerter = String(anfrage || '').split(/\s+/).map(norm).filter(function (w) { return w; });
    if (!ganz || !woerter.length) { return []; }
    var treffer = [];
    ARTIKEL.forEach(function (a) {
      var h = heu(a);
      var passt = woerter.every(function (w) { return h.indexOf(w) !== -1; }) || h.indexOf(ganz) !== -1;
      if (!passt) { return; }
      var punkte = 0;
      var tn = norm(a.teilenummer);
      var nn = norm(a.name);
      if (tn && tn === ganz) { punkte += 100; } else if (tn && tn.indexOf(ganz) !== -1) { punkte += 60; }
      if (nn.indexOf(ganz) === 0) { punkte += 40; } else if (nn.indexOf(ganz) !== -1) { punkte += 20; }
      if (norm(a.hersteller) === ganz) { punkte += 10; }
      treffer.push({ a: a, punkte: punkte });
    });
    treffer.sort(function (x, y) {
      if (y.punkte !== x.punkte) { return y.punkte - x.punkte; }
      var rx = x.a.rang == null ? 999 : x.a.rang;
      var ry = y.a.rang == null ? 999 : y.a.rang;
      if (rx !== ry) { return rx - ry; }
      return x.a.name.localeCompare(y.a.name, 'de');
    });
    return treffer.map(function (t) { return t.a; });
  }

  function suchUrl(anfrage) {
    return ROOT + 'suche/?q=' + encodeURIComponent(String(anfrage || '').trim());
  }

  function combobox(form) {
    var feld = form.querySelector('input[role="combobox"]');
    if (!feld) { return; }
    var liste = document.getElementById(feld.getAttribute('aria-controls') || '') || form.querySelector('[role="listbox"]');

    form.addEventListener('submit', function (e) {
      if (!String(feld.value || '').trim()) {
        e.preventDefault();
        fokus(feld);
      }
    });

    if (!liste || !ARTIKEL.length) { return; }
    if (!feld.id) { feld.id = neueId('suche'); }
    var optionen = [];
    var aktiv = -1;

    function offen() { return !liste.hidden; }

    function schliessen() {
      liste.hidden = true;
      feld.setAttribute('aria-expanded', 'false');
      feld.removeAttribute('aria-activedescendant');
      aktiv = -1;
    }

    function setzeAktiv(i) {
      optionen.forEach(function (o, j) { o.setAttribute('aria-selected', j === i ? 'true' : 'false'); });
      aktiv = i;
      if (i >= 0 && optionen[i]) {
        feld.setAttribute('aria-activedescendant', optionen[i].id);
        try { optionen[i].scrollIntoView({ block: 'nearest' }); } catch (e) { /* nichts */ }
      } else {
        feld.removeAttribute('aria-activedescendant');
      }
    }

    function aktualisieren() {
      var anfrage = feld.value;
      if (norm(anfrage).length < SUCHE_MIN_ZEICHEN) {
        liste.innerHTML = '';
        optionen = [];
        schliessen();
        return;
      }
      var treffer = suchen(anfrage);
      var basis = feld.id + '-opt-';
      var html = treffer.slice(0, VORSCHLAEGE_MAX).map(function (a, i) {
        return '<li class="suche__vorschlag" role="option" id="' + esc(basis + i) + '" aria-selected="false" data-href="' +
          esc(ROOT + a.url) + '"><span class="suche__vorschlag-name">' + text(a.name) + '</span>' +
          (a.teilenummer ? '<span class="teilenummer">' + esc(a.teilenummer) + '</span>' : '') +
          '<span class="preis">' + esc(preis(a.preis)) + '</span></li>';
      });
      if (treffer.length) {
        var n = Math.min(treffer.length, VORSCHLAEGE_MAX);
        html.push('<li class="suche__vorschlag suche__vorschlag--alle" role="option" id="' + esc(basis + n) +
          '" aria-selected="false" data-href="' + esc(suchUrl(anfrage)) + '"><span class="suche__vorschlag-name">Alle Ergebnisse anzeigen</span>' +
          '<span class="suche__vorschlag-info">' + treffer.length + ' Treffer</span></li>');
        ansage(n === 1 ? 'Ein Vorschlag. Mit den Pfeiltasten auswählen.' : n + ' Vorschläge. Mit den Pfeiltasten auswählen.', 500);
      } else {
        html.push('<li class="suche__leer" role="option" id="' + esc(basis + 'leer') + '" aria-selected="false" aria-disabled="true">' +
          'Keine passenden Artikel gefunden</li>');
        ansage('Keine Vorschläge gefunden.', 500);
      }
      liste.innerHTML = html.join('');
      optionen = alle(liste, '[role="option"]:not([aria-disabled="true"])');
      aktiv = -1;
      feld.removeAttribute('aria-activedescendant');
      liste.hidden = false;
      feld.setAttribute('aria-expanded', 'true');
    }

    function oeffnen(option) {
      var ziel = option ? option.getAttribute('data-href') : '';
      if (ziel) {
        schliessen();
        window.location.href = ziel;
      }
    }

    feld.addEventListener('input', aktualisieren);

    feld.addEventListener('keydown', function (e) {
      if (e.key === 'ArrowDown' || e.key === 'Down') {
        e.preventDefault();
        if (!offen()) {
          aktualisieren();
          if (!offen()) { return; }
        }
        if (optionen.length) { setzeAktiv(aktiv + 1 >= optionen.length ? 0 : aktiv + 1); }
      } else if (e.key === 'ArrowUp' || e.key === 'Up') {
        if (!offen()) { return; }
        e.preventDefault();
        if (optionen.length) { setzeAktiv(aktiv <= 0 ? optionen.length - 1 : aktiv - 1); }
      } else if (e.key === 'Enter') {
        if (offen() && aktiv >= 0 && optionen[aktiv]) {
          e.preventDefault();
          oeffnen(optionen[aktiv]);
        } else {
          schliessen();
        }
      } else if (e.key === 'Escape' || e.key === 'Esc') {
        if (offen()) {
          e.preventDefault();
          e.stopPropagation();
          schliessen();
        }
      } else if (e.key === 'Tab') {
        schliessen();
      }
    });

    liste.addEventListener('mousedown', function (e) { e.preventDefault(); });
    liste.addEventListener('click', function (e) {
      var option = e.target.closest ? e.target.closest('[role="option"]') : null;
      if (option && option.getAttribute('aria-disabled') !== 'true') { oeffnen(option); }
    });
    liste.addEventListener('mousemove', function (e) {
      var option = e.target.closest ? e.target.closest('[role="option"]') : null;
      var i = option ? optionen.indexOf(option) : -1;
      if (i >= 0 && i !== aktiv) { setzeAktiv(i); }
    });

    form.addEventListener('focusout', function (e) {
      if (!e.relatedTarget || !form.contains(e.relatedTarget)) { schliessen(); }
    });
    document.addEventListener('click', function (e) {
      if (offen() && !form.contains(e.target)) { schliessen(); }
    });
    schliessen();
  }

  function suchseite(wurzel) {
    var p = urlParameter();
    var anfrage = p ? String(p.get('q') || '').trim() : '';
    var feld = wurzel.querySelector('#suche-seite') || wurzel.querySelector('input[name="q"]');
    var anzahl = wurzel.querySelector('[data-suchanzahl]');
    var raster = wurzel.querySelector('[data-suchergebnisse]');
    var leer = wurzel.querySelector('[data-suche-leer]');
    if (feld && anfrage) { feld.value = anfrage; }
    if (!raster) { return; }

    if (!anfrage) {
      raster.innerHTML = '';
      if (leer) { leer.hidden = true; }
      if (anzahl) { anzahl.textContent = 'Bitte geben Sie einen Suchbegriff ein, zum Beispiel ein Modell oder eine Teilenummer.'; }
      return;
    }
    var treffer = suchen(anfrage);
    raster.innerHTML = treffer.map(function (a) { return karteHtml(a, 'h2'); }).join('');
    raster.hidden = treffer.length === 0;
    if (leer) { leer.hidden = treffer.length > 0; }
    if (anzahl) {
      anzahl.textContent = treffer.length === 0
        ? 'Keine Treffer für „' + anfrage + '“'
        : (treffer.length === 1 ? '1 Treffer' : treffer.length + ' Treffer') + ' für „' + anfrage + '“';
    }
    try {
      var titel = document.title.split(' | ');
      document.title = 'Suche nach „' + anfrage + '“' + (titel.length > 1 ? ' | ' + titel[titel.length - 1] : '');
    } catch (e) { /* nichts */ }
  }

  /* ---------- Katalog: Filter und Sortierung ---------- */

  function katalog(wurzel) {
    var form = wurzel.querySelector('form[data-filter]');
    var raster = wurzel.querySelector('[data-katalog-raster]');
    var anzahl = wurzel.querySelector('[data-katalog-anzahl]');
    var leer = wurzel.querySelector('[data-katalog-leer]');
    var sortierung = wurzel.querySelector('[data-sortierung]');
    if (!raster) { return; }
    var karten = alle(raster, '.produkt');
    var reihenfolge = karten.slice();

    function zahl(name) {
      var el = form ? form.querySelector('[name="' + name + '"]') : null;
      if (!el || String(el.value).trim() === '') { return null; }
      var n = parseFloat(String(el.value).replace(',', '.'));
      return isNaN(n) ? null : n;
    }

    function gewaehlt(name) {
      return form ? alle(form, 'input[name="' + name + '"]:checked').map(function (el) { return el.value; }) : [];
    }

    function zustand() {
      var lieferbar = form ? form.querySelector('input[name="lieferbar"]') : null;
      return {
        kategorie: gewaehlt('kategorie'),
        hersteller: gewaehlt('hersteller'),
        zustand: gewaehlt('zustand'),
        preis_min: zahl('preis_min'),
        preis_max: zahl('preis_max'),
        lieferbar: !!(lieferbar && lieferbar.checked),
        sort: sortierung ? sortierung.value : 'empfehlung'
      };
    }

    function passt(karte, z) {
      if (z.kategorie.length && z.kategorie.indexOf(karte.getAttribute('data-kategorie')) === -1) { return false; }
      if (z.hersteller.length && z.hersteller.indexOf(karte.getAttribute('data-hersteller')) === -1) { return false; }
      if (z.zustand.length && z.zustand.indexOf(karte.getAttribute('data-zustand')) === -1) { return false; }
      var p = parseFloat(karte.getAttribute('data-preis'));
      if (z.preis_min !== null && !(p >= z.preis_min)) { return false; }
      if (z.preis_max !== null && !(p <= z.preis_max)) { return false; }
      if (z.lieferbar && karte.getAttribute('data-verfuegbar') !== '1') { return false; }
      return true;
    }

    function vergleich(art) {
      return function (a, b) {
        var ergebnis = 0;
        if (art === 'preis-auf' || art === 'preis-ab') {
          ergebnis = parseFloat(a.getAttribute('data-preis')) - parseFloat(b.getAttribute('data-preis'));
          if (art === 'preis-ab') { ergebnis = -ergebnis; }
        } else if (art === 'name') {
          ergebnis = String(a.getAttribute('data-name')).localeCompare(String(b.getAttribute('data-name')), 'de', { sensitivity: 'base', numeric: true });
        } else {
          ergebnis = (parseFloat(a.getAttribute('data-rang')) || 999) - (parseFloat(b.getAttribute('data-rang')) || 999);
        }
        return ergebnis || reihenfolge.indexOf(a) - reihenfolge.indexOf(b);
      };
    }

    function urlSchreiben(z) {
      if (!window.history || !window.history.replaceState) { return; }
      var p = urlParameter() || new URLSearchParams();
      KATALOG_PARAMETER.forEach(function (k) { p.delete(k); });
      ['kategorie', 'hersteller', 'zustand'].forEach(function (k) {
        z[k].forEach(function (w) { p.append(k, w); });
      });
      if (z.preis_min !== null) { p.set('preis_min', String(z.preis_min)); }
      if (z.preis_max !== null) { p.set('preis_max', String(z.preis_max)); }
      if (z.lieferbar) { p.set('lieferbar', '1'); }
      if (z.sort && z.sort !== 'empfehlung') { p.set('sort', z.sort); }
      var qs = p.toString();
      try {
        window.history.replaceState(window.history.state, '', window.location.pathname + (qs ? '?' + qs : '') + window.location.hash);
      } catch (e) { /* nichts */ }
    }

    function anwenden(schreiben) {
      var z = zustand();
      var sichtbar = 0;
      karten.forEach(function (k) {
        var ok = passt(k, z);
        k.hidden = !ok;
        if (ok) { sichtbar += 1; }
      });
      karten.slice().sort(vergleich(z.sort)).forEach(function (k) { raster.appendChild(k); });
      if (anzahl) { anzahl.textContent = sichtbar + ' Artikel'; }
      if (leer) { leer.hidden = sichtbar > 0; }
      raster.hidden = sichtbar === 0;
      if (schreiben) { urlSchreiben(z); }
    }

    function ausUrlLesen() {
      var p = urlParameter();
      if (!p) { return; }
      ['kategorie', 'hersteller', 'zustand'].forEach(function (k) {
        var werte = p.getAll(k).map(function (w) { return w.toLowerCase(); });
        if (!werte.length || !form) { return; }
        alle(form, 'input[name="' + k + '"]').forEach(function (el) {
          el.checked = werte.indexOf(String(el.value).toLowerCase()) !== -1;
        });
      });
      ['preis_min', 'preis_max'].forEach(function (k) {
        var el = form ? form.querySelector('[name="' + k + '"]') : null;
        var w = p.get(k);
        if (el && w !== null && w !== '' && !isNaN(parseFloat(w))) { el.value = String(parseFloat(w)); }
      });
      var lieferbar = form ? form.querySelector('input[name="lieferbar"]') : null;
      if (lieferbar && p.get('lieferbar') === '1') { lieferbar.checked = true; }
      var sort = p.get('sort');
      if (sortierung && sort && alle(sortierung, 'option').some(function (o) { return o.value === sort; })) {
        sortierung.value = sort;
      }
    }

    if (form) {
      form.addEventListener('change', function () { anwenden(true); });
      form.addEventListener('input', function (e) {
        if (e.target && e.target.type === 'number') { anwenden(true); }
      });
      form.addEventListener('submit', function (e) {
        e.preventDefault();
        anwenden(true);
      });
      form.addEventListener('reset', function () {
        setTimeout(function () { anwenden(true); }, 0);
      });
    }
    if (sortierung) {
      sortierung.addEventListener('change', function () { anwenden(true); });
    }

    ausUrlLesen();
    anwenden(false);
  }

  /* ---------- Umschalter: Menü und Filter ---------- */

  function umschalter(knopf, ziel, nurWennSichtbar) {
    if (!knopf || !ziel) { return; }

    function setzen(offen) {
      knopf.setAttribute('aria-expanded', offen ? 'true' : 'false');
      ziel.classList.toggle('ist-offen', offen);
    }

    function istOffen() { return knopf.getAttribute('aria-expanded') === 'true'; }

    knopf.addEventListener('click', function (e) {
      e.preventDefault();
      setzen(!istOffen());
    });

    document.addEventListener('keydown', function (e) {
      if ((e.key !== 'Escape' && e.key !== 'Esc') || e.defaultPrevented || !istOffen()) { return; }
      if (nurWennSichtbar && knopf.offsetParent === null) { return; }
      var aktiv = document.activeElement;
      if (nurWennSichtbar && aktiv && aktiv !== knopf && !ziel.contains(aktiv)) { return; }
      setzen(false);
      fokus(knopf);
    });

    setzen(false);
  }

  /* ---------- Start ---------- */

  function start() {
    datenLaden();
    ansageAnlegen();
    sicher(einkaufenBinden);
    sicher(zaehlerSetzen);

    sicher(function () {
      alle(document, '[data-menue-umschalter]').forEach(function (knopf) {
        umschalter(knopf, document.getElementById(knopf.getAttribute('aria-controls') || 'hauptnavigation'), false);
      });
    });
    sicher(function () {
      alle(document, '[data-filter-umschalter]').forEach(function (knopf) {
        umschalter(knopf, document.getElementById(knopf.getAttribute('aria-controls') || 'filter'), true);
      });
    });

    sicher(function () { alle(document, 'form[data-suche]').forEach(combobox); });
    sicher(function () { alle(document, '[data-suchseite]').forEach(suchseite); });
    sicher(function () { alle(document, '[data-katalog]').forEach(katalog); });
    sicher(function () {
      var wk = document.querySelector('[data-warenkorb]');
      if (wk) { warenkorbAnsicht = warenkorbSeite(wk); }
    });
    sicher(function () {
      var kasse = document.querySelector('form[data-kasse]');
      if (kasse) { kasseAnsicht = kasseSeite(kasse); }
    });
    sicher(function () { alle(document, 'form[data-formular]').forEach(formular); });

    var meldungEl = document.getElementById('meldung');
    if (meldungEl) {
      meldungEl.addEventListener('focusout', function () { if (meldungEl.innerHTML) { meldungPlanen(); } });
      meldungEl.addEventListener('mouseleave', function () { if (meldungEl.innerHTML) { meldungPlanen(); } });
    }
  }

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', function () { sicher(start); });
  } else {
    sicher(start);
  }
}());
