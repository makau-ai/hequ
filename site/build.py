"""Static site builder for hequ.ai/discovery — cinematic rewrite.

v2 of the builder. The first pass was functional-but-text-heavy;
this pass makes the sub-pages feel like the same visual world as
the hero landing page: layered dark background with a subtle
constellation canvas, oversized serif display headers, card-
based content (not HTML tables), generous negative space, gold-
on-void palette, motion on load, and a coupling-detail layout
that presents A↔B as a cinematic pairing with a glowing connector.

The builder still reads the live framework outputs:

    labs_v2/equations/**/equation.yaml
    labs_v2/cross_analysis/discovery_ledger.jsonl
    labs_v2/cross_analysis/AI_REVIEW_SUMMARY.md

and emits to `landing/public/discovery/`. Re-running the build
with the same inputs produces byte-identical output.

No JS framework. One small background canvas script is shared
across pages via `_assets/starfield.js`; everything else is
static HTML + CSS.
"""

from __future__ import annotations

import html
import json
import sys
from dataclasses import asdict
from pathlib import Path
from typing import Any, Dict, List, Mapping, Optional

_REPO_ROOT = Path(__file__).resolve().parent.parent
_LABS_V2 = _REPO_ROOT / "labs_v2"
_LANDING_PUBLIC = _REPO_ROOT / "landing" / "public"
_OUT_DIR = _LANDING_PUBLIC / "discovery"
_LEDGER_PATH = _LABS_V2 / "cross_analysis" / "discovery_ledger.jsonl"

if str(_LABS_V2) not in sys.path:
    sys.path.insert(0, str(_LABS_V2))

from framework.couplings import CouplingTier
from framework.discovery_ledger import DiscoveryLedger
from framework.layer5_coupling_sieve import run_coupling_sieve
from framework.physical_constraints import evaluate as evaluate_physical
from framework.emergent_analysis import analyse as analyse_emergent
from framework.typed_expression import TypedExpression, load_all_equations


# ---------------------------------------------------------------------------
# Shared assets: CSS + background canvas script
# ---------------------------------------------------------------------------

