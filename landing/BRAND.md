# hequ.ai Brand System

Derived from the five-SME review board (semiotician, physicist, cross-cultural reader, contrarian critic, multi-touchpoint strategist) and the earlier four-SME depth-and-color board. This document is the canonical reference for which mark to use where.

## Three-tier mark hierarchy

### Tier 1 — Hero Signature
The full animated wordmark on `#06050e` with the cosmic starfield canvas behind.

**Conditions for use:**
- Dark background only
- Width ≥ 480 px
- Screen / video only (requires CSS + canvas runtime)

**Live at:** `landing/public/index.html`

**Use for:** website hero, keynote title slide, video intro, trade-show LED wall.

### Tier 2 — Standard Identity
Five-color static wordmark with the lemniscate-orb entanglement pair replacing the animated thread. Motion cannot reach here, so the static lemniscate carries the coupling-pair meaning.

**Asset:** [marks/hequ-wordmark-static.svg](public/marks/hequ-wordmark-static.svg)

**Conditions for use:**
- Dark or light ground (invert contact treatment if light)
- Width ≥ 120 px
- Full-color reproduction

**Use for:** laptop stickers, field-notebook covers, email signature banners, PDF deck footers, coffee-cup wraps, conference lanyards.

### Tier 3 — Reduced / Monochrome
Single-color wordmark in Sky Cyan (the semantic anchor hue — the EQU spine) with only the EQU underline surviving. All atmosphere (halos, gradients, orbs, thread, contact shadow) dropped.

**Asset:** [marks/hequ-wordmark-mono.svg](public/marks/hequ-wordmark-mono.svg)

**Conditions for use:**
- Any substrate
- Any scale down to ~60 px wide
- Swap `color` attribute to re-ink (100% black on cream, 100% white on dark, 100% Sky Cyan on near-black — the default)

**Use for:** embossed stationery, screen-printed tees (pocket or chest), PCB silkscreen, one-color press ads, newsprint, fax.

### Tier 4 — Favicon / Avatar Monogram
The Q-orb-in-Q-counter monogram. The most distinctive letter of "hequ" — Q — used alone, with a vesper unity orb nested in its counter. At 16×16 the full wordmark is unreadable; this glyph is the compressed essence.

**Asset:** [marks/hequ-favicon-mono.svg](public/marks/hequ-favicon-mono.svg)

**Conditions for use:**
- Any square context from 16×16 up
- Dark ground recommended
- Social avatar, browser tab favicon, app icon placeholder, iOS tab bar

## The atom

[marks/hequ-entangled-pair.svg](public/marks/hequ-entangled-pair.svg) — the Q-U lemniscate-orb assembly as a portable SVG glyph. Every other tier derives from or incorporates this geometry. If the hero composition is ever refreshed, this atom is what the new hero must still be about.

## Palette (synthesis — five SMEs approved, accessibility-mandated Sky Cyan)

| Role | Hex | Name | Notes |
|---|---|---|---|
| Human | `#E8875A` | Ember | Warm terracotta-coral. Hearth color. At favicon scale consider nudging to `#EA7A44` for saturation. |
| Equation | `#4FC3F7` | Sky Cyan | CVD-safe (replaced former teal which collided with Q under deuteranopia). Brand anchor; monochrome default. |
| Quantum | `#9BF7C4` | Firefly | Bioluminescent mint. Board noted aging risk — reconsider in 2028 if "mint-on-black" reads dated. |
| Unity | `#D8B3F0` | Vesper | Twilight lilac. Heart color. **Cross-cultural risk:** mourning adjacency in Brazil, Thailand, Italy — never let "Unity" stand alone in global taglines; keep the four-word context visible. |
| Artificial Intelligence | `#FFE9B3` | First Light | Warm dawn gold. |

Background: `#06050e` (hero default). Non-acronym text in the etymology tooltip: `rgba(255,255,255,0.78)` — muted white for contrast.

## The physics (physicist SME override — shipped)

The original animated "traveling peak" along the entanglement thread was flagged as physicist-embarrassing — it read as signal propagation, which violates the no-communication theorem's mental model. **Fixed:** the thread is now static (shared state, not a channel), and the orbs carry *joint stochastic flicker* — both flashing simultaneously to a correlated hue drawn from a shared distribution. Correlation without transport.

Do not reintroduce a traveling packet between the orbs. If future motion is added, it must represent *correlated measurement outcomes*, not energy in transit.

## Cross-cultural notes

**"hequ" etymology.** The tooltip now surfaces `河曲` (Hequ, bend of the Yellow River — also a steppe horse breed and a Mongolian constellation). This is the brand's most distinctive provenance story and activates a latent asset for Mandarin-reading markets. Keep it visible on Chinese-facing surfaces.

**Unity caveats.** "Unity" reads politically in post-colonial Africa (Harambee, Ujamaa), pan-Arab (Ba'athist), Korean (reunification with DPRK). Always accompany with the four-word acronym context. Never use "Unity" alone in a tagline.

**Dark-mode dependency.** Hero is dark-mode only. Institutional / EDU markets (India, MENA especially) default to white backgrounds for credibility. Tier 2 and Tier 3 exist for those contexts; do not force dark mode on print collateral.

**Yin-yang treatment.** The Q/U crescents are an abstract taijitu quotation — respectful if kept abstract (the mint/lilac palette is already far enough from taijitu's canonical black/white). Do not let a future designer add a dot-of-opposite-color inside each orb; that crosses into literal appropriation.

## Accessibility guarantees

- WCAG 2.1 AA contrast on `#06050e` for all five palette colors.
- No CVD hue-collapse under deuteranopia, protanopia, or tritanopia.
- `prefers-reduced-motion` freezes all animations (orbs still glow statically).
- `prefers-contrast: more` thickens the EQU underline and strips glows.
- Tooltip fully keyboard-focusable (`tabindex="0"` + focus-within reveal).

## Aging strategy

The hero composition is a deliberate 2025 artifact — background-clip:text gradients, animated starfield, bioluminescent mint on near-black are all aesthetics of this moment. That was accepted with eyes open.

The Tier 2–4 assets above are designed to *survive the hero being swapped*. If the hero aesthetic is refreshed in 2028, the wordmark-static, wordmark-mono, entangled-pair, and favicon-mono SVGs remain — the semantic spine (EQU underline, Q-U coupled pair, five-color semantic encoding) does not date.

## One-week next steps (in priority order)

1. Replace `favicon.svg` with `marks/hequ-favicon-mono.svg` once visually approved.
2. Use Tier 2 `hequ-wordmark-static.svg` in the next pitch deck and email signature banner.
3. Test Tier 3 `hequ-wordmark-mono.svg` in a print preview (business-card size).
4. Validate 河曲 tooltip rendering on Windows Chrome (font-stack fallback).
