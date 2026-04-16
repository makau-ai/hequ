"""Phase 9 — multi-model AI review board.

Implements the voting protocol from
`labs_v2/DESIGN-COUPLING-SIEVE.md` §12. Three reviewers vote on
each coupling hypothesis; a unanimous APPROVE promotes to PROVED,
any REJECT demotes, the mixed case maps to EMPIRICAL.

Design contracts
----------------
- **No persisted keys.** API keys are fetched at runtime from
  Google Secret Manager on the `hequ-ai` project and held in
  memory for the duration of a single review session. After
  `ReviewBoard.__exit__` returns, the cached keys are cleared.
  Callers that hold the object must treat it as process-scoped
  and never pickle or serialize it.

- **Stdlib-only HTTP.** We deliberately avoid the anthropic,
  openai, and google-genai SDKs so the module has zero pip
  dependencies. Each adapter is a ~30-line stdlib `urllib`
  wrapper around the vendor's REST API. When the SDKs change or
  drop support for old versions, the adapters keep working
  because they pin the HTTP contract.

- **Structured verdicts.** Every model returns a
  `ReviewVerdict` enum in {APPROVE, REJECT, NEEDS_MORE_INFO}
  plus a one-paragraph reason. The board aggregates them per
  §12.2's voting rules. No free-text interpretation — if a
  model's reply can't be parsed into one of the three verdicts,
  we record it as ERROR and treat it as NEEDS_MORE_INFO for
  voting purposes.

- **Audit trail in the ledger.** Every vote (APPROVE, REJECT,
  NEEDS_MORE_INFO, ERROR) is recorded in the ledger v4 entry's
  `evidence.ai_review` list. Nothing is discarded. A future
  audit can re-derive why a coupling landed where it did.

Secret layout
-------------
All three keys live in the `hequ-ai` project's Secret Manager
under canonical names:

    anthropic-api-key
    openai-api-key
    gemini-api-key

Fetched via `gcloud secrets versions access latest --secret=<name>
--project=hequ-ai`. If the CLI is missing, or any key isn't
readable, `AIBoardKeysMissing` is raised with the specific
diagnostic. The caller (Phase 10 runner) should catch this and
leave affected couplings at CONJECTURAL with `review_required=True`.
"""

from __future__ import annotations

import json
import os
import re
import subprocess
import urllib.error
import urllib.request
from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import Any, Dict, List, Optional, Sequence

from .couplings import CouplingHypothesis, CouplingTier


# ---------------------------------------------------------------------------
# Exception types
# ---------------------------------------------------------------------------


class AIBoardKeysMissing(RuntimeError):
    """Raised when one or more API keys cannot be fetched from
    Google Secret Manager. The caller is expected to catch this
    and downgrade affected coupling hypotheses accordingly.
    """


class AIBoardAPIError(RuntimeError):
    """Raised when a vendor API returns an HTTP error or a
    response that can't be parsed. Wraps the original exception
    in the `.cause` attribute for post-mortem debugging.
    """


# ---------------------------------------------------------------------------
# Verdict types
# ---------------------------------------------------------------------------


class ReviewVerdict(Enum):
    APPROVE = "approve"
    REJECT = "reject"
    NEEDS_MORE_INFO = "needs_more_info"
    ERROR = "error"   # vendor error or unparseable reply


@dataclass
class ReviewVote:
    """One reviewer's verdict on a single coupling hypothesis."""
    reviewer: str           # "claude-opus", "openai-gpt5", "gemini-25-pro"
    verdict: ReviewVerdict
    reason: str
    raw_response: str       # verbatim vendor response, for audit
    timestamp: str          # ISO8601 UTC

    def as_dict(self) -> Dict[str, Any]:
        return {
            "reviewer": self.reviewer,
            "verdict": self.verdict.value,
            "reason": self.reason,
            "timestamp": self.timestamp,
            # raw_response is intentionally omitted from the dict
            # by default — it can be bulky. Callers that want it
            # can read it off the dataclass directly.
        }