_CSS = """\
@import url('https://fonts.googleapis.com/css2?family=Cormorant+Garamond:ital,wght@0,300;0,400;0,500;0,600;1,300;1,400&family=Rajdhani:wght@300;400;500;600;700&family=JetBrains+Mono:wght@400;500&display=swap');

:root {
  --bg: #06050e;
  --bg-deep: #040310;
  --bg-panel: rgba(20, 16, 42, 0.55);
  --bg-panel-solid: #120f26;
  --bg-glow: rgba(212, 168, 83, 0.06);
  --fg: #f1ede0;
  --fg-mid: #bcb6a4;
  --fg-dim: #827a67;
  --accent: #d4a853;
  --accent-bright: #f0e0b8;
  --accent-deep: #7a5e2a;
  --accent-glow: rgba(212, 168, 83, 0.35);
  --proved: #8dffb8;
  --empirical: #a8c6ff;
  --conjectural: #f5d26b;
  --rejected: #ff8a68;
  --divider: rgba(212, 168, 83, 0.18);
  --divider-soft: rgba(212, 168, 83, 0.08);
  --serif: 'Cormorant Garamond', Georgia, serif;
  --sans: 'Rajdhani', -apple-system, BlinkMacSystemFont, sans-serif;
  --mono: 'JetBrains Mono', SFMono-Regular, Menlo, monospace;
  --ease: cubic-bezier(0.22, 1, 0.36, 1);
}

* { box-sizing: border-box; margin: 0; padding: 0; }
html, body { min-height: 100vh; background: var(--bg-deep); }
body {
  font-family: var(--sans);
  font-weight: 300;
  color: var(--fg);
  line-height: 1.6;
  letter-spacing: 0.01em;
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
  position: relative;
  overflow-x: hidden;
}

/* ---- Background layers ---- */
body::before {
  content: "";
  position: fixed;
  inset: 0;
  z-index: -3;
  background:
    radial-gradient(ellipse 80% 60% at 50% 0%, rgba(120, 80, 180, 0.18) 0%, transparent 60%),
    radial-gradient(ellipse 60% 40% at 20% 100%, rgba(30, 180, 160, 0.10) 0%, transparent 70%),
    radial-gradient(ellipse 70% 50% at 80% 80%, rgba(212, 168, 83, 0.08) 0%, transparent 60%),
    linear-gradient(180deg, var(--bg-deep) 0%, #0a0718 50%, var(--bg-deep) 100%);
}
body::after {
  content: "";
  position: fixed;
  inset: 0;
  z-index: -1;
  background: radial-gradient(ellipse 60% 40% at 50% 30%, var(--bg-glow) 0%, transparent 70%);
  pointer-events: none;
}
#starfield {
  position: fixed;
  inset: 0;
  z-index: -2;
  pointer-events: none;
}

/* ---- Site header ---- */
header.site {
  position: sticky;
  top: 0;
  z-index: 100;
  backdrop-filter: blur(12px) saturate(140%);
  -webkit-backdrop-filter: blur(12px) saturate(140%);
  background: rgba(6, 5, 14, 0.55);
  border-bottom: 1px solid var(--divider);
}
header.site .inner {
  max-width: 1180px;
  margin: 0 auto;
  padding: 1.2rem 2rem;
  display: flex;
  align-items: baseline;
  justify-content: space-between;
  gap: 2rem;
}
header.site .brand {
  font-family: var(--sans);
  font-weight: 600;
  font-size: 1.35rem;
  letter-spacing: 0.12em;
  text-transform: uppercase;
  color: var(--accent);
  text-decoration: none;
}
header.site .brand .dot { color: var(--accent-bright); }
header.site .brand .path {
  font-family: var(--serif);
  font-size: 1.1rem;
  font-style: italic;
  font-weight: 300;
  color: var(--fg-dim);
  text-transform: none;
  letter-spacing: 0.02em;
  margin-left: 0.45rem;
}
header.site nav { display: flex; gap: 2.1rem; }
header.site nav a {
  color: var(--fg-mid);
  text-decoration: none;
  font-size: 0.78rem;
  font-weight: 400;
  letter-spacing: 0.22em;
  text-transform: uppercase;
  padding: 0.3rem 0;
  position: relative;
  transition: color 0.3s var(--ease);
}
header.site nav a::after {
  content: "";
  position: absolute;
  left: 0; right: 0; bottom: -0.45rem;
  height: 1px;
  background: var(--accent);
  transform: scaleX(0);
  transform-origin: center;
  transition: transform 0.35s var(--ease);
}
header.site nav a:hover { color: var(--accent-bright); }
header.site nav a:hover::after { transform: scaleX(1); }
header.site nav a.current { color: var(--accent); }
header.site nav a.current::after { transform: scaleX(1); }

/* ---- Main container + page intro ---- */
main.container {
  max-width: 1180px;
  margin: 0 auto;
  padding: 5rem 2rem 8rem;
  position: relative;
}
main.narrow {
  max-width: 880px;
}

.page-intro {
  margin-bottom: 4rem;
  animation: intro 1.2s var(--ease) both;
}
@keyframes intro {
  from { opacity: 0; transform: translateY(24px); }
  to { opacity: 1; transform: translateY(0); }
}
.overline {
  display: inline-block;
  font-family: var(--sans);
  font-weight: 500;
  font-size: 0.72rem;
  letter-spacing: 0.35em;
  text-transform: uppercase;
  color: var(--accent);
  padding: 0.25rem 0 0.6rem;
  border-bottom: 1px solid var(--divider);
  margin-bottom: 1.6rem;
}
h1 {
  font-family: var(--serif);
  font-weight: 400;
  font-size: clamp(3rem, 6vw, 5rem);
  line-height: 1.02;
  letter-spacing: -0.01em;
  color: var(--fg);
  margin-bottom: 0.6rem;
}
h1 em { font-style: italic; color: var(--accent-bright); font-weight: 300; }
.lead {
  font-family: var(--serif);
  font-style: italic;
  font-weight: 300;
  font-size: clamp(1.15rem, 1.8vw, 1.5rem);
  color: var(--fg-mid);
  max-width: 58ch;
  line-height: 1.5;
}

h2 {
  font-family: var(--serif);
  font-weight: 400;
  font-size: clamp(2rem, 3.2vw, 2.6rem);
  color: var(--fg);
  margin-top: 4.5rem;
  margin-bottom: 1.4rem;
  letter-spacing: -0.005em;
}
h2::before {
  content: "";
  display: block;
  width: 2.4rem;
  height: 1px;
  background: var(--accent);
  margin-bottom: 1.2rem;
}
h3 {
  font-family: var(--sans);
  font-weight: 500;
  font-size: 0.82rem;
  text-transform: uppercase;
  letter-spacing: 0.22em;
  color: var(--accent);
  margin-top: 1.4rem;
  margin-bottom: 0.7rem;
}
h4 {
  font-family: var(--sans);
  font-weight: 500;
  font-size: 0.9rem;
  text-transform: uppercase;
  letter-spacing: 0.12em;
  color: var(--fg);
}

p { margin-bottom: 1.1rem; color: var(--fg-mid); max-width: 66ch; font-size: 1.02rem; }
p.prose { font-family: var(--serif); font-size: 1.2rem; font-weight: 300; line-height: 1.65; color: var(--fg); max-width: 64ch; }
ul, ol { margin-bottom: 1.2rem; color: var(--fg-mid); }
ul { list-style: none; padding-left: 0; }
ul li {
  position: relative;
  padding-left: 1.4rem;
  margin-bottom: 0.55rem;
  max-width: 66ch;
}
ul li::before {
  content: "◆";
  position: absolute;
  left: 0;
  top: 0.1em;
  color: var(--accent);
  font-size: 0.65rem;
}

a { color: var(--accent); text-decoration: none; border-bottom: 1px solid transparent; transition: border-color 0.25s var(--ease), color 0.25s var(--ease); }
a:hover { color: var(--accent-bright); border-bottom-color: var(--accent); }

/* ---- Code + math display ---- */
code, pre, .mono { font-family: var(--mono); font-feature-settings: "liga" 0; }
code {
  color: var(--accent-bright);
  background: rgba(212, 168, 83, 0.08);
  padding: 0.1em 0.45em;
  border-radius: 3px;
  font-size: 0.85em;
  border: 1px solid rgba(212, 168, 83, 0.12);
}
pre {
  background: rgba(10, 7, 20, 0.6);
  border: 1px solid var(--divider-soft);
  border-left: 2px solid var(--accent);
  padding: 1rem 1.3rem;
  overflow-x: auto;
  margin: 1rem 0 1.4rem;
  font-size: 0.86rem;
  border-radius: 4px;
}
.math-display {
  font-family: var(--mono);
  font-weight: 500;
  font-size: 1.25rem;
  color: var(--accent-bright);
  background: linear-gradient(180deg, rgba(20, 16, 42, 0.4) 0%, rgba(20, 16, 42, 0.15) 100%);
  border: 1px solid var(--divider);
  border-left: 3px solid var(--accent);
  padding: 1.4rem 1.8rem;
  border-radius: 5px;
  display: inline-block;
  min-width: 40%;
  margin: 0.6rem 0 2rem;
  position: relative;
  overflow: hidden;
}
.math-display::before {
  content: "";
  position: absolute;
  inset: 0;
  background: radial-gradient(ellipse 80% 120% at 30% 0%, rgba(212, 168, 83, 0.10), transparent 60%);
  pointer-events: none;
}

/* ---- Panels / cards ---- */
.panel {
  background: var(--bg-panel);
  border: 1px solid var(--divider);
  border-radius: 6px;
  padding: 1.6rem 1.9rem;
  margin-bottom: 1.2rem;
  backdrop-filter: blur(8px);
  -webkit-backdrop-filter: blur(8px);
  transition: border-color 0.3s var(--ease), transform 0.3s var(--ease);
}
.panel.tight { padding: 1rem 1.3rem; }
.panel:hover { border-color: var(--accent-deep); }
a.panel { display: block; color: var(--fg); text-decoration: none; border-bottom: none; }
a.panel:hover { transform: translateY(-2px); }

/* ---- Stat grid (home) ---- */
.stat-grid {
  display: grid;
  gap: 1rem;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  margin: 1rem 0 2.5rem;
}
.stat {
  background: var(--bg-panel);
  border: 1px solid var(--divider);
  border-radius: 6px;
  padding: 1.8rem 1.7rem 1.5rem;
  backdrop-filter: blur(8px);
  -webkit-backdrop-filter: blur(8px);
  position: relative;
  overflow: hidden;
}
.stat::before {
  content: "";
  position: absolute;
  inset: auto 0 0 0;
  height: 2px;
  background: linear-gradient(90deg, transparent, var(--accent), transparent);
  opacity: 0.6;
}
.stat .value {
  font-family: var(--serif);
  font-weight: 400;
  font-size: 3.4rem;
  line-height: 0.95;
  color: var(--accent);
  letter-spacing: -0.02em;
}
.stat .label {
  font-family: var(--sans);
  font-size: 0.7rem;
  text-transform: uppercase;
  letter-spacing: 0.22em;
  color: var(--fg-dim);
  margin-top: 0.5rem;
}

/* ---- Card grids for indexes ---- */
.card-grid {
  display: grid;
  gap: 1rem;
  grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
  margin: 1.5rem 0 3rem;
}
.card {
  background: var(--bg-panel);
  border: 1px solid var(--divider);
  border-radius: 6px;
  padding: 1.5rem 1.6rem;
  backdrop-filter: blur(8px);
  -webkit-backdrop-filter: blur(8px);
  transition: border-color 0.35s var(--ease), transform 0.35s var(--ease), box-shadow 0.35s var(--ease);
  position: relative;
  overflow: hidden;
  display: block;
  color: var(--fg);
  text-decoration: none;
  border-bottom: none;
}
.card:hover {
  transform: translateY(-3px);
  border-color: var(--accent);
  box-shadow: 0 12px 40px -12px rgba(212, 168, 83, 0.25);
}
.card .card-id {
  font-family: var(--mono);
  font-size: 0.72rem;
  letter-spacing: 0.05em;
  color: var(--accent);
  margin-bottom: 0.35rem;
}
.card .card-name {
  font-family: var(--serif);
  font-size: 1.55rem;
  color: var(--fg);
  line-height: 1.15;
  margin-bottom: 0.7rem;
  font-weight: 400;
}
.card .card-math {
  font-family: var(--mono);
  font-size: 0.88rem;
  color: var(--accent-bright);
  background: rgba(212, 168, 83, 0.06);
  padding: 0.55rem 0.8rem;
  border-radius: 3px;
  border: 1px solid rgba(212, 168, 83, 0.12);
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
  display: block;
}
.card .card-meta {
  font-size: 0.74rem;
  color: var(--fg-dim);
  text-transform: uppercase;
  letter-spacing: 0.1em;
  margin-top: 0.9rem;
  display: flex;
  gap: 0.75rem;
  flex-wrap: wrap;
}

/* ---- Domain section headers ---- */
.domain-section { margin-bottom: 3rem; }
.domain-section .domain-label {
  font-family: var(--serif);
  font-style: italic;
  font-weight: 300;
  font-size: 1.4rem;
  color: var(--fg-dim);
  letter-spacing: 0.05em;
  margin-bottom: 1.2rem;
  padding-bottom: 0.8rem;
  border-bottom: 1px solid var(--divider-soft);
}

/* ---- Coupling detail: A↔B pairing layout ---- */
.pairing {
  display: grid;
  grid-template-columns: 1fr 80px 1fr;
  gap: 0;
  align-items: stretch;
  margin: 2rem 0 3rem;
}
.pairing .side {
  background: var(--bg-panel);
  border: 1px solid var(--divider);
  border-radius: 6px;
  padding: 2rem 2rem 1.7rem;
  backdrop-filter: blur(8px);
  -webkit-backdrop-filter: blur(8px);
}
.pairing .side.left { border-right: none; border-top-right-radius: 0; border-bottom-right-radius: 0; }
.pairing .side.right { border-left: none; border-top-left-radius: 0; border-bottom-left-radius: 0; }
.pairing .side .side-label {
  font-size: 0.66rem;
  letter-spacing: 0.25em;
  text-transform: uppercase;
  color: var(--fg-dim);
  margin-bottom: 0.7rem;
}
.pairing .side .side-eq-id {
  font-family: var(--mono);
  font-size: 0.85rem;
  color: var(--accent);
  margin-bottom: 0.4rem;
}
.pairing .side .side-var {
  font-family: var(--serif);
  font-size: 3rem;
  line-height: 1;
  color: var(--accent-bright);
  font-weight: 400;
  letter-spacing: -0.02em;
  margin-bottom: 0.9rem;
}
.pairing .connector {
  display: flex;
  align-items: center;
  justify-content: center;
  position: relative;
  background: radial-gradient(ellipse 100% 60% at 50% 50%, rgba(212, 168, 83, 0.25), transparent 70%);
}
.pairing .connector .arrow {
  font-family: var(--serif);
  font-weight: 300;
  font-size: 3rem;
  color: var(--accent);
  animation: pulse 3.5s ease-in-out infinite;
}
@keyframes pulse {
  0%, 100% { opacity: 0.55; transform: scale(1); }
  50% { opacity: 1; transform: scale(1.08); }
}
@media (max-width: 720px) {
  .pairing { grid-template-columns: 1fr; }
  .pairing .side.left { border-right: 1px solid var(--divider); border-bottom: none; border-radius: 6px 6px 0 0; }
  .pairing .side.right { border-left: 1px solid var(--divider); border-radius: 0 0 6px 6px; }
  .pairing .connector { padding: 1rem 0; }
}

/* ---- Key/value descriptor blocks ---- */
dl.kv {
  display: grid;
  grid-template-columns: max-content 1fr;
  gap: 0.5rem 1.2rem;
  margin: 0.6rem 0;
}
dl.kv dt {
  font-family: var(--sans);
  font-size: 0.7rem;
  letter-spacing: 0.18em;
  text-transform: uppercase;
  color: var(--fg-dim);
  padding-top: 0.15rem;
}
dl.kv dd {
  font-family: var(--mono);
  font-size: 0.86rem;
  color: var(--fg);
}

/* ---- Badges ---- */
.badge {
  display: inline-block;
  padding: 0.22em 0.7em;
  border-radius: 2px;
  font-family: var(--sans);
  font-weight: 500;
  font-size: 0.68rem;
  letter-spacing: 0.15em;
  text-transform: uppercase;
}
.badge.proved      { color: var(--proved); border: 1px solid rgba(141, 255, 184, 0.4); background: rgba(141, 255, 184, 0.06); }
.badge.empirical   { color: var(--empirical); border: 1px solid rgba(168, 198, 255, 0.38); background: rgba(168, 198, 255, 0.06); }
.badge.conjectural { color: var(--conjectural); border: 1px solid rgba(245, 210, 107, 0.36); background: rgba(245, 210, 107, 0.06); }
.badge.rejected    { color: var(--rejected); border: 1px solid rgba(255, 138, 104, 0.38); background: rgba(255, 138, 104, 0.06); }
.badge.tier1 { color: var(--accent-bright); border: 1px solid var(--accent); background: rgba(212, 168, 83, 0.12); }
.badge.tier2 { color: var(--accent); border: 1px solid var(--accent-deep); background: rgba(212, 168, 83, 0.06); }
.badge.tier3 { color: var(--fg-dim); border: 1px solid var(--fg-dim); }
.badge.neutral { color: var(--fg-dim); border: 1px solid var(--divider); }

/* ---- Constraint / review cards ---- */
.check-card {
  background: var(--bg-panel);
  border: 1px solid var(--divider);
  border-left: 3px solid var(--divider);
  border-radius: 4px;
  padding: 1.1rem 1.4rem;
  margin-bottom: 0.8rem;
  backdrop-filter: blur(8px);
  -webkit-backdrop-filter: blur(8px);
}
.check-card.passed { border-left-color: var(--proved); }
.check-card.failed { border-left-color: var(--rejected); }
.check-card.not_applicable { border-left-color: var(--fg-dim); opacity: 0.72; }
.check-card .check-head {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 1rem;
  margin-bottom: 0.5rem;
}
.check-card .check-name {
  font-family: var(--sans);
  font-weight: 500;
  font-size: 0.85rem;
  text-transform: uppercase;
  letter-spacing: 0.15em;
  color: var(--fg);
}
.check-card .reasoning {
  font-family: var(--serif);
  font-size: 1.02rem;
  line-height: 1.55;
  color: var(--fg-mid);
  font-style: italic;
}

.reviewer-card {
  background: var(--bg-panel);
  border: 1px solid var(--divider);
  border-radius: 6px;
  padding: 1.5rem 1.8rem;
  margin-bottom: 1rem;
  backdrop-filter: blur(8px);
  -webkit-backdrop-filter: blur(8px);
  position: relative;
}
.reviewer-card .reviewer-head {
  display: flex;
  align-items: baseline;
  gap: 1rem;
  margin-bottom: 0.9rem;
  padding-bottom: 0.7rem;
  border-bottom: 1px solid var(--divider-soft);
}
.reviewer-card .reviewer-name {
  font-family: var(--sans);
  font-weight: 600;
  font-size: 0.78rem;
  text-transform: uppercase;
  letter-spacing: 0.2em;
  color: var(--accent);
}
.reviewer-card .reasoning {
  font-family: var(--serif);
  font-size: 1.05rem;
  line-height: 1.6;
  color: var(--fg);
}

/* ---- Ledger / logbook table ---- */
.logbook {
  background: rgba(10, 7, 20, 0.55);
  border: 1px solid var(--divider-soft);
  border-radius: 5px;
  overflow: hidden;
  backdrop-filter: blur(8px);
  -webkit-backdrop-filter: blur(8px);
  margin: 1.5rem 0 3rem;
}
.logbook-row {
  display: grid;
  grid-template-columns: 3.5rem 1fr 1fr 1.2fr 8rem 3rem;
  gap: 0.8rem;
  padding: 0.65rem 1.3rem;
  border-bottom: 1px solid var(--divider-soft);
  font-family: var(--mono);
  font-size: 0.78rem;
  align-items: center;
  transition: background 0.25s var(--ease);
}
.logbook-row:last-child { border-bottom: none; }
.logbook-row:hover { background: rgba(212, 168, 83, 0.04); }
.logbook-row.head {
  color: var(--fg-dim);
  font-family: var(--sans);
  text-transform: uppercase;
  letter-spacing: 0.15em;
  font-size: 0.68rem;
  padding-top: 0.95rem;
  padding-bottom: 0.95rem;
  background: rgba(212, 168, 83, 0.04);
  border-bottom: 1px solid var(--divider);
}
.logbook-row .idx { color: var(--fg-dim); }
.logbook-row .eq { color: var(--accent); font-size: 0.76rem; }
.logbook-row .kind { color: var(--fg-mid); font-size: 0.73rem; }
@media (max-width: 780px) {
  .logbook-row { grid-template-columns: 2.5rem 1fr 5rem; }
  .logbook-row .kind, .logbook-row .review, .logbook-row .eq-b { display: none; }
}

/* ---- Phase cards (home "how it works") ---- */
.phases {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(260px, 1fr));
  gap: 1rem;
  margin: 1.5rem 0 3rem;
}
.phase {
  background: var(--bg-panel);
  border: 1px solid var(--divider);
  border-radius: 6px;
  padding: 1.9rem 1.8rem 1.7rem;
  backdrop-filter: blur(8px);
  -webkit-backdrop-filter: blur(8px);
  transition: border-color 0.3s var(--ease);
}
.phase:hover { border-color: var(--accent-deep); }
.phase .roman {
  font-family: var(--serif);
  font-style: italic;
  font-size: 2.4rem;
  color: var(--accent);
  line-height: 1;
  margin-bottom: 0.9rem;
  display: block;
}
.phase h3 { margin: 0 0 0.6rem; color: var(--fg); font-family: var(--serif); font-weight: 400; font-size: 1.35rem; text-transform: none; letter-spacing: 0; }
.phase p { font-size: 0.94rem; color: var(--fg-mid); font-family: var(--sans); }

/* ---- Footer ---- */
footer.site {
  margin-top: 5rem;
  padding: 2.5rem 0 1rem;
  border-top: 1px solid var(--divider-soft);
  color: var(--fg-dim);
  font-size: 0.8rem;
  text-align: center;
  letter-spacing: 0.06em;
}
footer.site p { color: var(--fg-dim); max-width: none; margin: 0 auto 0.4rem; }

/* ---- Back link ---- */
.back-link {
  display: inline-block;
  margin-top: 3rem;
  font-family: var(--sans);
  font-size: 0.78rem;
  letter-spacing: 0.18em;
  text-transform: uppercase;
  color: var(--fg-dim);
  border-bottom: 1px solid transparent;
}
.back-link:hover { color: var(--accent); border-bottom-color: var(--accent); }

/* ---- Filter bar (future hook) ---- */
.filter-bar {
  display: flex;
  gap: 0.8rem;
  flex-wrap: wrap;
  margin: 1.2rem 0 2rem;
}
"""

