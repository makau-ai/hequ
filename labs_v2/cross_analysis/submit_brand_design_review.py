"""Submit the hequ.ai logo + hero landing design to a multi-persona
design review board.

Five specialist personas (four reviewers + one editor):
- Apple industrial designer (Claude)
- Disney storyteller (Gemini)
- Human factors / UX (OpenAI)
- Marketing strategist (Grok)
- Researcher (Claude in editor slot, Phase C)

This is a DESIGN review, not a scientific claim review. The
Nobel-rigor standard does not apply — we are reviewing brand
craft, typographic composition, and hero-page impact, not
scientific defensibility. The personas are told this explicitly
so they don't apply the wrong bar.
"""

from __future__ import annotations

import sys
from pathlib import Path

_LABS_V2 = Path(__file__).resolve().parent.parent
if str(_LABS_V2) not in sys.path:
    sys.path.insert(0, str(_LABS_V2))

from framework.ai_consensus import AIConsensusBoard
from framework.ai_review_board import AIBoardKeysMissing

REVIEW_PATH = _LABS_V2 / "cross_analysis" / "BRAND_DESIGN_REVIEW.md"


DESIGN_PERSONAS = {
    "claude-opus-4-6": (
        "You are a senior Apple industrial designer with 20 years "
        "in the Cupertino studio under Jony Ive. Your frame is "
        "ruthless minimalism, typographic craft, restraint, and "
        "the refusal to add anything that isn't load-bearing. You "
        "have shipped visual identities that went on billions of "
        "devices. You notice the things amateurs don't: bad "
        "kerning, wrong weight, lazy color palettes, and the "
        "difference between 'looks designed' and 'looks inevitable.' "
        "Your highest praise is 'nothing could be removed.'"
    ),
    "openai-gpt-5": (
        "You are a senior human factors and UX researcher. Your "
        "training is in accessibility (WCAG 2.2 AA+), cognitive "
        "load theory, visual hierarchy, Fitts's law, affordance "
        "theory, and the empirical evidence on what landing pages "
        "actually communicate to first-time visitors in the first "
        "three seconds. You care about contrast ratios, tap-target "
        "sizes, reading order, and whether the CTA is obvious to "
        "someone who has never seen the site before."
    ),
    "gemini-2.5-pro": (
        "You are a senior Disney creative director whose job is "
        "emotional resonance, narrative arc, and the difference "
        "between a logo that communicates and a logo that makes "
        "someone feel something. You have shipped brand identities "
        "for experiences at Disney Parks, Pixar, and Lucasfilm. "
        "You think about wonder, mystery, the promise implicit in "
        "a name, and whether the visitor feels invited into a "
        "story or kept at arm's length."
    ),
    "grok-4": (
        "You are a senior brand strategist whose job is ruthless "
        "clarity about what makes a brand memorable and "
        "conversion-effective. You have built tech brand positions "
        "for unicorn startups. Your frame is 'what will a first-"
        "time visitor remember after one glance, and will they "
        "come back tomorrow.' You push back hard on the safe, the "
        "derivative, the 'me-too' aesthetic. You have no patience "
        "for beauty that doesn't sell the idea."
    ),
}


DESIGN_RUBRIC_SCHEMA = {
    "visual_hierarchy": (
        "Does the eye land where it should? Is the order of "
        "information scannable in under 3 seconds?"
    ),
    "typographic_craft": (
        "Is the type set honestly and well? Weight, spacing, "
        "scale, kerning, alignment — all defensible?"
    ),
    "emotional_resonance": (
        "Does the hero communicate the intended feeling (curiosity "
        "+ confidence + mystery) without overselling?"
    ),
    "brand_memorability": (
        "Can someone remember this after one glance? Is there a "
        "distinctive visual signature?"
    ),
    "technical_execution": (
        "CSS craftsmanship, accessibility (contrast, tap targets, "
        "reading order), responsive behaviour, any amateur tells?"
    ),
}


