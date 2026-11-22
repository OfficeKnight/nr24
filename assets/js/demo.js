/*
  Notebook Reparatur 24, Demo-Leiste (Paket designs).

  Diese Datei gehört nur zur Vorschau des Redesigns. Sie setzt sofort beim Laden im head die Attribute
  data-design, data-schrift und data-platzhalter am html-Element (gespeichert in localStorage unter
  "nr24-demo") und blendet oben eine Leiste mit den Schaltern für Design, Schrift und Platzhalter ein.

  So entfernen Sie die Demo-Leiste
  1. In src/vorlagen/base.html die eine Zeile
       <script src="{{ root }}assets/js/demo.js"></script>
     löschen.
  2. Die Seite aus der Repo-Wurzel neu bauen (python3 src/build.py).
  3. Optional diese Datei assets/js/demo.js löschen.
  Ohne die Leiste gelten die Vorgaben aus base.html (Design A Werkstattgrün, Schrift 1). Ein Design fest
  einstellen geht über data-design und data-schrift am html-Element in base.html.

  Die Datei hat keine Abhängigkeiten und bringt ihr eigenes CSS mit (Klassen mit Präfix demo-leiste).
*/
(function () {
  "use strict";

  var SCHLUESSEL = "nr24-demo";
  var STANDARD = { design: "a", schrift: "1", platzhalter: false };
  var DESIGNS = [
    ["a", "A", "Werkstattgrün"],
    ["b", "B", "Hell und neutral"],
    ["c", "C", "Dunkel"]
  ];
  var SCHRIFTEN = [
    ["1", "1", "Space Grotesk und Inter"],
    ["2", "2", "Inter"],
    ["3", "3", "IBM Plex Sans"]
  ];
  var html = document.documentElement;

  function bereinigen(wert) {
    var z = { design: STANDARD.design, schrift: STANDARD.schrift, platzhalter: STANDARD.platzhalter };
    if (wert && typeof wert === "object") {
      if (/^[abc]$/.test(wert.design)) { z.design = wert.design; }
      if (/^[123]$/.test(String(wert.schrift))) { z.schrift = String(wert.schrift); }
      z.platzhalter = wert.platzhalter === true;
    }
    return z;
  }

  function lesen(text) {
    try {
      if (text === undefined) { text = window.localStorage.getItem(SCHLUESSEL); }
      return bereinigen(text ? JSON.parse(text) : null);
    } catch (e) {
      return bereinigen(null);
    }
  }

  function speichern(zustand) {
    try {
      window.localStorage.setItem(SCHLUESSEL, JSON.stringify(zustand));
    } catch (e) { /* ohne Speicher gilt die Auswahl nur für diese Seite */ }
  }

  function anwenden(zustand) {
    html.setAttribute("data-design", zustand.design);
    html.setAttribute("data-schrift", zustand.schrift);
    html.setAttribute("data-platzhalter", zustand.platzhalter ? "an" : "aus");
  }

  /* Sofort und synchron im head, damit beim ersten Zeichnen schon das richtige Design gilt. */
  var aktuell = lesen();
  anwenden(aktuell);

  var CSS = [
    ".demo-leiste{--dl-grund:#17191C;--dl-text:#FFFFFF;--dl-text-2:#C5CAD1;--dl-linie:#6B737E;--dl-wahl:#FFFFFF;--dl-wahl-text:#17191C;--dl-fokus:#FFD54A;",
    "position:relative;z-index:900;margin:0;padding:0;background:var(--dl-grund);color:var(--dl-text);border-bottom:1px solid #000000;",
    "font:500 13px/1.35 system-ui,-apple-system,\"Segoe UI\",Roboto,Arial,sans-serif;letter-spacing:0;text-align:left;color-scheme:dark}",
    ".demo-leiste *,.demo-leiste *::before,.demo-leiste *::after{box-sizing:border-box;-webkit-tap-highlight-color:transparent}",
    ".demo-leiste__innen{display:flex;flex-wrap:wrap;align-items:center;gap:4px 16px;max-width:1440px;margin:0 auto;padding:4px 16px}",
    ".demo-leiste__kennung{flex:1 1 0;min-width:0;margin:0;padding:6px 0;color:var(--dl-text);font-weight:600}",
    ".demo-leiste__umschalter{display:inline-flex;align-items:center;gap:6px;flex:none;min-height:44px;margin:0;padding:0 12px;border:1px solid var(--dl-linie);border-radius:6px;background:transparent;color:var(--dl-text);font:inherit;font-weight:600;cursor:pointer}",
    ".demo-leiste__umschalter:hover{border-color:var(--dl-text-2);background:#2A2E33}",
    ".demo-leiste__pfeil{width:10px;height:10px;flex:none}",
    ".demo-leiste__umschalter[aria-expanded=\"true\"] .demo-leiste__pfeil{transform:rotate(180deg)}",
    ".demo-leiste__schalter{display:none;flex:1 1 100%;flex-direction:column;align-items:stretch;gap:10px;padding:4px 0 12px}",
    ".demo-leiste--offen .demo-leiste__schalter{display:flex}",
    ".demo-leiste__gruppe{display:flex;flex-wrap:wrap;align-items:center;gap:6px;min-width:0;margin:0;padding:0;border:0}",
    ".demo-leiste__gruppe legend{float:left;margin:0 4px 0 0;padding:0;color:var(--dl-text-2);font-weight:600}",
    ".demo-leiste__gruppe legend+*{clear:none}",
    ".demo-leiste__optionen{display:flex;flex-wrap:wrap;gap:6px;width:100%}",
    ".demo-leiste__opt{position:relative;display:inline-flex;margin:0;cursor:pointer}",
    ".demo-leiste__opt input{position:absolute;inset:0;width:100%;height:100%;margin:0;opacity:0;cursor:pointer}",
    ".demo-leiste__opt span{display:inline-flex;align-items:center;min-height:44px;padding:0 12px;border:1px solid var(--dl-linie);border-radius:6px;color:var(--dl-text);white-space:nowrap}",
    ".demo-leiste__opt b{margin-right:6px;font-weight:700}",
    ".demo-leiste__opt:hover span{border-color:var(--dl-text-2);background:#2A2E33}",
    ".demo-leiste__opt input:checked+span{border-color:var(--dl-wahl);background:var(--dl-wahl);color:var(--dl-wahl-text)}",
    ".demo-leiste__opt input:focus-visible+span,.demo-leiste__umschalter:focus-visible,.demo-leiste__pruef input:focus-visible+span{outline:3px solid var(--dl-fokus);outline-offset:2px}",
    ".demo-leiste__pruef{position:relative;display:inline-flex;align-items:center;margin:0;cursor:pointer}",
    ".demo-leiste__pruef input{position:absolute;inset:0;width:100%;height:100%;margin:0;opacity:0;cursor:pointer}",
    ".demo-leiste__pruef span{display:inline-flex;align-items:center;gap:8px;min-height:44px;padding:0 12px 0 8px;border:1px solid var(--dl-linie);border-radius:6px;white-space:nowrap}",
    ".demo-leiste__pruef span::before{content:\"\";flex:none;width:16px;height:16px;border:2px solid var(--dl-text-2);border-radius:3px;background:transparent}",
    ".demo-leiste__pruef input:checked+span::before{border-color:var(--dl-wahl);background:var(--dl-wahl);box-shadow:inset 0 0 0 2px var(--dl-grund)}",
    ".demo-leiste__pruef:hover span{border-color:var(--dl-text-2);background:#2A2E33}",
    "@media (min-width:720px){",
    ".demo-leiste__schalter{flex-direction:row;flex-wrap:wrap;align-items:center;gap:10px 24px}",
    ".demo-leiste__optionen{width:auto}",
    "}",
    "@media (min-width:1280px){",
    ".demo-leiste{font-size:12px}",
    ".demo-leiste__innen{flex-wrap:nowrap;gap:8px 18px;padding:3px 20px}",
    ".demo-leiste__kennung{flex:0 1 auto;min-width:150px;max-width:230px;padding:2px 0;line-height:1.25}",
    ".demo-leiste__umschalter{display:none}",
    ".demo-leiste__schalter{display:flex;flex:0 1 auto;flex-wrap:wrap;justify-content:flex-end;gap:4px 18px;margin-left:auto;padding:0}",
    ".demo-leiste__gruppe{flex-wrap:nowrap}",
    ".demo-leiste__gruppe legend{margin-right:6px}",
    ".demo-leiste__optionen{flex-wrap:nowrap;gap:4px}",
    ".demo-leiste__opt span,.demo-leiste__pruef span{min-height:28px;padding:0 8px;border-radius:5px}",
    ".demo-leiste__opt b{margin-right:5px}",
    ".demo-leiste__pruef span{gap:7px;padding-left:7px}",
    ".demo-leiste__pruef span::before{width:14px;height:14px}",
    "}",
    "@media (min-width:1440px){.demo-leiste__kennung{max-width:none}}",
    "@media (forced-colors:active){.demo-leiste__opt input:checked+span{outline:2px solid Highlight;forced-color-adjust:none;background:Highlight;color:HighlightText}.demo-leiste__pruef input:checked+span::before{background:Highlight}}",
    "@media print{.demo-leiste{display:none!important}}"
  ].join("\n");

  function stilEinfuegen() {
    if (document.getElementById("demo-leiste-stil")) { return; }
    var s = document.createElement("style");
    s.id = "demo-leiste-stil";
    s.textContent = CSS;
    (document.head || html).appendChild(s);
  }
  stilEinfuegen();

  function el(tag, klasse, text) {
    var e = document.createElement(tag);
    if (klasse) { e.className = klasse; }
    if (text) { e.textContent = text; }
    return e;
  }

  function gruppe(titel, name, optionen, gewaehlt) {
    var fs = el("fieldset", "demo-leiste__gruppe");
    fs.appendChild(el("legend", "", titel));
    var box = el("div", "demo-leiste__optionen");
    optionen.forEach(function (o) {
      var label = el("label", "demo-leiste__opt");
      var input = document.createElement("input");
      input.type = "radio";
      input.name = name;
      input.value = o[0];
      input.checked = o[0] === gewaehlt;
      var span = el("span");
      span.appendChild(el("b", "", o[1]));
      span.appendChild(document.createTextNode(o[2]));
      label.appendChild(input);
      label.appendChild(span);
      box.appendChild(label);
    });
    fs.appendChild(box);
    return fs;
  }

  var leiste = null;

  function eingabenAbgleichen(zustand) {
    if (!leiste) { return; }
    var inputs = leiste.querySelectorAll("input");
    for (var i = 0; i < inputs.length; i++) {
      var inp = inputs[i];
      if (inp.name === "demo-leiste-design") { inp.checked = inp.value === zustand.design; }
      else if (inp.name === "demo-leiste-schrift") { inp.checked = inp.value === zustand.schrift; }
      else if (inp.name === "demo-leiste-platzhalter") { inp.checked = zustand.platzhalter; }
    }
  }

  function leisteBauen() {
    if (leiste || !document.body || document.querySelector(".demo-leiste")) { return; }
    stilEinfuegen();

    leiste = el("section", "demo-leiste");
    leiste.setAttribute("aria-label", "Demo-Einstellungen");
    var innen = el("div", "demo-leiste__innen");

    var kennung = el("p", "demo-leiste__kennung");
    kennung.textContent = "Demo für ein Redesign, keine Bestellung möglich";
    innen.appendChild(kennung);

    var knopf = el("button", "demo-leiste__umschalter");
    knopf.type = "button";
    knopf.setAttribute("aria-expanded", "false");
    knopf.setAttribute("aria-controls", "demo-leiste-schalter");
    knopf.appendChild(el("span", "", "Demo-Einstellungen"));
    knopf.insertAdjacentHTML("beforeend",
      '<svg class="demo-leiste__pfeil" viewBox="0 0 10 10" aria-hidden="true" focusable="false">' +
      '<path d="M1 3.5 5 7.5 9 3.5" fill="none" stroke="currentColor" stroke-width="1.6"/></svg>');
    innen.appendChild(knopf);

    var schalter = el("div", "demo-leiste__schalter");
    schalter.id = "demo-leiste-schalter";
    schalter.appendChild(gruppe("Design", "demo-leiste-design", DESIGNS, aktuell.design));
    schalter.appendChild(gruppe("Schrift", "demo-leiste-schrift", SCHRIFTEN, aktuell.schrift));

    var pruef = el("label", "demo-leiste__pruef");
    var cb = document.createElement("input");
    cb.type = "checkbox";
    cb.name = "demo-leiste-platzhalter";
    cb.checked = aktuell.platzhalter;
    pruef.appendChild(cb);
    pruef.appendChild(el("span", "", "Platzhalter markieren"));
    schalter.appendChild(pruef);
    innen.appendChild(schalter);
    leiste.appendChild(innen);

    knopf.addEventListener("click", function () {
      var offen = knopf.getAttribute("aria-expanded") !== "true";
      knopf.setAttribute("aria-expanded", offen ? "true" : "false");
      leiste.classList.toggle("demo-leiste--offen", offen);
    });

    schalter.addEventListener("change", function (ev) {
      var t = ev.target;
      if (!t || !t.name) { return; }
      var neu = { design: aktuell.design, schrift: aktuell.schrift, platzhalter: aktuell.platzhalter };
      if (t.name === "demo-leiste-design" && t.checked) { neu.design = t.value; }
      else if (t.name === "demo-leiste-schrift" && t.checked) { neu.schrift = t.value; }
      else if (t.name === "demo-leiste-platzhalter") { neu.platzhalter = t.checked; }
      aktuell = bereinigen(neu);
      anwenden(aktuell);
      speichern(aktuell);
    });

    leiste.addEventListener("keydown", function (ev) {
      if (ev.key === "Escape" && knopf.getAttribute("aria-expanded") === "true" &&
          window.getComputedStyle(knopf).display !== "none") {
        knopf.setAttribute("aria-expanded", "false");
        leiste.classList.remove("demo-leiste--offen");
        knopf.focus();
      }
    });

    var skip = document.querySelector(".skiplink");
    if (skip && skip.parentNode) {
      skip.parentNode.insertBefore(leiste, skip.nextSibling);
    } else {
      document.body.insertBefore(leiste, document.body.firstChild);
    }
  }

  /* Abgleich zwischen Tabs und beim Zurückblättern aus dem Verlauf. */
  window.addEventListener("storage", function (ev) {
    if (ev.key !== SCHLUESSEL && ev.key !== null) { return; }
    aktuell = lesen(ev.key === null ? undefined : ev.newValue);
    anwenden(aktuell);
    eingabenAbgleichen(aktuell);
  });
  window.addEventListener("pageshow", function (ev) {
    if (!ev.persisted) { return; }
    aktuell = lesen();
    anwenden(aktuell);
    eingabenAbgleichen(aktuell);
  });

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", leisteBauen);
  } else {
    leisteBauen();
  }
})();