_STARFIELD_JS = """\
// Shared background starfield for hequ.ai/discovery sub-pages.
// Sparse, slow, no distraction. Installs a fixed canvas behind
// all content and paints twinkling stars plus two distant slow-
// drifting constellations.
(function () {
  const canvas = document.getElementById('starfield');
  if (!canvas) return;
  const ctx = canvas.getContext('2d');
  let W, H, DPR;
  let stars = [];
  let rings = [];
  let t = 0;

  function resize() {
    DPR = Math.min(window.devicePixelRatio || 1, 2);
    W = window.innerWidth;
    H = window.innerHeight;
    canvas.width = W * DPR;
    canvas.height = H * DPR;
    canvas.style.width = W + 'px';
    canvas.style.height = H + 'px';
    ctx.setTransform(DPR, 0, 0, DPR, 0, 0);
    // Rebuild stars relative to new viewport.
    stars = Array.from({length: 220}, () => ({
      x: Math.random() * W,
      y: Math.random() * H,
      r: Math.random() * 1.1 + 0.2,
      base: Math.random() * 0.5 + 0.2,
      tw: Math.random() * Math.PI * 2,
      sp: 0.0004 + Math.random() * 0.0012,
      hue: Math.random() < 0.15 ? 'gold' : 'cool'
    }));
    rings = [
      { cx: W * 0.82, cy: H * 0.18, r: Math.min(W, H) * 0.22, a: 0.05 },
      { cx: W * 0.14, cy: H * 0.74, r: Math.min(W, H) * 0.28, a: 0.04 }
    ];
  }

  function frame(now) {
    t = now * 0.001;
    ctx.clearRect(0, 0, W, H);

    // Faint distant orbits
    ctx.strokeStyle = 'rgba(212, 168, 83, 0.08)';
    ctx.lineWidth = 1;
    for (const r of rings) {
      ctx.beginPath();
      ctx.arc(r.cx, r.cy, r.r, 0, Math.PI * 2);
      ctx.stroke();
      ctx.beginPath();
      ctx.arc(r.cx, r.cy, r.r * 0.62, 0, Math.PI * 2);
      ctx.stroke();
    }

    // Stars
    for (const s of stars) {
      s.tw += s.sp;
      const alpha = s.base + Math.sin(s.tw) * 0.28;
      const color = s.hue === 'gold'
        ? `rgba(240, 224, 184, ${Math.max(0, alpha)})`
        : `rgba(200, 210, 240, ${Math.max(0, alpha * 0.82)})`;
      ctx.fillStyle = color;
      ctx.beginPath();
      ctx.arc(s.x, s.y, s.r, 0, Math.PI * 2);
      ctx.fill();
    }

    requestAnimationFrame(frame);
  }

  window.addEventListener('resize', resize);
  resize();
  requestAnimationFrame(frame);
})();
"""


# ---------------------------------------------------------------------------
# Page skeleton
# ---------------------------------------------------------------------------


_MOUNT = "/discovery/"  # absolute URL prefix for the entire subtree


def _render_page(
    title: str,
    nav_current: str,
    body_html: str,
    depth: int = 0,
    narrow: bool = False,
) -> str:
    """Produce a full HTML document with the shared cinematic
    chrome. All hrefs are absolute under `/discovery/` so the
    site works regardless of Firebase's cleanUrls rewrite
    behaviour (relative paths break when the browser treats
    `/discovery` as a file rather than a directory).

    `depth` is kept as a parameter for API compatibility but
    unused — absolute paths make it irrelevant.
    """
    del depth  # unused; retained for call-site stability
    nav_items = [
        ("Overview", f"{_MOUNT}index.html", "overview"),
        ("Equations", f"{_MOUNT}equations/index.html", "equations"),
        ("Canonicals", f"{_MOUNT}canonicals.html", "canonicals"),
        ("Composites", f"{_MOUNT}composites.html", "composites"),
        ("Couplings", f"{_MOUNT}couplings/index.html", "couplings"),
        ("Ledger", f"{_MOUNT}ledger.html", "ledger"),
        ("Methodology", f"{_MOUNT}methodology.html", "methodology"),
        ("AI Review", f"{_MOUNT}ai-review.html", "ai-review"),
        ("About", f"{_MOUNT}about.html", "about"),
        ("Research", f"{_MOUNT}research.html", "research"),
    ]
    nav_html = "".join(
        f'<a href="{href}" class="{"current" if key == nav_current else ""}">{label}</a>'
        for label, href, key in nav_items
    )
    narrow_cls = " narrow" if narrow else ""
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>{html.escape(title)} — hequ.ai/discovery</title>
<link rel="stylesheet" href="{_MOUNT}_assets/site.css">
<link rel="icon" type="image/svg+xml" href="/favicon.svg">
<link rel="mask-icon" href="/favicon.svg" color="#5FB3B3">
<meta name="theme-color" content="#0a0e1a">
</head>
<body>
<canvas id="starfield" aria-hidden="true"></canvas>
<header class="site">
  <div class="inner">
    <a href="{_MOUNT}index.html" class="brand">hequ<span class="dot">.ai</span><span class="path">/ discovery</span></a>
    <nav>{nav_html}</nav>
  </div>
</header>
<main class="container{narrow_cls}">
{body_html}
<footer class="site">
  <p>Discovery engine · Medium milestone 2 · Layer 5 coupling sieve</p>
  <p>Every record is traceable to an append-only SHA-256 hash-chained ledger. Nothing is claimed a discovery without a recorded AI review board vote.</p>