@dataclass
class BoardDecision:
    """The aggregated verdict of the whole board on one coupling.

    `outcome_hint` is the enum that the ledger-writer should use
    when deciding whether to promote/demote the hypothesis.
    Unanimous-APPROVE → PROMOTE, any-REJECT → DEMOTE,
    2-APPROVE-1-NEEDS_MORE_INFO → HOLD_EMPIRICAL, everything else
    → HOLD_CONJECTURAL.
    """
    votes: List[ReviewVote]
    outcome_hint: str       # "PROMOTE", "HOLD_EMPIRICAL", "HOLD_CONJECTURAL", "DEMOTE"
    rationale: str

    def as_dict(self) -> Dict[str, Any]:
        return {
            "votes": [v.as_dict() for v in self.votes],
            "outcome_hint": self.outcome_hint,
            "rationale": self.rationale,
        }


# ---------------------------------------------------------------------------
# Secret fetcher
# ---------------------------------------------------------------------------


SECRET_NAMES = {
    "anthropic": "anthropic-api-key",
    "openai": "openai-api-key",
    "gemini": "gemini-api-key",
}
SECRET_PROJECT = "hequ-ai"

# Grok (xAI) is optional — only fetched when `include_grok=True`
# is passed on query construction. Kept out of the default
# `ReviewBoardKeys.load()` path so a missing Grok key doesn't
# break 3-model runs.
OPTIONAL_SECRET_NAMES = {
    "grok": "grok-api-key",
}


def _fetch_secret(secret_name: str) -> str:
    """Fetch a secret's latest version from Google Secret Manager
    via the `gcloud` CLI. Returns the decoded string (whitespace
    trimmed). Raises `AIBoardKeysMissing` on any failure.

    We shell out to gcloud rather than using the
    google-cloud-secret-manager SDK because:
    - zero pip dependency
    - honours the user's existing gcloud auth (ADC or CLI)
    - identical behaviour across macOS / Linux / container
    """
    try:
        out = subprocess.run(
            [
                "gcloud", "secrets", "versions", "access", "latest",
                f"--secret={secret_name}",
                f"--project={SECRET_PROJECT}",
            ],
            capture_output=True,
            check=True,
            timeout=15,
        )
    except FileNotFoundError as exc:
        raise AIBoardKeysMissing(
            "gcloud CLI not found; cannot fetch AI-review-board keys. "
            "Install gcloud or set env vars manually."
        ) from exc
    except subprocess.CalledProcessError as exc:
        stderr = exc.stderr.decode("utf-8", errors="replace").strip()
        raise AIBoardKeysMissing(
            f"gcloud failed fetching {secret_name}: {stderr}"
        ) from exc
    except subprocess.TimeoutExpired as exc:
        raise AIBoardKeysMissing(
            f"gcloud timed out fetching {secret_name}"
        ) from exc
    return out.stdout.decode("utf-8").strip()


@dataclass
class ReviewBoardKeys:
    """Short-lived bundle of API keys. Instances should not be
    serialized, logged, or pickled — they are meant to live only
    within a `with ReviewBoard(...) as board:` block.

    `grok` is optional. If None, Grok is not available for this
    session and any query that requests it will skip the Grok
    reviewer. If not None, Grok can be included as a 4th reviewer.
    """
    anthropic: str
    openai: str
    gemini: str
    grok: Optional[str] = None

    @classmethod
    def load(cls, include_optional: tuple = ()) -> "ReviewBoardKeys":
        """Fetch the three mandatory keys and optionally any
        named optional keys (e.g. `include_optional=("grok",)`).

        A missing OPTIONAL key is logged and the field is set to
        None, not raised. A missing MANDATORY key raises
        `AIBoardKeysMissing`.
        """
        missing = []
        values: Dict[str, Any] = {}
        for vendor, secret in SECRET_NAMES.items():
            try:
                values[vendor] = _fetch_secret(secret)
            except AIBoardKeysMissing as exc:
                missing.append(f"{vendor} ({secret}): {exc}")
        if missing:
            raise AIBoardKeysMissing(
                "Could not fetch one or more AI-review-board keys: "
                + "; ".join(missing)
            )
        for vendor in include_optional:
            secret = OPTIONAL_SECRET_NAMES.get(vendor)
            if not secret:
                continue
            try:
                values[vendor] = _fetch_secret(secret)
            except AIBoardKeysMissing:
                values[vendor] = None
        return cls(**values)


# ---------------------------------------------------------------------------
# Prompt construction
# ---------------------------------------------------------------------------