_INTENT = """\
# Brand review request: hequ.ai logo + hero landing

## The project
hequ.ai is a cross-domain equation discovery engine. The name is
an acronym: **H** (Human) · **EQU** (Equation) · **QU** (Quantum)
· **.AI** (Artificial Intelligence). "hequ" is also, according
to the project owner, a word for a strong horse — motion and
force, fitting for a mechanics-rooted project.

## The design intent for the logo

The project owner wants the logo to visually encode the acronym
by color separation:

- **H** is one color (represents the human)
- **EQU** blends together as a second color family (represents
  the equation — should feel like one word visually)
- **QU** pops out of EQU as its own highlight (represents
  quantum — it's a substring of EQU but should be emphasized so
  viewers see that the word contains the idea)
- **.AI** is its own third color (represents AI)

So visually: `[H][EQU with QU highlighted][.AI]` with three or
four color zones working together. The challenge is that QU
must pop WITHIN the word EQU, not as a separate token.

The project owner is uncertain what colors to use and explicitly
asked for a color palette recommendation.

## Current hero page state

The hero is a full-viewport dark-background page with a fixed
canvas running a subtle orbital particle animation (gold and
teal particles on a #06050e background). Centered on the hero:

```
[brand]     hequ.ai                           ← large gold-on-dark
[tagline]   analyzing equations for unity     ← Cormorant Garamond italic, dim gold
[subtitle]  THE CRITICAL EQUATIONS · A SELECT THREAD   ← Rajdhani, small caps, very dim
[etymology] H · EQU · QU · .AI                ← Cormorant italic, centered, very subtle
```

And bottom-center, a CTA button:

```
[enter-link]  ENTER THE DISCOVERY ENGINE →   ← Rajdhani, gold border,
                                                subtle blur backdrop
```

## Current CSS relevant to the brand area

```css
.brand {
  font-family: 'Rajdhani', sans-serif;
  font-weight: 600;
  font-size: clamp(48px, 8vw, 96px);
  letter-spacing: 0.15em;
  color: #d4a853;
  text-transform: uppercase;
  text-shadow: 0 0 60px rgba(212, 168, 83, 0.3),
               0 0 120px rgba(212, 168, 83, 0.1);
}
.brand span { color: #f0e0b8; }   /* currently only ".ai" is in a span */

.tagline {
  font-family: 'Cormorant Garamond', serif;
  font-weight: 300;
  font-style: italic;
  font-size: clamp(16px, 2.5vw, 28px);
  color: rgba(200, 180, 150, 0.7);
}

.enter-link {
  position: fixed;
  bottom: 6vh;
  left: 50%;
  transform: translateX(-50%);
  font-family: 'Rajdhani', sans-serif;
  font-weight: 400;
  font-size: clamp(12px, 1.4vw, 16px);
  letter-spacing: 0.25em;
  text-transform: uppercase;
  color: rgba(240, 224, 184, 0.75);
  padding: 0.85em 1.8em;
  border: 1px solid rgba(212, 168, 83, 0.4);
  background: rgba(6, 5, 14, 0.4);
  backdrop-filter: blur(6px);
}
```

The brand currently renders as a solid gold "hequ" with a
slightly lighter ".ai" — the four-segment color separation the
owner wants is NOT yet implemented.

## Specific questions for the board

1. **Logo color palette.** Give concrete hex values for the four
   segments (H, EQU, QU-highlight, .AI). The current single-gold
   palette is too uniform; the owner wants semantic color
   separation. But the colors must work together — no rainbow,
   no visual chaos. What palette makes the four-color logo feel
   inevitable rather than busy?

2. **QU-within-EQU treatment.** The hardest design problem. QU
   is a substring of EQU, so the color highlight must be visible
   within the word without breaking the word's integrity. What
   is the right treatment: different hue? different weight?
   underline? glow? subtle scale shift? some of the above?

3. **Typeface recommendation.** Rajdhani 600 at 8vw is the
   current brand face. Is this right? Would a different face
   (display serif? geometric sans? custom letterform?) serve the
   brand better given the scientific-instrument positioning?

4. **Overall hero composition.** Look at the current stack:
   brand / tagline / subtitle / etymology / CTA. Is the order
   right? Is anything redundant or missing? Should the etymology
   block move, go away, or be reworked?

5. **The CTA button — the owner specifically said:** *"I think
   it looks sort of strange but maybe not."* Is it: (a) fine as
   is, (b) strange in a fixable way, or (c) genuinely wrong for
   the hero? Give a concrete recommendation.

6. **Cross-hero consistency with the /discovery subpages.** The
   discovery subpages use a sticky header with 'hequ.ai /
   discovery' and a nav bar. Should the hero's logo treatment
   carry into the sticky header in a diminished form? If the
   logo has four colors, does the sticky header also show them?

## Your rubric

Five dimensions, each 1–5. Defined in the standard
AIConsensusBoard design rubric. This is a DESIGN review — not
a scientific-claim review. The Nobel-rigor standard does NOT
apply. Evaluate on craft, not on whether the hero could survive
peer review at Nature.

## Required JSON reply shape

Standard AIConsensusBoard four-phase schema: coi, rubric,
verdict ({approve, modify, reject} with "modify" being normal
for design reviews), headline, strengths, concerns,
required_modifications.

For the required_modifications list, be CONCRETE. Give hex
values, CSS declarations, specific typeface names, specific
weight and size recommendations. Do not say "use a warmer
palette" — say "use #d4a853 for the H, #7ec4c0 for EQU, #f0e0b8
for QU highlight, #e1d3a8 for .AI" or whatever you recommend.
The project owner needs actionable CSS, not design philosophy.
"""