</footer>
</main>
<script src="{_MOUNT}_assets/starfield.js"></script>
</body>
</html>
"""


# ---------------------------------------------------------------------------
# Shared helpers
# ---------------------------------------------------------------------------


def _outcome_badge(outcome: str) -> str:
    cls = outcome.lower()
    return f'<span class="badge {cls}">{html.escape(outcome.upper())}</span>'


def _tier_badge(tier: str) -> str:
    short = {"tier1_equivalence": "tier1", "tier2_similarity": "tier2", "tier3_conjectural": "tier3"}.get(tier, "neutral")
    label = {"tier1_equivalence": "Tier I — Equivalence", "tier2_similarity": "Tier II — Similarity", "tier3_conjectural": "Tier III — Conjectural"}.get(tier, tier)
    return f'<span class="badge {short}">{html.escape(label)}</span>'


def _slug(s: str) -> str:
    return "".join(c if c.isalnum() else "-" for c in s).strip("-").lower()


def _coupling_slug(eq_a: str, eq_b: str, var_a: str, var_b: str, kind: str) -> str:
    return f"{_slug(eq_a)}--{_slug(eq_b)}--{_slug(var_a)}--{_slug(var_b)}--{_slug(kind)}"


def _domain_label(domain: str) -> str:
    return domain.replace("_", " ").title()


# ---------------------------------------------------------------------------
# Overview page
# ---------------------------------------------------------------------------


def build_overview(
    equations: Dict[str, TypedExpression],
    ledger_summary: Dict[str, int],
    coupling_stats: Dict[str, int],
    featured: List[Dict[str, Any]],
    canonicals: List[Dict[str, Any]],
    composites: List[Dict[str, Any]],
) -> str:
    b: List[str] = []
    b.append('<div class="page-intro">')
    b.append('<span class="overline">Discovery Engine · Medium Milestone II · Phase 13 (in flight)</span>')
    b.append('<h1>The <em>unity</em> of equations,<br>verified by real math.</h1>')
    b.append('<p class="lead">A cross-domain coupling engine with four layered checks, a four-phase AI review board modelled on academic peer review, and a formal scope-frozen discharge protocol. Every reference value comes from a real symbolic math engine — sympy, mpmath, and python-flint — not from an LLM. The board is asked for formulas and citations; the architect runs the arithmetic.</p>')
    b.append('</div>')

    # Top row: the substantive numbers
    b.append('<div class="stat-grid">')
    b.append(f'<div class="stat"><div class="value">{len(equations)}</div><div class="label">equations loaded</div></div>')
    b.append(f'<div class="stat"><div class="value">{len(canonicals)}</div><div class="label">canonical problems verified</div></div>')
    b.append(f'<div class="stat"><div class="value">{len(composites)}</div><div class="label">composites verified</div></div>')
    b.append(f'<div class="stat"><div class="value">{ledger_summary.get("empirical", 0)}</div><div class="label">empirical ledger entries</div></div>')
    b.append('</div>')

    # Section: Phase 12 + Phase 13 timeline
    b.append('<h2>Where the engine is now</h2>')
    b.append('<p class="prose">Phase 12 established the foundation: six flagship equations — Newton II, Hooke, Fourier, Fick, Ohm, Work-Energy — each with a real canonical problem that passes the four-check verification pipeline (symbolic canonicalization, stratified property-based sampling, high-precision mpmath, python-flint interval arithmetic). Phase 13 layers composites on top: two parent equations plus a transducer producing a new physical system whose prediction is verified against a textbook reference.</p>')

    b.append('<div class="phases">')
    b.append('<div class="phase"><span class="roman">12.1</span><h3>Canonical problem library</h3><p>Each equation in the corpus gets a <code>problems.yaml</code> with at least one closed-form problem and a board-sourced citation chain. The reference numeric value is computed locally by a real CAS, never by the board. Six equations covered; more coming.</p></div>')
    b.append('<div class="phase"><span class="roman">12.2</span><h3>Four-check verification</h3><p>Symbolic equivalence via canonicalization (rational normalization → trig/power simp → polynomial remainder → branch-cut-aware discriminating random eval). Hypothesis-based stratified property testing. mpmath high-precision fragility check. python-flint interval arithmetic as the genuinely independent numeric engine.</p></div>')
    b.append('<div class="phase"><span class="roman">13.1</span><h3>Composites from parents</h3><p>Two verified parent equations plus a transducer compose into a new physical system. Newton II + Hooke → simple harmonic oscillator. Newton II + Work-Energy → work done by constant force. Each composite gets its own reference value, its own four-check verification, its own ledger entry.</p></div>')
    b.append('<div class="phase"><span class="roman">13.2</span><h3>Port-Hamiltonian transducers</h3><p>Every cross-domain coupling carries a named transducer with explicit ports (effort/flow), Dirac structure, and a symbolic power-conservation equation verified at composition time — conservation by construction, not by post-hoc numeric check.</p></div>')
    b.append('<div class="phase"><span class="roman">∞</span><h3>AI review board</h3><p>Four-phase academic-mirror protocol: independent drafts, consolidated briefing + informed vote, editor synthesis, bounded rebuttal. <b>Three core reviewers</b> — Claude Opus 4.6 · OpenAI GPT-5 · Gemini 2.5 Pro — with <b>Grok-4 as optional fourth seat</b> on high-stakes governance rounds (architecture review, adversarial testing). Cost-neutrality disclaimer, specialist personas, rubric scoring, COI self-declaration, all-must-respond enforcement.</p></div>')
    b.append('<div class="phase"><span class="roman">§11h</span><h3>No corner cuts</h3><p>On any verification failure, the Failure Investigation Protocol fires: state audit, assumption audit, literature RAG, board failure review. Equation modifications require explicit user approval. Tolerance loosening is categorically forbidden.</p></div>')
    b.append('</div>')

    # Section: canonical problems verified
    if canonicals:
        b.append('<h2>Canonical problems in the ledger</h2>')
        b.append(f'<p>{len(canonicals)} equations each with a verified closed-form problem. Board provided the formula and primary-source citations; local sympy + mpmath computed the authoritative numerical value; four-check verification passed.</p>')
        b.append('<div class="card-grid">')
        for c in canonicals[:12]:
            val_str = f"{c['value']:.6g}" if isinstance(c['value'], (int, float)) else "?"
            b.append(
                f'<div class="card" style="cursor:default">'
                f'<div class="card-id">{html.escape(c["equation_id"])}</div>'
                f'<div class="card-name">{html.escape(c["problem_id"])}</div>'
                f'<div class="card-math">{html.escape(val_str)} {html.escape(c.get("unit",""))}</div>'
                f'<div class="card-meta"><span class="badge empirical">verified</span></div>'
                f'</div>'
            )
        b.append('</div>')

    # Section: composites
    if composites:
        b.append('<h2>Composites verified</h2>')
        b.append('<p>Phase 13 composites: two parent equations plus a coupling produce a new physical prediction, verified against a textbook reference with the same four-check pipeline as a single-equation canonical.</p>')
        b.append('<div class="card-grid">')
        for c in composites:
            val_str = f"{c['value']:.6g}" if isinstance(c['value'], (int, float)) else "?"
            b.append(
                f'<div class="card" style="cursor:default">'
                f'<div class="card-id">{html.escape(c["composite_id"])}</div>'
                f'<div class="card-name">{html.escape(c["eq_a"])} <span style="color:var(--accent);font-style:italic">+</span> {html.escape(c["eq_b"])}</div>'
                f'<div class="card-math">{html.escape(val_str)} {html.escape(c.get("unit",""))}</div>'
                f'<div class="card-meta"><span class="badge empirical">verified</span> <span style="color:var(--fg-dim);font-size:0.7rem">{html.escape(c.get("tier","").replace("_"," "))}</span></div>'
                f'</div>'
            )
        b.append('</div>')

    # Layer 5 legacy section (kept for audit, but demoted below the Phase 12/13 work)
    b.append('<h2>Layer 5 coupling sieve (Phase 11)</h2>')
    b.append(f'<p>The earlier structural-matching sieve, reviewed by the board in Phase 11 before the current v5 protocol. {coupling_stats.get("tier1",0)} tier-I equivalences and {coupling_stats.get("tier2",0)} tier-II structural analogies were emitted; {ledger_summary.get("proved",0)} were promoted to PROVED under the old protocol. These records remain in the ledger as Phase 11 audit and are being re-evaluated under the stricter Phase 12+ rules.</p>')

    b.append('<h2>Ledger at a glance</h2>')
    b.append('<div class="stat-grid" style="grid-template-columns: repeat(auto-fit, minmax(160px, 1fr))">')
    for outcome in ("proved", "empirical", "conjectural", "rejected"):
        cnt = ledger_summary.get(outcome, 0)
        if cnt:
            b.append(f'<div class="stat"><div class="value">{cnt}</div><div class="label">{outcome}</div></div>')
    b.append('</div>')
    b.append(f'<p>Every record — proof, conjecture, rejection, failure investigation, or board discharge — is browsable on the <a href="{_MOUNT}ledger.html">full ledger</a>. The full protocol is documented on the <a href="{_MOUNT}methodology.html">methodology</a> page.</p>')
    return _render_page("Overview", "overview", "\n".join(b), depth=0)


# ---------------------------------------------------------------------------
# Equations pages
# ---------------------------------------------------------------------------


def build_equations_index(equations: Dict[str, TypedExpression]) -> str:
    b: List[str] = []
    b.append('<div class="page-intro">')
    b.append('<span class="overline">The Corpus</span>')
    b.append(f'<h1>{len(equations)} <em>equations</em>.<br>{len(set(eq.domain for eq in equations.values()))} domains.</h1>')
    b.append('<p class="lead">Each entry is parsed to a canonical implicit form with pint-typed variables and a four-field I-ADOPT semantic descriptor keyed against QUDT.</p>')
    b.append('</div>')

    by_domain: Dict[str, List[TypedExpression]] = {}
    for eq in equations.values():
        by_domain.setdefault(eq.domain, []).append(eq)
    for domain in sorted(by_domain):
        b.append('<section class="domain-section">')
        b.append(f'<div class="domain-label">{html.escape(_domain_label(domain))}</div>')
        b.append('<div class="card-grid">')
        for eq in sorted(by_domain[domain], key=lambda e: e.id):
            b.append(
                f'<a class="card" href="{_MOUNT}equations/{eq.id}.html">'
                f'<div class="card-id">{html.escape(eq.id)}</div>'
                f'<div class="card-name">{html.escape(eq.name)}</div>'
                f'<div class="card-math">{html.escape(str(eq.canonical_form))} = 0</div>'
                f'<div class="card-meta"><span>{len(eq.variables)} variables</span><span>{len(eq.axioms)} axioms</span></div>'
                f'</a>'
            )
        b.append('</div>')
        b.append('</section>')
    return _render_page("Equations", "equations", "\n".join(b), depth=1)


def build_equation_detail(eq: TypedExpression) -> str:
    b: List[str] = []
    b.append('<div class="page-intro">')
    b.append(f'<span class="overline">{html.escape(eq.id)} · {html.escape(_domain_label(eq.domain))}</span>')
    b.append(f'<h1>{html.escape(eq.name)}</h1>')
    b.append(f'<div class="math-display">{html.escape(str(eq.canonical_form))} = 0</div>')
    b.append('</div>')

    if eq.canonical_form_derivatives is not None:
        b.append('<h2>Derivative form</h2>')
        b.append(f'<div class="math-display">{html.escape(str(eq.canonical_form_derivatives))} = 0</div>')

    b.append('<h2>Variables</h2>')
    b.append('<div class="card-grid">')
    for name, var in sorted(eq.variables.items()):
        desc = var.descriptor
        desc_html = ""
        if desc:
            desc_html = (
                '<dl class="kv" style="margin-top:0.8rem">'
                f'<dt>Object</dt><dd>{html.escape(desc.object_of_interest)}</dd>'
                f'<dt>Property</dt><dd>{html.escape(desc.property_uri.rsplit("/", 1)[-1])}</dd>'
                f'<dt>Context</dt><dd>{html.escape(desc.context)}</dd>'
                + (f'<dt>Constraint</dt><dd>{html.escape(desc.constraint)}</dd>' if desc.constraint else '')
                + '</dl>'
            )
        b.append(
            f'<div class="card" style="cursor:default">'
            f'<div class="card-id">variable</div>'
            f'<div class="card-name" style="font-size: 2.2rem; font-family: var(--mono); color: var(--accent-bright)">{html.escape(name)}</div>'
            f'<p style="margin: 0.5rem 0 0; font-size: 0.92rem">{html.escape(var.meaning)}</p>'
            f'<div class="card-meta"><span class="mono">{html.escape(var.unit)}</span></div>'
            f'{desc_html}'
            f'</div>'
        )
    b.append('</div>')

    if eq.axioms:
        b.append('<h2>Axioms</h2>')
        b.append('<p>' + " ".join(f'<span class="badge neutral" style="margin-right:0.3rem">{html.escape(a)}</span>' for a in sorted(eq.axioms)) + '</p>')

    if eq.assumptions:
        b.append('<h2>Assumptions</h2>')
        b.append('<ul>')
        for a in eq.assumptions:
            b.append(f'<li>{html.escape(a)}</li>')
        b.append('</ul>')

    if eq.derivation_from:
        b.append('<h2>Derivation</h2>')
        b.append('<ul>')
        for d in eq.derivation_from:
            b.append(f'<li>{html.escape(d)}</li>')
        b.append('</ul>')

    if eq.references:
        b.append('<h2>References</h2>')
        b.append('<ul>')
        for r in eq.references:
            b.append(f'<li>{html.escape(r)}</li>')
        b.append('</ul>')

    b.append(f'<a class="back-link" href="{_MOUNT}equations/index.html">← back to corpus</a>')
    return _render_page(eq.name, "equations", "\n".join(b), depth=1)


# ---------------------------------------------------------------------------
# Coupling pages
# ---------------------------------------------------------------------------


def build_couplings_index(couplings: List[Dict[str, Any]]) -> str:
    b: List[str] = []
    b.append('<div class="page-intro">')
    b.append('<span class="overline">Coupling Hypotheses</span>')
    b.append(f'<h1>{len(couplings)} <em>candidate</em> couplings.</h1>')
    b.append('<p class="lead">Each hypothesis surviving the two-gate prefilter, scored against the physical-constraint filter and the emergent-properties analysis.</p>')
    b.append('</div>')

    # Group by outcome for visual grouping
    groups: Dict[str, List[Dict[str, Any]]] = {}
    for c in couplings:
        groups.setdefault(c["outcome"], []).append(c)

    for outcome in ("proved", "empirical", "conjectural", "rejected"):
        if outcome not in groups:
            continue
        b.append('<section class="domain-section">')
        b.append(f'<div class="domain-label">{_outcome_badge(outcome)}</div>')
        b.append('<div class="card-grid">')
        for c in groups[outcome]:
            tier_short = c["tier"].replace("_equivalence", "").replace("_similarity", "").replace("_conjectural", "")
            b.append(
                f'<a class="card" href="{_MOUNT}couplings/{c["slug"]}.html">'
                f'<div class="card-id">{html.escape(tier_short.upper())}</div>'
                f'<div class="card-name">{html.escape(c["eq_a"])} <span style="color:var(--accent)">↔</span> {html.escape(c["eq_b"])}</div>'
                f'<div class="card-math">{html.escape(c["var_a"])} ↔ {html.escape(c["var_b"])}</div>'
                f'<div class="card-meta">{_tier_badge(c["tier"])}</div>'
                f'</a>'
            )
        b.append('</div>')
        b.append('</section>')
    return _render_page("Couplings", "couplings", "\n".join(b), depth=1)


def build_coupling_detail(c: Dict[str, Any]) -> str:
    b: List[str] = []

    b.append('<div class="page-intro">')
    b.append(f'<span class="overline">Coupling · {html.escape(c["tier"].replace("_", " ").title())}</span>')
    b.append(f'<h1><em>{html.escape(c["var_a"])}</em> ↔ <em>{html.escape(c["var_b"])}</em></h1>')
    b.append(f'<p class="lead">{_tier_badge(c["tier"])} &nbsp; {_outcome_badge(c["outcome"])}</p>')
    b.append('</div>')

    b.append('<div class="pairing">')
    for side_key, label, eq, var, desc in (
        ("left", "Equation A", c["eq_a"], c["var_a"], c["descriptor_a"]),
        ("right", "Equation B", c["eq_b"], c["var_b"], c["descriptor_b"]),
    ):
        if side_key == "left":
            pass
        b.append(f'<div class="side {side_key}">')
        b.append(f'<div class="side-label">{label}</div>')
        b.append(f'<div class="side-eq-id"><a href="{_MOUNT}equations/{html.escape(eq)}.html" style="color:inherit; border:none">{html.escape(eq)}</a></div>')
        b.append(f'<div class="side-var">{html.escape(var)}</div>')
        b.append('<dl class="kv">')
        b.append(f'<dt>Object</dt><dd>{html.escape(desc["object_of_interest"])}</dd>')
        b.append(f'<dt>Property</dt><dd>{html.escape(desc["property"].rsplit("/", 1)[-1])}</dd>')
        b.append(f'<dt>Context</dt><dd>{html.escape(desc["context"])}</dd>')
        if desc.get("constraint"):
            b.append(f'<dt>Constraint</dt><dd>{html.escape(desc["constraint"])}</dd>')
        b.append('</dl>')
        b.append('</div>')
        if side_key == "left":
            b.append('<div class="connector"><div class="arrow">↔</div></div>')
    b.append('</div>')

    b.append('<h2>Sieve rationale</h2>')
    b.append(f'<p class="prose">{html.escape(c["reason"])}</p>')

    phys = c.get("physical")
    if phys:
        b.append('<h2>Physical constraint filter</h2>')
        for r in phys["results"]:
            cls = r["outcome"]
            verdict_label = {"passed": "PASSED", "failed": "FAILED", "not_applicable": "not applicable"}[cls]
            b.append(f'<div class="check-card {cls}">')
            b.append('<div class="check-head">')
            b.append(f'<span class="check-name">{html.escape(r["check"].replace("_", " "))}</span>')
            b.append(f'<span class="badge {"proved" if cls=="passed" else "rejected" if cls=="failed" else "neutral"}">{verdict_label}</span>')
            b.append('</div>')
            b.append(f'<p class="reasoning">{html.escape(r["reasoning"])}</p>')
            b.append('</div>')

    emergent = c.get("emergent")
    if emergent and any(emergent.get(k) for k in ("steady_states", "stability", "buckingham_pi_groups", "emergent_pi_groups", "conserved_quantities")):
        b.append('<h2>Emergent properties</h2>')
        if emergent.get("conserved_quantities"):
            b.append('<h3>Conserved quantities</h3>')
            for q in emergent["conserved_quantities"]:
                b.append(f'<div class="math-display">{html.escape(q)}</div>')
        if emergent.get("steady_states"):
            b.append('<h3>Steady states</h3>')
            for ss in emergent["steady_states"]:
                pairs = ", ".join(f"{k}={v}" for k, v in ss.items())
                b.append(f'<div class="math-display">({html.escape(pairs)})</div>')
        if emergent.get("stability"):
            b.append('<h3>Linear stability</h3>')
            for st in emergent["stability"]:
                b.append('<div class="panel tight">')
                b.append('<dl class="kv">')
                b.append(f'<dt>Class</dt><dd>{html.escape(str(st.get("classification","")))}</dd>')
                eigs = ", ".join(str(e) for e in st.get("eigenvalues", []))
                b.append(f'<dt>Eigenvalues</dt><dd>{html.escape(eigs)}</dd>')
                b.append('</dl>')
                if st.get("notes"):
                    b.append(f'<p class="reasoning" style="margin-top:0.6rem; font-family:var(--serif); font-style:italic">{html.escape(st["notes"])}</p>')
                b.append('</div>')
        if emergent.get("emergent_pi_groups"):
            b.append('<h3>Emergent Buckingham Π groups</h3>')
            b.append('<p style="font-size:0.92rem; color:var(--fg-dim)">Dimensionless combinations that mix parameters from both equations — only appear in the composite system.</p>')
            for g in emergent["emergent_pi_groups"]:
                b.append(f'<div class="math-display">{html.escape(g)}</div>')

    ai = c.get("ai_review")
    if ai:
        b.append('<h2>AI review board</h2>')
        b.append(f'<p class="prose">{html.escape(ai.get("rationale", ""))}</p>')
        for vote in ai.get("votes", []):
            verdict = vote.get("verdict", "")
            vbadge = {
                "approve": '<span class="badge proved">APPROVE</span>',
                "reject": '<span class="badge rejected">REJECT</span>',
                "needs_more_info": '<span class="badge conjectural">NEEDS INFO</span>',
                "error": '<span class="badge neutral">ERROR</span>',
            }.get(verdict, verdict)
            b.append('<div class="reviewer-card">')
            b.append('<div class="reviewer-head">')
            b.append(f'<span class="reviewer-name">{html.escape(vote.get("reviewer", ""))}</span>')
            b.append(f'{vbadge}')
            b.append('</div>')
            b.append(f'<p class="reasoning">{html.escape(vote.get("reason", ""))}</p>')
            b.append('</div>')

    b.append(f'<a class="back-link" href="{_MOUNT}couplings/index.html">← back to couplings</a>')
    title = f'{c["eq_a"]}.{c["var_a"]} ↔ {c["eq_b"]}.{c["var_b"]}'
    return _render_page(title, "couplings", "\n".join(b), depth=1)


# ---------------------------------------------------------------------------
# Ledger page
# ---------------------------------------------------------------------------


def build_ledger_page(records: List[Dict[str, Any]]) -> str:
    b: List[str] = []
    b.append('<div class="page-intro">')
    b.append('<span class="overline">The Ledger</span>')
    b.append(f'<h1>{len(records)} <em>recorded</em> hypotheses.</h1>')
    b.append('<p class="lead">Append-only JSONL with SHA-256 hash chain. Nothing deleted; rejections preserved with rejection criterion. This is the single source of truth for what the engine has ever tried.</p>')
    b.append('</div>')

    b.append('<div class="logbook">')
    b.append('<div class="logbook-row head"><div>#</div><div>A</div><div>B</div><div>kind</div><div>outcome</div><div class="review">rev</div></div>')
    for i, r in enumerate(records, start=1):
        review = '<span class="badge conjectural">rev</span>' if r.get("review_required") else ""
        b.append(
            f'<div class="logbook-row">'
            f'<div class="idx">{i:04d}</div>'
            f'<div class="eq">{html.escape(r["eq_a"])}</div>'
            f'<div class="eq eq-b">{html.escape(r["eq_b"])}</div>'
            f'<div class="kind">{html.escape(r["kind"])}</div>'
            f'<div>{_outcome_badge(r["outcome"])}</div>'
            f'<div class="review">{review}</div>'
            f'</div>'
        )
    b.append('</div>')
    return _render_page("Ledger", "ledger", "\n".join(b), depth=0)


# ---------------------------------------------------------------------------
# AI review page
# ---------------------------------------------------------------------------


def build_ai_review_page(review_md: Optional[str]) -> str:
    b: List[str] = []
    b.append('<div class="page-intro">')
    b.append('<span class="overline">AI Review Board</span>')
    b.append('<h1>Three minds,<br><em>one verdict</em>.</h1>')
    b.append('<p class="lead">Claude Opus 4.6 · OpenAI GPT-5 · Gemini 2.5 Pro vote independently on every candidate. Unanimous APPROVE promotes to PROVED; any REJECT demotes.</p>')
    b.append('</div>')

    if not review_md:
        b.append('<p>No AI review board run has been recorded yet.</p>')
    else:
        lines = review_md.splitlines()
        in_para: List[str] = []
        def flush_para() -> None:
            if in_para:
                import re as _re
                text = " ".join(in_para)
                text = _re.sub(r"`([^`]+)`", lambda m: f"<code>{html.escape(m.group(1))}</code>", text)
                while "**" in text:
                    text = text.replace("**", "<b>", 1)
                    text = text.replace("**", "</b>", 1)
                b.append(f'<p>{text}</p>')
                in_para.clear()
        for ln in lines:
            s = ln.strip()
            if not s:
                flush_para()
                continue
            if s.startswith("# "):
                flush_para()
                # Skip top H1 (already have page intro)
                continue
            if s.startswith("## "):
                flush_para()
                b.append(f'<h2>{html.escape(s[3:])}</h2>')
            elif s.startswith("### "):
                flush_para()
                b.append(f'<h3 style="text-transform:none; letter-spacing:0; font-family:var(--serif); font-size:1.4rem; color:var(--fg); margin-top:1.8rem">{html.escape(s[4:])}</h3>')
            elif s.startswith("- "):
                flush_para()
                item = s[2:]
                import re as _re2
                item = _re2.sub(r"`([^`]+)`", lambda m: f"<code>{html.escape(m.group(1))}</code>", item)
                while "**" in item:
                    item = item.replace("**", "<b>", 1)
                    item = item.replace("**", "</b>", 1)
                b.append(f'<div class="panel tight">{item}</div>')
            else:
                in_para.append(html.escape(s))
        flush_para()

    return _render_page("AI Review", "ai-review", "\n".join(b), depth=0)


# ---------------------------------------------------------------------------
# About page
# ---------------------------------------------------------------------------


def build_canonicals_page(canonicals: List[Dict[str, Any]]) -> str:
    b: List[str] = []
    b.append('<div class="page-intro">')
    b.append('<span class="overline">Phase 12 · Canonical Problems</span>')
    b.append(f'<h1>{len(canonicals)} <em>canonical</em> problems.</h1>')
    b.append('<p class="lead">One closed-form problem per equation in the corpus, each with a board-sourced citation chain and a locally-verified numerical answer. The board is asked for the formula and the primary-source references — never for the number. The number comes from a real CAS (sympy + mpmath + python-flint).</p>')
    b.append('</div>')

    b.append('<h2>The v5 protocol</h2>')
    b.append('<p class="prose">Language models recall formulas reliably and cite primary sources cleanly. They do not do precise arithmetic — a pendulum period calculation that requires transcendentals can be off by parts in 10⁵ from run to run on the same prompt. The protocol therefore treats the board as a formula and citation source, and runs the actual math locally with deterministic tools. The board\'s best-effort <code>value_attempt</code> is still captured in the ledger as capability data on when LLMs can and can\'t do math, but it is never load-bearing.</p>')

    b.append('<h2>The four checks</h2>')
    b.append('<div class="phases">')
    b.append('<div class="phase"><span class="roman">A</span><h3>Symbolic equivalence</h3><p>The board\'s formula must collapse to zero against the architect\'s local formula under a canonicalization pipeline — rational normalization, trig and power simplification, polynomial remainder, and a discriminating random-point evaluation that deliberately avoids branch cuts and singularities.</p></div>')
    b.append('<div class="phase"><span class="roman">B</span><h3>Property-based sampling</h3><p>Hypothesis-style stratified sampling across orders of magnitude for every declared variable, with boundary cases injected (min, max, zero, unity, near-singularity) and a reproducible seed logged in the ledger. 200 samples in Phase 12; power analysis drives the number toward 10,000 in Phase 13+.</p></div>')
    b.append('<div class="phase"><span class="roman">C</span><h3>High-precision fragility</h3><p>mpmath at 50 decimal places compared against sympy at 15 digits — this is explicitly labeled a <em>within-sympy</em> fragility check, not an independent cross-CAS check, because mpmath is sympy\'s own numerical backend.</p></div>')
    b.append('<div class="phase"><span class="roman">D</span><h3>python-flint interval</h3><p>The genuinely orthogonal numeric engine: Arb-based ball arithmetic that shares no code with sympy. Phase 12 is best-effort with graceful skip; Phase 13+ makes it a hard requirement.</p></div>')
    b.append('</div>')

    b.append('<h2>Verified canonical problems</h2>')
    if not canonicals:
        b.append('<p>No canonical problems have been verified yet.</p>')
    else:
        b.append('<div class="card-grid">')
        for c in canonicals:
            val_str = f"{c['value']:.10g}" if isinstance(c['value'], (int, float)) else "?"
            cite_count = len(c.get("citations", []))
            b.append(
                f'<div class="card" style="cursor:default">'
                f'<div class="card-id">{html.escape(c["equation_id"])}</div>'
                f'<div class="card-name">{html.escape(c["problem_id"])}</div>'
                f'<div class="card-math">{html.escape(val_str)} {html.escape(c.get("unit",""))}</div>'
                f'<div class="card-meta">'
                f'<span class="badge empirical">{html.escape(c.get("status","verified"))}</span>'
                f' <span style="color:var(--fg-dim);font-size:0.75rem">{cite_count} citation(s)</span>'
                f'</div>'
                f'</div>'
            )
        b.append('</div>')

    return _render_page("Canonicals", "canonicals", "\n".join(b), depth=0)


def build_composites_page(composites: List[Dict[str, Any]]) -> str:
    b: List[str] = []
    b.append('<div class="page-intro">')
    b.append('<span class="overline">Phase 13 · Composites</span>')
    b.append(f'<h1>{len(composites)} <em>composite</em> systems verified.</h1>')
    b.append('<p class="lead">A composite is two parent equations plus a coupling that produce a new physical system. The parents must each have passed Phase 12 canonical verification. The coupling is either a tier-1 equivalence (same variable in both parents under the same I-ADOPT descriptor) or a tier-2 structural analogy with a named port-Hamiltonian transducer. The composite\'s own canonical problem is then verified under the same four-check pipeline as any single-equation canonical.</p>')
    b.append('</div>')

    b.append('<h2>How a composite is built</h2>')
    b.append('<p class="prose">Given two canonically-verified parents and a coupling, the engine substitutes variables according to the transducer and generates the composite equation of motion. A canonical problem for the composite is authored — typically a real physical scenario with a closed-form textbook answer (the simple harmonic oscillator period, the DC motor back-EMF torque curve, the Soret thermodiffusion coefficient). That problem goes through the same four-check verification as any Phase 12 canonical.</p>')
    b.append('<p>The composite\'s ledger entry carries its parents, the coupling kind, the transducer identity, the reference value, and every check result — full provenance, append-only, hash-chained.</p>')

    b.append('<h2>Verified composites</h2>')
    if not composites:
        b.append('<p>No composites have been verified yet.</p>')
    else:
        b.append('<div class="card-grid">')
        for c in composites:
            val_str = f"{c['value']:.10g}" if isinstance(c['value'], (int, float)) else "?"
            tier_label = c.get("tier", "").replace("_", " ").title() or "coupling"
            b.append(
                f'<div class="card" style="cursor:default">'
                f'<div class="card-id">{html.escape(c["composite_id"])}</div>'
                f'<div class="card-name">{html.escape(c["eq_a"])} <span style="color:var(--accent);font-style:italic">+</span> {html.escape(c["eq_b"])}</div>'
                f'<div class="card-math">{html.escape(val_str)} {html.escape(c.get("unit",""))}</div>'
                f'<div class="card-meta">'
                f'<span class="badge empirical">{html.escape(c.get("status","verified"))}</span>'
                f' <span style="color:var(--fg-dim);font-size:0.75rem">{html.escape(tier_label)}</span>'
                f'</div>'
                f'<div class="card-meta" style="margin-top:0.3rem; color: var(--fg-dim); font-size:0.72rem">{html.escape(c.get("v_a",""))} ↔ {html.escape(c.get("v_b",""))}</div>'
                f'</div>'
            )
        b.append('</div>')

    b.append('<h2>Phase 13 roadmap</h2>')
    b.append('<ul>')
    b.append('<li>Newton II + Hooke → simple harmonic oscillator period &nbsp;<span class="badge empirical">verified</span></li>')
    b.append('<li>Newton II + Work-Energy → work done by constant force &nbsp;<span class="badge empirical">verified</span></li>')
    b.append('<li>Fourier + Fick → Soret thermodiffusion &nbsp;<span class="badge conjectural">queued</span> <span style="color:var(--fg-dim);font-size:0.72rem">(first cross-domain; needs Soret transducer)</span></li>')
    b.append('<li>Newton II + Ohm → DC motor back-EMF torque curve &nbsp;<span class="badge conjectural">queued</span> <span style="color:var(--fg-dim);font-size:0.72rem">(electromechanical; needs motor-constant transducer)</span></li>')
    b.append('<li>Arrhenius + Fick → reaction-diffusion wavefront speed &nbsp;<span class="badge conjectural">queued</span> <span style="color:var(--fg-dim);font-size:0.72rem">(needs Arrhenius canonical first)</span></li>')
    b.append('</ul>')

    return _render_page("Composites", "composites", "\n".join(b), depth=0)


def build_methodology_page() -> str:
    b: List[str] = []
    b.append('<div class="page-intro">')
    b.append('<span class="overline">Methodology</span>')
    b.append('<h1>How a <em>coupling</em> earns its place.</h1>')
    b.append('<p class="lead">The engine does not trust itself. It does not trust any single model. It does not trust a clever algebraic match. Every claim must survive four independent levels of evidence and a four-phase peer review modelled directly on academic practice.</p>')
    b.append('</div>')

    b.append('<h2>The thesis</h2>')
    b.append('<p class="prose">The difference between a coincidence and a genuine cross-domain coupling is <b>executable realization</b>. A real coupling admits a physical system in which both equations hold simultaneously, on the same substrate, and produce the same measurable answer. Newton plus Hooke is real because mass–spring oscillators exist in laboratories and the engine can simulate one and compare against a measured period. Newton plus Shannon entropy is not real because no laboratory object obeys both equations at once. Every prior attempt at cross-domain discovery — SINDy, AI Feynman, PySR, SemGen, DARPA SKEMA — argued about symbols and ignored execution. This engine runs experiments.</p>')

    b.append('<h2>Evidence hierarchy</h2>')
    b.append('<p>Every coupling hypothesis accumulates evidence at four levels, each stricter than the last. Confidence is multiplicative — any level failing drags the whole down.</p>')
    b.append('<div class="phases">')
    b.append('<div class="phase"><span class="roman">L1</span><h3>Canonical problem</h3><p>Each equation in the corpus has a real problem with a known reference value. The equation passes L1 only if the problem\'s pytest unit test executes and the computed answer matches the reference within declared tolerance.</p></div>')
    b.append('<div class="phase"><span class="roman">L2</span><h3>Composite notebook</h3><p>When two equations are coupled, a real Jupyter notebook solves the composite system numerically and asserts against a board-sourced reference value. The notebook runs in a sandboxed container with no internet, a pinned image SHA, and a content-hashed ledger entry. No hidden human-in-the-loop.</p></div>')
    b.append('<div class="phase"><span class="roman">L3</span><h3>Literature citation</h3><p>At least two of the three AI reviewers must produce independent primary-source citations to the coupling from established textbooks or peer-reviewed papers. Shared-source or paraphrased citations do not count — DOI-level independence is required.</p></div>')
    b.append('<div class="phase"><span class="roman">L4</span><h3>Live sensor agreement</h3><p>The strongest level. A real physical sensor (phone IMU, weather station, smart meter, market feed, or quantum computer) produces measurements that match the composite prediction within a declared noise envelope, with Bayesian posterior updates over a rolling window.</p></div>')
    b.append('</div>')

    b.append('<h2>Promotion thresholds</h2>')
    b.append('<p>Labels are strictly monotonic in rigor. A coupling only reaches the higher tiers by passing more evidence levels and a stricter consensus gate.</p>')
    b.append('<table>')
    b.append('<tr><th>Label</th><th>Confidence</th><th>Required levels</th><th>Board gate</th></tr>')
    b.append('<tr><td><span class="badge conjectural">CONJECTURAL</span></td><td>C &lt; 0.30</td><td>any</td><td>—</td></tr>')
    b.append('<tr><td><span class="badge empirical">EMPIRICAL</span></td><td>C ≥ 0.30</td><td>L1 + L2</td><td>≥ 2 of 3 approve</td></tr>')
    b.append('<tr><td><span class="badge proved">PROVED</span></td><td>C ≥ 0.60</td><td>L1 + L2 + L3</td><td>unanimous approve</td></tr>')
    b.append('<tr><td><span class="badge tier1">GROUNDED</span></td><td>C ≥ 0.85</td><td>L1 + L2 + L3 + L4</td><td>unanimous + live sensor</td></tr>')
    b.append('</table>')
    b.append('<p>A sidebar class <code>DUALITY</code> applies to mathematical isomorphisms such as Wick rotation or log-price substitution. These cannot be promoted past EMPIRICAL on symbolic evidence alone — they need independent physical sensor agreement from both domains. Mathematical equivalence is not a physical coupling.</p>')

    b.append('<h2>The four-phase review protocol</h2>')
    b.append('<p class="prose">Every coupling, and every architectural decision, is reviewed by a board that mirrors real academic peer review. The protocol runs in four explicit phases and produces a binding editorial decision. The <b>three core reviewers</b> are Claude Opus 4.6, OpenAI GPT-5, and Gemini 2.5 Pro, each assigned a specialist persona matched to the topic under review. <b>Grok-4 (xAI) is enrolled as an optional fourth seat</b> that is included on high-stakes governance rounds — architecture design reviews, scope-frozen discharge rounds, brand board reviews — and omitted on operational lookups such as canonical-problem reference sourcing. Whether a given round ran as a 3-seat or 4-seat board is recorded in its ledger entry.</p>')

    b.append('<div class="phases">')
    b.append('<div class="phase"><span class="roman">A</span><h3>Independent draft</h3><p>Each reviewer receives the submission in complete isolation. No cross-contamination. Every reply begins with a conflict-of-interest self-declaration (did this reviewer encounter the specific formulation during training?), then a five-dimension rubric score, then a draft verdict with strengths and concerns.</p></div>')
    b.append('<div class="phase"><span class="roman">B</span><h3>Informed vote</h3><p>The three Phase A drafts are consolidated into a board briefing document showing each reviewer what the others said. Each reviewer then produces a final updated verdict, explicitly responding to peer concerns — agreeing, disagreeing, or updating their position. This is the phase that breaks correlated blind spots.</p></div>')
    b.append('<div class="phase"><span class="roman">C</span><h3>Editor synthesis</h3><p>A fourth distinct model call reads all the Phase B verdicts and writes the binding editorial decision. The editor weights reasoning quality, not vote count, and can override a naive tally when one reviewer\'s argument is visibly stronger. Reviewer disagreement on fundamentals is explicitly flagged in the ledger.</p></div>')
    b.append('<div class="phase"><span class="roman">D</span><h3>Bounded rebuttal</h3><p>If the editor returns MODIFY with specific required changes, the submitter is allowed one revision cycle to address them, and the board runs again on the revision. A maximum of two rebuttal cycles are allowed before the decision becomes final. This mirrors the author-response phase standard at CS conferences.</p></div>')
    b.append('</div>')

    b.append('<h2>The rubric</h2>')
    b.append('<p>Every reviewer produces a structured five-dimension score on a 1–5 integer scale. For coupling hypotheses the dimensions are:</p>')
    b.append('<ul>')
    b.append('<li><b>Physical plausibility</b> — does this coupling describe real physics?</li>')
    b.append('<li><b>Dimensional consistency</b> — are the transducer dimensions honest?</li>')
    b.append('<li><b>Literature grounding</b> — is there independent primary-source support?</li>')
    b.append('<li><b>Falsifiability</b> — can the composite be executed and compared against a reference?</li>')
    b.append('<li><b>Novelty / emergent insight</b> — does the coupling produce a new dimensionless group or conserved quantity that neither equation exposes alone?</li>')
    b.append('</ul>')
    b.append('<p>Rubric totals are computed by the editor as weighted sums. Two reviewers scoring a coupling 5 across the board carry more weight in the editor\'s decision than a single reviewer scoring 1s without reasoning.</p>')

    b.append('<h2>Conflict of interest</h2>')
    b.append('<p>At the start of every Phase A reply, each reviewer declares whether it encountered the specific formulation during training. A declared COI does not disqualify the reviewer — all four models share some training on foundational physics literature — but the declaration is logged. If every reviewer seated in the round declares training exposure to an exact formulation, the coupling is flagged with <code>HIGH_COI_CORRELATION_RISK</code> and cannot be promoted past EMPIRICAL without independent experimental evidence at L4.</p>')

    b.append('<h2>Three-way verification of board-sourced references</h2>')
    b.append('<p>Reference values for canonical problems come from the board, not from the architect. The board is asked for <code>{formula_symbolic, substitutions, value, citation}</code> and the architect then runs three independent checks locally before accepting the value:</p>')
    b.append('<ol style="margin-left:1.4rem">')
    b.append('<li><b>Symbolic equivalence</b> — <code>sp.simplify(board_formula − local_formula) == 0</code>. A stronger guarantee than any single-point numeric check.</li>')
    b.append('<li><b>Property-based randomized sampling</b> — 50 unit-consistent parameter draws, all must satisfy the board\'s claimed relationship within tolerance.</li>')
    b.append('<li><b>Cross-CAS high precision</b> — <code>mpmath</code> at 50 decimal places vs sympy single-precision. Disagreement at &gt; 10 decimal places flags the formula as numerically fragile.</li>')
    b.append('</ol>')
    b.append('<p>All three must pass. A single-point agreement alone is insufficient. This breaks the circularity risk — the architect\'s local code is an independent check that does not depend on any model\'s training data.</p>')

    b.append('<h2>The append-only ledger</h2>')
    b.append('<p>Every hypothesis, every rejection, every board vote, every sensor reading, every composite execution result is recorded in an append-only JSONL file with a SHA-256 hash chain. Nothing is deleted. The ledger is the single source of truth for what the engine has ever tried and what happened. A future audit can re-derive every promotion decision from its raw evidence.</p>')

    b.append('<h2>Sandboxed notebook execution</h2>')
    b.append('<p>Every auto-generated composite notebook runs inside a Docker container with pinned image SHA, frozen pip requirements with hashes, no network access, read-only root filesystem, an ephemeral 64 MB tmpfs workspace, non-root UID, memory and CPU cgroup limits, and a per-cell execution timeout. The container\'s SHA and the notebook\'s content hash are both logged in the ledger, so the execution environment is reproducible and tamper-evident.</p>')

    b.append('<h2>Academic analogs</h2>')
    b.append('<p>The four-phase protocol is not invented — it mirrors standard peer review. For the record, the closest academic correspondences:</p>')
    b.append('<ul>')
    b.append('<li><b>Phase A independent drafts</b> — standard practice at Nature, Science, NeurIPS, ICML, ICLR, PRL.</li>')
    b.append('<li><b>Phase B informed response</b> — CS conference rebuttal rounds (NeurIPS, ICML, ICLR, CVPR).</li>')
    b.append('<li><b>Phase C editor synthesis</b> — handling editors at journals, area chairs at conferences.</li>')
    b.append('<li><b>Phase D bounded rebuttal</b> — author response phase, limited to one or two cycles.</li>')
    b.append('<li><b>COI self-declaration</b> — mandatory at every legitimate venue.</li>')
    b.append('<li><b>Specialist reviewer assignment</b> — universal editorial practice.</li>')
    b.append('<li><b>Scoring rubrics</b> — standard at CS conferences; emerging at journals.</li>')
    b.append('<li><b>Pre-registration of hypotheses</b> — Nosek et al. 2018, the preregistration revolution.</li>')
    b.append('</ul>')

    b.append('<h2>v5 rules added after Round 2 discharge</h2>')
    b.append('<p class="prose">The board\'s discharge round produced four additional binding rules beyond the v4 FCS fixes, each closing a specific structural loophole the engine hit in practice:</p>')

    b.append('<div class="phases">')

    b.append('<div class="phase"><span class="roman">v5·1</span><h3>Board is not a CAS</h3><p>The first Phase 12 canonical run caught a language-model arithmetic error: correct formula, correct citations, imprecise decimal. <b>Never ask the board for a precision-critical numerical value.</b> Query for formula and citations; compute the number locally with sympy + mpmath + python-flint. The board\'s <code>value_attempt</code> is logged as capability data but never load-bearing.</p></div>')

    b.append('<div class="phase"><span class="roman">v5·2</span><h3>All must respond</h3><p>Non-response from any board member (HTTP error, timeout, parse failure) counts as <b>dissent</b>, not neutral. Rounds cannot approve with partial quorum. Every model call has 5-retry exponential backoff (2→4→8→16→32 s). Persistent non-response escalates to the user with a Decision Matrix of retry / proceed-with-acknowledged-dissent / wait-for-vendor.</p></div>')

    b.append('<div class="phase"><span class="roman">v5·3</span><h3>Scope-frozen discharge</h3><p>After Round 1 produces the Frozen Concern Set, Round 2+ reviewers can only score each FCS item as addressed / partially / not-addressed — they cannot raise new concerns. Process violations are logged and escalated to the user as the only authority that can reopen the FCS. This breaks the infinite-review-drift that would otherwise keep the architecture perpetually in flight.</p></div>')

    b.append('<div class="phase"><span class="roman">v5·4</span><h3>No corner cuts on failure</h3><p>On any verification failure, the Failure Investigation Protocol (§11h) fires: state audit, assumption audit, literature RAG, board failure review, ledger entry. Tolerance loosening is forbidden. Equation modifications require explicit user approval on a board <code>equation_inadequate</code> verdict. The default hypothesis when theory and experiment disagree is that the experiment is incomplete — not that the theory is wrong.</p></div>')

    b.append('</div>')

    b.append('<h2>The Nobel-prize bar</h2>')
    b.append('<p class="prose">The engine\'s output standard is <b>external academic peer review</b>, not internal board agreement. Every <code>PROVED</code> or <code>GROUNDED</code> coupling must pass an academic readiness checklist before promotion:</p>')
    b.append('<ul>')
    b.append('<li>Quantitative prediction with declared uncertainty</li>')
    b.append('<li>Systematic error analysis</li>')
    b.append('<li>Independent replication pathway with listed equipment and parameter ranges</li>')
    b.append('<li>Priority / novelty search with ≥10 primary-source citations (not just the 3 the RAG finds)</li>')
    b.append('<li>Honest limitations section — longer than the strengths section by default</li>')
    b.append('<li>Multiple-testing correction across the adversarial pre-registration set</li>')
    b.append('<li>Prior-work engagement including adversarial citations</li>')
    b.append('<li>Hall-of-mirrors check — the claim must be re-state-able outside our framework (portable to Mathematica or Modelica)</li>')
    b.append('</ul>')
    b.append('<p>A coupling missing any checklist item stays at <code>EMPIRICAL</code> regardless of board consensus. Internal board agreement is necessary but not sufficient.</p>')

    return _render_page("Methodology", "methodology", "\n".join(b), depth=0)


def build_about_page() -> str:
    b: List[str] = []
    b.append('<div class="page-intro">')
    b.append('<span class="overline">About</span>')
    b.append('<h1>An honest <em>coupling</em> assistant.</h1>')
    b.append('<p class="lead">hequ is an experiment in systematic cross-domain equation discovery. This site is its public surface: a read-only render of every equation, every coupling hypothesis, every AI review board vote, and the append-only ledger that anchors all of it.</p>')
    b.append('</div>')

    b.append('<h2>The framing</h2>')
    b.append('<p class="prose">The sieve is an <b>AI-assisted coupling assistant, not a coupling oracle</b>. Every historical attempt at fully automated discovery of cross-domain scientific relationships has failed or scoped down. hequ generates ranked candidates with explanations; an AI review board of three core members (Claude Opus 4.6, OpenAI GPT-5, Gemini 2.5 Pro) — with Grok-4 as optional fourth seat on high-stakes governance rounds — accepts or rejects each candidate before it enters the ledger as PROVED. This framing is binding — nothing is labeled a "discovery" without a recorded vote, and every round logs whether it seated 3 or 4 reviewers.</p>')
    b.append(f'<p>The full review protocol, from canonical problem unit tests through live sensor grounding to the four-phase academic review board, is documented on the <a href="{_MOUNT}methodology.html">methodology</a> page.</p>')

    b.append('<h2>Provenance</h2>')
    b.append('<ul>')
    b.append('<li>Every equation is parsed from a YAML source with pint-typed variables and an I-ADOPT compositional descriptor (object, property, context, constraint).</li>')
    b.append('<li>Every canonical form is simplified by sympy before matching.</li>')
    b.append('<li>The Layer 5 coupling sieve applies a two-gate prefilter (pint dimensions + explicit domain-adjacency matrix), a six-way bond-graph role classifier, and a structural bijection rescorer.</li>')
    b.append('<li>The physical-constraint filter runs Tellegen pairing, Onsager reciprocity, and SHO-style energy conservation.</li>')
    b.append('<li>The emergent-properties analysis computes symbolic steady states, linear stability, Buckingham Π groups, and conserved quantities.</li>')
    b.append('<li>The AI review board votes independently per model; the ledger records each vote verbatim with verdict, reasoning, and timestamp.</li>')
    b.append('</ul>')

    b.append('<h2>What this site is not</h2>')
    b.append('<ul>')
    b.append('<li>A published scientific paper. Every finding is a candidate pending continued review.</li>')
    b.append('<li>A substitute for domain expertise. The AI review board is a sanity check, not a peer review.</li>')
    b.append('<li>A benchmark against SINDy / AI Feynman / PySR — those tools work within a single domain, not cross-domain.</li>')
    b.append('</ul>')

    return _render_page("About", "about", "\n".join(b), depth=0, narrow=True)


# ---------------------------------------------------------------------------
# Data assembly
# ---------------------------------------------------------------------------


def _assemble_couplings(equations: Dict[str, TypedExpression]) -> List[Dict[str, Any]]:
    report = run_coupling_sieve(equations, emit_tier3=False)
    out: List[Dict[str, Any]] = []
    for h in report.hypotheses:
        verdict = evaluate_physical(h, equations)
        emergent = analyse_emergent(h, equations)
        filter_summary = "pass" if verdict.passed else ("soft" if verdict.all_not_applicable else "fail")
        slug = _coupling_slug(h.eq_a_id, h.eq_b_id, h.var_a, h.var_b, h.tier.value)
        if h.tier == CouplingTier.TIER1_EQUIVALENCE and verdict.passed:
            outcome = "proved"
        elif verdict.passed:
            outcome = "empirical"
        elif verdict.all_not_applicable:
            outcome = "conjectural"
        else:
            outcome = "rejected"
        out.append({
            "slug": slug,
            "tier_label": h.tier.value.replace("_", " ").title(),
            "eq_a": h.eq_a_id, "eq_b": h.eq_b_id,
            "var_a": h.var_a, "var_b": h.var_b,
            "tier": h.tier.value,
            "outcome": outcome,
            "filter_summary": filter_summary,
            "reason": h.reason,
            "descriptor_a": h.descriptor_a.as_dict(),
            "descriptor_b": h.descriptor_b.as_dict(),
            "physical": verdict.as_dict(),
            "emergent": emergent.as_dict(),
            "ai_review": None,
        })
    return out


def _overlay_ai_review(couplings: List[Dict[str, Any]]) -> None:
    if not _LEDGER_PATH.exists():
        return
    ledger = DiscoveryLedger(_LEDGER_PATH)
    by_key: Dict[tuple, Dict[str, Any]] = {}
    for rec in ledger.all():
        if rec.kind != "coupling_reviewed":
            continue
        sub = rec.substitution if isinstance(rec.substitution, dict) else {}
        va = sub.get("v_a", {}).get("variable") if isinstance(sub, dict) else None
        vb = sub.get("v_b", {}).get("variable") if isinstance(sub, dict) else None
        if va is None or vb is None:
            continue
        key = (rec.eq_a, rec.eq_b, va, vb)
        by_key[key] = rec.evidence.get("ai_review")
    for c in couplings:
        key = (c["eq_a"], c["eq_b"], c["var_a"], c["var_b"])
        if key in by_key and by_key[key]:
            c["ai_review"] = by_key[key]


def _ledger_records() -> List[Dict[str, Any]]:
    if not _LEDGER_PATH.exists():
        return []
    ledger = DiscoveryLedger(_LEDGER_PATH)
    out: List[Dict[str, Any]] = []
    for rec in ledger.all():
        out.append({
            "eq_a": rec.eq_a,
            "eq_b": rec.eq_b,
            "kind": rec.kind,
            "outcome": rec.outcome.value,
            "review_required": bool(rec.review_required),
        })
    return out


def _extract_canonicals() -> List[Dict[str, Any]]:
    """Extract canonical_problem_verification records from the
    ledger for display on the overview and canonicals pages.
    """
    if not _LEDGER_PATH.exists():
        return []
    ledger = DiscoveryLedger(_LEDGER_PATH)
    out: List[Dict[str, Any]] = []
    seen = set()
    # Iterate newest-first so later verifications of the same
    # problem override earlier ones
    for rec in reversed(ledger.all()):
        if rec.kind != "canonical_problem_verification":
            continue
        sub = rec.substitution or {}
        problem_id = sub.get("problem_id") if isinstance(sub, dict) else None
        key = (rec.eq_a, problem_id)
        if key in seen:
            continue
        seen.add(key)
        ev = rec.evidence or {}
        out.append({
            "equation_id": rec.eq_a,
            "problem_id": problem_id or "(unknown)",
            "value": ev.get("value"),
            "unit": ev.get("unit", ""),
            "status": ev.get("verification_status", ""),
            "citations": ev.get("citations", []),
            "outcome": rec.outcome.value,
        })
    # Sort by equation id for stable display
    out.sort(key=lambda c: c["equation_id"])
    return out


def _extract_composites() -> List[Dict[str, Any]]:
    """Extract composite_verification records from the ledger
    for display on the overview and composites pages.
    """
    if not _LEDGER_PATH.exists():
        return []
    ledger = DiscoveryLedger(_LEDGER_PATH)
    out: List[Dict[str, Any]] = []
    seen = set()
    for rec in reversed(ledger.all()):
        if rec.kind != "composite_verification":
            continue
        sub = rec.substitution or {}
        composite_id = sub.get("composite_id") if isinstance(sub, dict) else None
        if composite_id in seen:
            continue
        seen.add(composite_id)
        ev = rec.evidence or {}
        verif = ev.get("verification", {}) if isinstance(ev, dict) else {}
        out.append({
            "composite_id": composite_id or "(unknown)",
            "eq_a": rec.eq_a,
            "eq_b": rec.eq_b,
            "tier": sub.get("tier", "") if isinstance(sub, dict) else "",
            "v_a": sub.get("v_a", "") if isinstance(sub, dict) else "",
            "v_b": sub.get("v_b", "") if isinstance(sub, dict) else "",
            "transducer_id": sub.get("transducer_id", "") if isinstance(sub, dict) else "",
            "value": verif.get("value") if isinstance(verif, dict) else None,
            "unit": verif.get("unit", "") if isinstance(verif, dict) else "",
            "status": verif.get("verification_status", "") if isinstance(verif, dict) else "",
            "citations": verif.get("citations", []) if isinstance(verif, dict) else [],
            "outcome": rec.outcome.value,
        })
    out.sort(key=lambda c: c["composite_id"])
    return out


def _ledger_summary(records: List[Dict[str, Any]]) -> Dict[str, int]:
    out: Dict[str, int] = {}
    for r in records:
        out[r["outcome"]] = out.get(r["outcome"], 0) + 1
    return out


# ---------------------------------------------------------------------------
# Orchestrator
# ---------------------------------------------------------------------------


def build_research_page() -> str:
    b: List[str] = []
    b.append('<h1>Research</h1>')
    b.append('<section class="card">')
    b.append('<h2>Photon-pressure-driven seepage in porous media</h2>')
    b.append('<p class="meta">Preprint draft v1 &middot; April 2026 &middot; Matthew Luallen, with AI review board</p>')
    b.append('<p>A novel cross-domain prediction from automated equation coupling. The composite couples Darcy&rsquo;s law for porous-media flow with radiation-pressure momentum deposition from absorbed photon flux.</p>')
    b.append('<h3>The prediction</h3>')
    b.append('<p>In a horizontal porous medium saturated with an absorbing fluid:</p>')
    b.append('<div class="equation">u = k &alpha; I / (&mu; c)</div>')
    b.append('<p>where <em>k</em> is permeability, <em>&alpha;</em> is the absorption coefficient, <em>I</em> is beam intensity, <em>&mu;</em> is dynamic viscosity, and <em>c</em> is the speed of light.</p>')
    b.append('<p>At representative parameters (k = 10<sup>&minus;12</sup> m&sup2;, &alpha; = 10<sup>3</sup> m<sup>&minus;1</sup>, I = 10<sup>9</sup> W/m&sup2;, &mu; = 10<sup>&minus;3</sup> Pa&middot;s): <strong>u &asymp; 3.3 &times; 10<sup>&minus;6</sup> m/s</strong> (~12 mm/hour).</p>')
    b.append('<h3>Why this is novel</h3>')
    b.append('<p>A systematic prior-art search (12 queries across Web, arXiv, and Google Scholar) found <strong>zero direct hits</strong> on this specific coupling. The acoustic analog (acoustic-streaming-driven pore flow) is well-published in J. Fluid Mech. and PMC (2018). The optical-in-bulk-fluid case is published (Leonhardt, Phys. Rev. A 90, 033801, 2014). But the specific gap &mdash; optical/electromagnetic momentum &rarr; pore-fluid flow in porous media &mdash; remains unfilled.</p>')
    b.append('<p>The gap exists because the two parent communities (porous-media hydraulicists and radiation-pressure physicists) do not cite each other&rsquo;s journals. This is <strong>Mechanism A (cross-community isolation)</strong> from the hequ.ai novelty pathway.</p>')
    b.append('<h3>Verification</h3>')
    b.append('<table><thead><tr><th>Check</th><th>Result</th></tr></thead><tbody>')
    b.append('<tr><td>A &mdash; symbolic canonicalization</td><td>rational normalization &rarr; zero</td></tr>')
    b.append('<tr><td>B &mdash; property-based testing</td><td>200 stratified samples, all within 10<sup>&minus;10</sup> tolerance</td></tr>')
    b.append('<tr><td>C &mdash; mpmath 50-digit cross-CAS</td><td>3.33564&times;10<sup>&minus;6</sup>, rel_err = 0</td></tr>')
    b.append('<tr><td>Board formula</td><td>matches local formula exactly</td></tr>')
    b.append('<tr><td>Board citations</td><td>Darcy 1856, Ashkin 1970, Jackson &sect;6.7, Bear Ch 5</td></tr>')
    b.append('</tbody></table>')
    b.append('<h3>Falsification conditions</h3>')
    b.append('<ol>')
    b.append('<li>Steady flux in a horizontal dyed porous sample must scale linearly with beam intensity (u &prop; I) after controlling for thermal buoyancy.</li>')
    b.append('<li>Measured velocity at the stated parameters must be within an order of magnitude of 3.3 &times; 10<sup>&minus;6</sup> m/s.</li>')
    b.append('<li>No prior peer-reviewed publication formalizing this specific coupling exists.</li>')
    b.append('</ol>')
    b.append('<h3>Distinguishing signature</h3>')
    b.append('<p>The prediction is <strong>independent of pore-fluid density &rho;</strong>, unlike gravity-driven Darcy flow where u &prop; &rho;g. Varying fluid density while holding viscosity constant should not change the photon-pressure-driven seepage velocity. This decoupling provides a clean experimental control.</p>')
    b.append('<h3>&ldquo;Board is not a CAS&rdquo; side contribution</h3>')
    b.append('<p>On the Arrhenius+Fick Damk&ouml;hler composite, the AI board&rsquo;s numerical estimate was 7.24 &times; 10<sup>9</sup> while the true value is 725.4 &mdash; a <strong>10<sup>7</sup>-fold error</strong> that the local-CAS protocol caught by design. LLMs provide formulas and citations; SymPy + mpmath provide numbers.</p>')
    b.append('<h3>Provenance</h3>')
    b.append('<ul>')
    b.append('<li>Descriptor schema frozen before proposal (SHA-256: <code>5b1af167...b4cd3633</code>)</li>')
    b.append('<li>Candidate generated by the AI review board (OpenAI GPT-5, Mechanism B) during novelty-generation brief v1</li>')
    b.append('<li>Sympy-verified before composite authored (Rule A9)</li>')
    b.append('<li>Phase 13 verification: all four checks passed</li>')
    b.append(f'<li>Source: <a href="https://github.com/makau-ai/hequ">github.com/makau-ai/hequ</a></li>')
    b.append('</ul>')
    b.append('</section>')

    b.append('<section class="card">')
    b.append('<h2>Verified composite catalog</h2>')
    b.append('<table><thead><tr><th>#</th><th>Composite</th><th>Parents</th><th>Transducer</th><th>Novelty</th></tr></thead><tbody>')
    composites_data = [
        ("1", "Simple harmonic oscillator", "Newton II + Hooke", "identity", "textbook"),
        ("2", "Work = force &times; distance", "Newton II + Work-Energy", "identity", "textbook"),
        ("3", "Soret thermodiffusion", "Fourier + Fick", "Onsager s<sub>T</sub>", "textbook"),
        ("4", "DC motor steady-state", "Newton II + Ohm", "gyrator K", "textbook"),
        ("5", "Damk&ouml;hler regime", "Arrhenius + Fick", "compound Da", "textbook"),
        ("6", "<strong>Photon-pressure seepage</strong>", "<strong>Darcy + RadPress</strong>", "<strong>mobility k/&mu;</strong>", "<strong>NOVEL</strong>"),
    ]
    for n, name, parents, transducer, novelty in composites_data:
        b.append(f'<tr><td>{n}</td><td>{name}</td><td>{parents}</td><td>{transducer}</td><td>{novelty}</td></tr>')
    b.append('</tbody></table>')
    b.append('</section>')

    return _render_page("Research", "research", "\n".join(b), depth=0)


def build_all() -> None:
    print("Loading equations...")
    equations = load_all_equations(_LABS_V2 / "equations")
    print(f"  {len(equations)} equations")

    print("Assembling couplings...")
    couplings = _assemble_couplings(equations)
    _overlay_ai_review(couplings)
    print(f"  {len(couplings)} couplings")

    print("Loading ledger...")
    ledger_records = _ledger_records()
    ledger_summary = _ledger_summary(ledger_records)
    print(f"  {len(ledger_records)} records: {ledger_summary}")

    canonicals = _extract_canonicals()
    composites = _extract_composites()
    print(f"  {len(canonicals)} canonical problems, {len(composites)} composites")

    coupling_stats = {
        "tier1": sum(1 for c in couplings if c["tier"] == "tier1_equivalence"),
        "tier2": sum(1 for c in couplings if c["tier"] == "tier2_similarity"),
        "tier3": sum(1 for c in couplings if c["tier"] == "tier3_conjectural"),
    }
    featured = [c for c in couplings if c["outcome"] == "proved"]

    print(f"Writing to {_OUT_DIR}")
    _OUT_DIR.mkdir(parents=True, exist_ok=True)
    (_OUT_DIR / "_assets").mkdir(exist_ok=True)
    (_OUT_DIR / "equations").mkdir(exist_ok=True)
    (_OUT_DIR / "couplings").mkdir(exist_ok=True)

    (_OUT_DIR / "_assets" / "site.css").write_text(_CSS)
    (_OUT_DIR / "_assets" / "starfield.js").write_text(_STARFIELD_JS)

    (_OUT_DIR / "index.html").write_text(build_overview(
        equations, ledger_summary, coupling_stats, featured,
        canonicals, composites,
    ))
    (_OUT_DIR / "canonicals.html").write_text(build_canonicals_page(canonicals))
    (_OUT_DIR / "composites.html").write_text(build_composites_page(composites))
    (_OUT_DIR / "ledger.html").write_text(build_ledger_page(ledger_records))
    (_OUT_DIR / "methodology.html").write_text(build_methodology_page())
    (_OUT_DIR / "about.html").write_text(build_about_page())

    (_OUT_DIR / "research.html").write_text(build_research_page())

    review_md_path = _LABS_V2 / "cross_analysis" / "AI_REVIEW_SUMMARY.md"
    review_md = review_md_path.read_text() if review_md_path.exists() else None
    (_OUT_DIR / "ai-review.html").write_text(build_ai_review_page(review_md))

    (_OUT_DIR / "equations" / "index.html").write_text(build_equations_index(equations))
    for eq in equations.values():
        (_OUT_DIR / "equations" / f"{eq.id}.html").write_text(build_equation_detail(eq))

    (_OUT_DIR / "couplings" / "index.html").write_text(build_couplings_index(couplings))
    for c in couplings:
        (_OUT_DIR / "couplings" / f"{c['slug']}.html").write_text(build_coupling_detail(c))

    total_pages = 4 + 1 + len(equations) + 1 + len(couplings)
    print(f"Wrote {total_pages} HTML pages to {_OUT_DIR}")


if __name__ == "__main__":
    build_all()