_REVIEW_SYSTEM_INSTRUCTIONS = """\
You are a senior scientific reviewer participating in a three-
model review board evaluating a proposed cross-domain coupling
between two equations in the hequ corpus. Your job is to decide
whether this coupling should enter the project's discovery
ledger.

Reply ONLY with a JSON object of the form:

    {"verdict": "approve"|"reject"|"needs_more_info",
     "reason": "<one concise paragraph>"}

No markdown, no preamble, no trailing text. Only the JSON.

The verdict should be based on:
- whether the coupling is physically plausible
- whether the semantic descriptors honestly identify the same
  quantity (or a related quantity via a named transform)
- whether the physical-constraint filter's verdict is consistent
  with your understanding of the two equations
- whether the claimed emergent properties are genuine or
  artefacts of algebraic manipulation"""


def _build_review_prompt(
    hypothesis: CouplingHypothesis,
    physical_verdict_dict: Optional[Dict[str, Any]],
    emergent_dict: Optional[Dict[str, Any]],
) -> str:
    """Serialize the coupling and its context into a compact
    user-message body. Kept under ~1500 tokens so the call is
    cheap and fast.
    """
    body = {
        "coupling_tier": hypothesis.tier.value,
        "equation_a": hypothesis.eq_a_id,
        "equation_b": hypothesis.eq_b_id,
        "variable_a": hypothesis.var_a,
        "variable_b": hypothesis.var_b,
        "descriptor_a": hypothesis.descriptor_a.as_dict(),
        "descriptor_b": hypothesis.descriptor_b.as_dict(),
        "transfer_function": hypothesis.transfer_function,
        "sieve_reason": hypothesis.reason,
        "physical_constraint_filter": physical_verdict_dict,
        "emergent_properties": emergent_dict,
    }
    return (
        "Review the following proposed cross-domain coupling and "
        "return your verdict as specified:\n\n"
        + json.dumps(body, indent=2, default=str)
    )


def _parse_verdict(raw: str) -> tuple[ReviewVerdict, str]:
    """Extract (verdict, reason) from a vendor reply.

    Accepts either a pure JSON object or a JSON object embedded
    in surrounding text. Returns (ERROR, raw_text) on any
    parsing failure.
    """
    text = raw.strip()
    # Tolerate markdown code fences.
    text = re.sub(r"^```(?:json)?\s*", "", text)
    text = re.sub(r"\s*```$", "", text)
    # Try direct parse first.
    try:
        obj = json.loads(text)
    except json.JSONDecodeError:
        # Fall back to finding the first {...} block.
        match = re.search(r"\{[\s\S]*\}", text)
        if not match:
            return ReviewVerdict.ERROR, raw[:500]
        try:
            obj = json.loads(match.group(0))
        except json.JSONDecodeError:
            return ReviewVerdict.ERROR, raw[:500]
    if not isinstance(obj, dict):
        return ReviewVerdict.ERROR, raw[:500]
    verdict_raw = str(obj.get("verdict", "")).lower().strip()
    reason = str(obj.get("reason", "")).strip()
    for v in (ReviewVerdict.APPROVE, ReviewVerdict.REJECT, ReviewVerdict.NEEDS_MORE_INFO):
        if verdict_raw == v.value:
            return v, reason or "(no reason provided)"
    return ReviewVerdict.ERROR, raw[:500]


# ---------------------------------------------------------------------------
# Vendor adapters (stdlib HTTP)
# ---------------------------------------------------------------------------


_KEY_QUERY_PATTERN = re.compile(r"([?&]key=)[^&\s\"'}]+")


def _redact_key(s: str) -> str:
    """Strip `?key=<secret>` or `&key=<secret>` query params from
    any string before it goes into an error / log / ledger field.

    Vendor error payloads (notably Gemini's) echo back the full
    request URL including the API key. The initial Phase 11 run
    captured that into the ledger before this safeguard existed.
    Every outbound string that could carry a URL now passes
    through this function so a bad vendor response cannot
    exfiltrate the key into our artifacts.
    """
    return _KEY_QUERY_PATTERN.sub(r"\1REDACTED", s)