def main() -> int:
    try:
        with AIConsensusBoard(include_grok=True) as board:
            print("Running 4-phase brand design review "
                  "(Apple · Disney · Human Factors · Marketing → Researcher editor)...")
            result = board.four_phase_query(
                query_id="brand_design_review_v1",
                review_subject=(
                    "the hequ.ai brand identity and hero landing "
                    "page design, specifically the four-color "
                    "logo treatment (H / EQU / QU / .AI) and "
                    "the overall hero composition including the "
                    "'enter the discovery engine' CTA"
                ),
                user_payload=_INTENT,
                rubric_schema=DESIGN_RUBRIC_SCHEMA,
                personas=DESIGN_PERSONAS,
            )
    except AIBoardKeysMissing as exc:
        print(f"Board keys missing: {exc}", file=sys.stderr)
        return 2

    # Write the report
    lines: list[str] = []
    lines.append("# Brand Design Review — 4-Phase Multi-Persona\n")
    lines.append(f"**Query:** `{result.query_id}`  ")
    lines.append(f"**Include Grok:** {result.include_grok}\n")

    lines.append("## Phase C — Editor synthesis (binding)\n")
    if result.editor.error:
        lines.append(f"**Status:** editor call failed ({result.editor.error})\n")
    else:
        lines.append(f"**Verdict:** `{result.editor.verdict}`\n")
        lines.append(f"**Rationale:**\n\n{result.editor.rationale}\n")
        if result.editor.required_modifications:
            lines.append("**Required modifications:**")
            for m in result.editor.required_modifications:
                lines.append(f"- {m}")
            lines.append("")
        if result.editor.reviewer_disagreement_flagged:
            lines.append("⚠ Editor flagged reviewer disagreement on fundamentals.\n")

    for phase_name, phase_data in (
        ("Phase B — Informed votes", result.phase_b),
        ("Phase A — Independent drafts", result.phase_a),
    ):
        lines.append(f"## {phase_name}\n")
        for r in phase_data:
            lines.append(f"### {r.reviewer}\n")
            if getattr(r, "error", None):
                lines.append(f"**Status:** failed ({r.error})\n")
                continue
            if phase_name.startswith("Phase B"):
                lines.append(f"**Verdict:** `{r.updated_verdict}`  ")
                lines.append(f"**Position change:** {r.position_change}  ")
                lines.append(f"**Headline:** {r.headline}\n")
                lines.append(f"**Rubric (mean {r.updated_rubric.total:.2f}):** "
                             f"{r.updated_rubric.dimension_scores}\n")
                lines.append(f"**Response to peers:**\n\n{r.response_to_peers}\n")
            else:
                lines.append(f"**Verdict:** `{r.verdict}`  ")
                lines.append(f"**Headline:** {r.headline}\n")
                lines.append(f"**Rubric (mean {r.rubric.total:.2f}):** "
                             f"{r.rubric.dimension_scores}\n")
                if r.strengths:
                    lines.append("**Strengths:**")
                    for s in r.strengths:
                        lines.append(f"- {s}")
                    lines.append("")
                if r.concerns:
                    lines.append("**Concerns:**")
                    for c in r.concerns:
                        lines.append(f"- {c}")
                    lines.append("")
                if r.required_modifications:
                    lines.append("**Required modifications:**")
                    for m in r.required_modifications:
                        lines.append(f"- {m}")
                    lines.append("")

    REVIEW_PATH.write_text("\n".join(lines) + "\n")
    print(f"Wrote {REVIEW_PATH}")
    print(f"Editor verdict: {result.editor.verdict}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