def _http_post_json(url: str, headers: Dict[str, str], body: Dict[str, Any]) -> Dict[str, Any]:
    """POST a JSON body and return the parsed JSON response.

    **Retry policy (v4, user-directed — non-response counts as
    dissent so we must try HARD before giving up).** The call
    retries up to 5 times with exponential backoff on:
      - HTTPError 5xx (server-side transient, includes 503)
      - URLError (transient network failures)
      - socket.timeout / TimeoutError (read timeouts)
      - JSONDecodeError on the response body (server sent bad JSON)

    Retries are NOT attempted on HTTPError 4xx (client error —
    the request is wrong and retrying won't fix it) or on
    AIBoardKeysMissing (auth failure).

    Backoff schedule: 2, 4, 8, 16, 32 seconds (total wait up
    to ~62s). After the 5th retry, the original exception is
    re-raised as `AIBoardAPIError`. The caller treats this as
    dissent per the v4 'all must respond' rule.

    All string error payloads pass through `_redact_key` before
    being embedded in the raised exception's message.
    """
    import socket as _socket
    import time as _time
    data = json.dumps(body).encode("utf-8")
    safe_url = _redact_key(url)

    last_exception: Optional[Exception] = None
    max_attempts = 5
    for attempt in range(max_attempts):
        req = urllib.request.Request(url, data=data, headers=headers, method="POST")
        try:
            with urllib.request.urlopen(req, timeout=150) as resp:
                payload = resp.read().decode("utf-8")
            try:
                return json.loads(payload)
            except json.JSONDecodeError as exc:
                last_exception = AIBoardAPIError(
                    f"unparseable JSON from {safe_url} "
                    f"(attempt {attempt + 1}/{max_attempts}): "
                    f"{_redact_key(payload)[:500]}"
                )
                # Retry on parse failures — sometimes a transient
                # proxy hiccup truncates the body
        except urllib.error.HTTPError as exc:
            try:
                err_body = exc.read().decode("utf-8", errors="replace")
            except Exception:
                err_body = "(unreadable)"
            safe_body = _redact_key(err_body)
            # 4xx = client error, don't retry (our request is bad)
            if 400 <= exc.code < 500:
                raise AIBoardAPIError(
                    f"HTTP {exc.code} from {safe_url}: {safe_body[:500]}"
                ) from exc
            # 5xx = server transient, retry with backoff
            last_exception = AIBoardAPIError(
                f"HTTP {exc.code} from {safe_url} "
                f"(attempt {attempt + 1}/{max_attempts}): "
                f"{safe_body[:500]}"
            )
        except (urllib.error.URLError, _socket.timeout, TimeoutError) as exc:
            last_exception = AIBoardAPIError(
                f"timeout/network error on {safe_url} "
                f"(attempt {attempt + 1}/{max_attempts}): "
                f"{_redact_key(str(exc))}"
            )

        # Exponential backoff before next attempt
        if attempt < max_attempts - 1:
            backoff_seconds = 2 ** (attempt + 1)
            _time.sleep(backoff_seconds)

    # All retries exhausted
    if last_exception:
        raise last_exception
    # Shouldn't reach here, but satisfy the type checker
    raise AIBoardAPIError(
        f"all {max_attempts} retries exhausted on {safe_url} "
        f"with no specific exception captured"
    )


def _call_claude(api_key: str, user_msg: str,
                 system_override: Optional[str] = None) -> str:
    """Call Claude Opus via the Anthropic messages API and return
    the assistant's text reply.

    `system_override` replaces the default coupling-review system
    instructions for this one call. Used by `ai_consensus.py`
    for non-coupling queries (architecture review, reference
    value sourcing, transducer library authoring, etc.).
    """
    body = {
        "model": "claude-opus-4-6",
        "max_tokens": 8192,
        "system": system_override if system_override is not None else _REVIEW_SYSTEM_INSTRUCTIONS,
        "messages": [{"role": "user", "content": user_msg}],
    }
    headers = {
        "x-api-key": api_key,
        "anthropic-version": "2023-06-01",
        "content-type": "application/json",
    }
    resp = _http_post_json("https://api.anthropic.com/v1/messages", headers, body)
    content = resp.get("content") or []
    for block in content:
        if block.get("type") == "text":
            return block.get("text", "")
    return json.dumps(resp)


def _call_openai(api_key: str, user_msg: str,
                 system_override: Optional[str] = None) -> str:
    """Call OpenAI (gpt-5 / o3 family) via chat completions and
    return the assistant's text reply.
    """
    body = {
        "model": "gpt-5",
        "messages": [
            {"role": "system", "content":
             system_override if system_override is not None else _REVIEW_SYSTEM_INSTRUCTIONS},
            {"role": "user", "content": user_msg},
        ],
    }
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
    }
    resp = _http_post_json(
        "https://api.openai.com/v1/chat/completions", headers, body
    )
    choices = resp.get("choices") or []
    if not choices:
        return json.dumps(resp)
    return choices[0].get("message", {}).get("content", "")


def _call_grok(api_key: str, user_msg: str,
               system_override: Optional[str] = None) -> str:
    """Call xAI Grok via the OpenAI-compatible chat completions
    API. xAI ships a drop-in-OpenAI interface at
    https://api.x.ai/v1/chat/completions, which lets us reuse the
    same adapter shape as `_call_openai`.

    Grok is an OPTIONAL fourth reviewer; this function is only
    called when `four_phase_query(include_grok=True)` is used.
    """
    body = {
        "model": "grok-4-latest",
        "messages": [
            {"role": "system", "content":
             system_override if system_override is not None else _REVIEW_SYSTEM_INSTRUCTIONS},
            {"role": "user", "content": user_msg},
        ],
    }
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
    }
    resp = _http_post_json(
        "https://api.x.ai/v1/chat/completions", headers, body
    )
    choices = resp.get("choices") or []
    if not choices:
        return json.dumps(resp)
    return choices[0].get("message", {}).get("content", "")


def _call_gemini(api_key: str, user_msg: str,
                 system_override: Optional[str] = None) -> str:
    """Call Gemini 2.5 Pro via the Generative Language API and
    return the first candidate's text.
    """
    body = {
        "systemInstruction": {
            "parts": [{"text":
             system_override if system_override is not None else _REVIEW_SYSTEM_INSTRUCTIONS}]
        },
        "contents": [{
            "role": "user",
            "parts": [{"text": user_msg}],
        }],
    }
    headers = {"Content-Type": "application/json"}
    url = (
        "https://generativelanguage.googleapis.com/v1beta/"
        f"models/gemini-2.5-pro:generateContent?key={api_key}"
    )
    resp = _http_post_json(url, headers, body)
    candidates = resp.get("candidates") or []
    if not candidates:
        return json.dumps(resp)
    parts = candidates[0].get("content", {}).get("parts", [])
    return "".join(p.get("text", "") for p in parts)


# ---------------------------------------------------------------------------
# ReviewBoard — the high-level entry point
# ---------------------------------------------------------------------------


def _aggregate(votes: Sequence[ReviewVote]) -> BoardDecision:
    """Apply the design doc §12.2 voting rules.

    Unanimous APPROVE             → PROMOTE
    2 APPROVE + 1 NEEDS_MORE_INFO → HOLD_EMPIRICAL
    Any REJECT                    → DEMOTE  (strongest signal wins)
    2+ REJECT                     → DEMOTE  (same outcome, stronger signal)
    Otherwise                     → HOLD_CONJECTURAL
    """
    tally = {v.value: 0 for v in ReviewVerdict}
    for vote in votes:
        tally[vote.verdict.value] += 1
    approve = tally[ReviewVerdict.APPROVE.value]
    reject = tally[ReviewVerdict.REJECT.value]
    needs = tally[ReviewVerdict.NEEDS_MORE_INFO.value]
    err = tally[ReviewVerdict.ERROR.value]
    total = len(votes)
    if approve == total:
        return BoardDecision(
            votes=list(votes),
            outcome_hint="PROMOTE",
            rationale="Unanimous APPROVE from the AI review board.",
        )
    if reject >= 1:
        return BoardDecision(
            votes=list(votes),
            outcome_hint="DEMOTE",
            rationale=(
                f"{reject} REJECT vote(s); the coupling is demoted "
                f"to conjectural per §12.2."
            ),
        )
    if approve == 2 and needs == 1:
        return BoardDecision(
            votes=list(votes),
            outcome_hint="HOLD_EMPIRICAL",
            rationale="2 APPROVE + 1 NEEDS_MORE_INFO: hold at EMPIRICAL, flag for follow-up.",
        )
    return BoardDecision(
        votes=list(votes),
        outcome_hint="HOLD_CONJECTURAL",
        rationale=(
            f"Mixed verdicts (approve={approve}, reject={reject}, "
            f"needs_info={needs}, error={err}); hold at CONJECTURAL."
        ),
    )


class ReviewBoard:
    """High-level interface to the three-model review board.

    Usage:

        with ReviewBoard() as board:
            for h, v, e in ranked_candidates:
                decision = board.review(h, v.as_dict(), e.as_dict())
                # record decision.as_dict() in the ledger

    The context manager fetches keys on enter and clears them on
    exit. Re-entering is allowed but each entry fetches fresh
    keys (callers that want long-lived sessions should reuse a
    single `with` block).
    """

    def __init__(self):
        self._keys: Optional[ReviewBoardKeys] = None

    def __enter__(self) -> "ReviewBoard":
        self._keys = ReviewBoardKeys.load()
        return self

    def __exit__(self, exc_type, exc, tb) -> None:
        self._keys = None

    def review(
        self,
        hypothesis: CouplingHypothesis,
        physical_verdict_dict: Optional[Dict[str, Any]] = None,
        emergent_dict: Optional[Dict[str, Any]] = None,
    ) -> BoardDecision:
        """Collect verdicts from all three reviewers and return
        the aggregated decision. Requires the board to be inside
        its `with` block.
        """
        if self._keys is None:
            raise RuntimeError(
                "ReviewBoard.review() called outside a `with` block; "
                "keys have not been loaded."
            )
        user_msg = _build_review_prompt(hypothesis, physical_verdict_dict, emergent_dict)
        votes: List[ReviewVote] = []
        for reviewer, fn, key in (
            ("claude-opus-4-6", _call_claude, self._keys.anthropic),
            ("openai-gpt-5", _call_openai, self._keys.openai),
            ("gemini-2.5-pro", _call_gemini, self._keys.gemini),
        ):
            ts = datetime.now(tz=timezone.utc).isoformat()
            try:
                raw = fn(key, user_msg)
                verdict, reason = _parse_verdict(raw)
            except AIBoardAPIError as exc:
                raw = f"AIBoardAPIError: {exc}"
                verdict = ReviewVerdict.ERROR
                reason = str(exc)
            votes.append(ReviewVote(
                reviewer=reviewer,
                verdict=verdict,
                reason=reason,
                raw_response=raw,
                timestamp=ts,
            ))
        return _aggregate(votes)


# ---------------------------------------------------------------------------
# Offline dry-run (no API calls)
# ---------------------------------------------------------------------------


def dry_run_board(
    hypothesis: CouplingHypothesis,
    physical_verdict_dict: Optional[Dict[str, Any]] = None,
    emergent_dict: Optional[Dict[str, Any]] = None,
) -> BoardDecision:
    """Construct a synthetic board decision without calling any
    vendor API. Used by Phase 10's pre-registered test harness
    to exercise the ledger-write path while the user decides
    whether to burn API credits on the real board.

    Heuristic: if the physical verdict says `passed=True`, vote
    unanimous APPROVE; if a FAILED outcome exists, vote
    unanimous REJECT; otherwise all three vote NEEDS_MORE_INFO.
    This is a *stub*, not a judgement — it exists so the code
    path runs end-to-end.
    """
    if physical_verdict_dict and physical_verdict_dict.get("passed"):
        verdict = ReviewVerdict.APPROVE
        reason = "Dry-run auto-APPROVE: physical constraint filter passed."
    elif physical_verdict_dict and any(
        r.get("outcome") == "failed"
        for r in (physical_verdict_dict.get("results") or [])
    ):
        verdict = ReviewVerdict.REJECT
        reason = "Dry-run auto-REJECT: physical constraint filter reported FAILED."
    else:
        verdict = ReviewVerdict.NEEDS_MORE_INFO
        reason = "Dry-run default: physical filter not decisive."
    ts = datetime.now(tz=timezone.utc).isoformat()
    votes = [
        ReviewVote(r, verdict, reason, "dry-run (no api)", ts)
        for r in ("claude-opus-4-6", "openai-gpt-5", "gemini-2.5-pro")
    ]
    return _aggregate(votes)
