"""Container-sandboxed notebook execution (design v4 §11b).

Phase 13 composite notebooks are generated programmatically
from a coupling hypothesis + board-sourced parameters, then
executed inside a pinned-SHA Docker container with no network,
no host volume mounts beyond the input notebook itself, and
a content-hashed ledger entry. This module provides the
Python-side wrapper that invokes the container and captures
the provenance.

Phase 12 uses this module too: the canonical-problem unit
tests authored in each equation's `problems/` directory run
through the same sandbox, so the execution path from test
(Phase 12) to composite (Phase 13) is the same code — the
only difference is who wrote the notebook.

Security contract (design v4 §11b):
- Pinned image SHA256 (from `labs_v2/exec/Dockerfile`)
- `--network=none` — notebooks cannot reach the internet
- `--read-only` root filesystem
- `--tmpfs /workspace:rw,size=64m` ephemeral scratch
- Non-root UID 1000:1000 (enforced by Dockerfile)
- `--memory=512m --cpus=1.0` cgroup limits
- Per-cell timeout 60s (nbclient default)
- Input notebook mounted read-only via bind mount
- SHA256 of notebook content logged in every execution record

No corner cuts: if the sandbox execution fails, the
Failure Investigation Protocol (§11h) fires. Tolerances are
NOT adjusted. The sandbox itself is one of the things a
failure investigation can blame — a bad image SHA, a broken
dependency, or a sandbox escape attempt — so the ledger
records the full image fingerprint for every run.
"""

from __future__ import annotations

import hashlib
import json
import subprocess
import tempfile
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional


# The expected image tag used when docker-running. This is
# separate from the image SHA — the SHA is computed at run
# time from the actual image the daemon has loaded, so even
# if someone re-tagged a different image with the same tag,
# the ledger still records what actually ran.
IMAGE_TAG = "hequ-exec:pinned"


@dataclass
class SandboxRunResult:
    """Result of executing one notebook in the sandbox."""
    notebook_path: str
    notebook_sha256: str
    image_tag: str
    image_sha256: str
    exit_code: int
    stdout: str
    stderr: str
    wall_time_seconds: float
    executed_at: str                 # ISO8601 UTC
    timed_out: bool = False
    error: Optional[str] = None

    def passed(self) -> bool:
        """True iff the notebook ran to completion with no error."""
        return self.exit_code == 0 and not self.timed_out and not self.error

    def as_ledger_dict(self) -> Dict[str, Any]:
        return {
            "notebook_path": self.notebook_path,
            "notebook_sha256": self.notebook_sha256,
            "image_tag": self.image_tag,
            "image_sha256": self.image_sha256,
            "exit_code": self.exit_code,
            "wall_time_seconds": round(self.wall_time_seconds, 3),
            "executed_at": self.executed_at,
            "timed_out": self.timed_out,
            "error": self.error,
            "passed": self.passed(),
            # stdout/stderr are intentionally NOT in the ledger
            # dict by default — they can be large. The caller
            # reads them separately if an audit needs them.
        }


class SandboxError(Exception):
    """Raised when the sandbox itself fails to run (not when
    the notebook inside it fails — that's captured in the
    SandboxRunResult's exit_code).
    """


def _sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as fh:
        for chunk in iter(lambda: fh.read(65536), b""):
            h.update(chunk)
    return "sha256:" + h.hexdigest()


def _image_sha256(image_tag: str) -> str:
    """Return the SHA256 of the docker image currently loaded
    under `image_tag`. Raises SandboxError if the image is
    missing or docker is not available.
    """
    try:
        out = subprocess.run(
            ["docker", "image", "inspect", image_tag, "--format={{.Id}}"],
            capture_output=True,
            check=True,
            timeout=10,
        )
    except FileNotFoundError as exc:
        raise SandboxError(
            f"docker binary not found in PATH. Install Docker "
            f"Desktop, OrbStack, Colima, or Podman to use the "
            f"sandbox. See labs_v2/exec/Dockerfile for the "
            f"build instructions."
        ) from exc
    except subprocess.CalledProcessError as exc:
        raise SandboxError(
            f"docker image '{image_tag}' not found. Build it "
            f"with: cd labs_v2/exec && docker build -t {image_tag} ."
        ) from exc
    return out.stdout.decode("utf-8").strip()


def run_notebook(
    notebook_path: Path,
    memory_mb: int = 512,
    cpus: float = 1.0,
    image_tag: str = IMAGE_TAG,
) -> SandboxRunResult:
    """Execute `notebook_path` inside the pinned-SHA sandbox
    and return a SandboxRunResult with full provenance.

    The notebook is bind-mounted **read-only** into the
    container at `/workspace/in.ipynb`. The container has no
    network, a read-only root filesystem, and a tmpfs
    `/workspace` of 64 MB for any scratch output.

    Raises `SandboxError` if the sandbox itself cannot run
    (missing docker, missing image). Notebook-level errors
    (cell exceptions, timeouts) are captured in the returned
    SandboxRunResult with a non-zero exit code.
    """
    import time as _time

    notebook_path = notebook_path.resolve()
    if not notebook_path.is_file():
        raise SandboxError(f"notebook not found: {notebook_path}")

    image_sha = _image_sha256(image_tag)
    nb_sha = _sha256_file(notebook_path)

    docker_cmd = [
        "docker", "run",
        "--rm",
        "--network=none",
        "--read-only",
        "--tmpfs", "/workspace:rw,size=64m",
        "--memory", f"{memory_mb}m",
        "--cpus", str(cpus),
        "--user", "1000:1000",
        "-v", f"{notebook_path}:/workspace/in.ipynb:ro",
        image_tag,
        "/workspace/in.ipynb",
    ]

    t_start = _time.perf_counter()
    ts = datetime.now(tz=timezone.utc).isoformat()
    timed_out = False
    error: Optional[str] = None
    stdout = ""
    stderr = ""
    exit_code = -1

    try:
        proc = subprocess.run(
            docker_cmd,
            capture_output=True,
            timeout=120,  # outer wall-clock timeout (inner per-cell is 60s)
        )
        exit_code = proc.returncode
        stdout = proc.stdout.decode("utf-8", errors="replace")
        stderr = proc.stderr.decode("utf-8", errors="replace")
    except subprocess.TimeoutExpired as exc:
        timed_out = True
        exit_code = 124  # conventional "timeout" exit code
        error = f"sandbox wall-clock timeout after {exc.timeout}s"
        if exc.stdout:
            stdout = exc.stdout.decode("utf-8", errors="replace")
        if exc.stderr:
            stderr = exc.stderr.decode("utf-8", errors="replace")
    except Exception as exc:
        error = f"sandbox run failed: {type(exc).__name__}: {exc}"

    wall_time = _time.perf_counter() - t_start

    return SandboxRunResult(
        notebook_path=str(notebook_path),
        notebook_sha256=nb_sha,
        image_tag=image_tag,
        image_sha256=image_sha,
        exit_code=exit_code,
        stdout=stdout,
        stderr=stderr,
        wall_time_seconds=wall_time,
        executed_at=ts,
        timed_out=timed_out,
        error=error,
    )


def run_notebook_text(
    notebook_json: str,
    memory_mb: int = 512,
    cpus: float = 1.0,
    image_tag: str = IMAGE_TAG,
) -> SandboxRunResult:
    """Convenience wrapper: accept notebook content as a JSON
    string (typical for programmatically-generated notebooks),
    write it to a temp file, execute it, return the result.

    The temp file is deleted on successful run. On failure the
    temp file is preserved so the caller can inspect what was
    actually executed.
    """
    tmp = tempfile.NamedTemporaryFile(
        mode="w", suffix=".ipynb", delete=False, encoding="utf-8"
    )
    tmp.write(notebook_json)
    tmp.close()
    tmp_path = Path(tmp.name)
    try:
        result = run_notebook(
            tmp_path,
            memory_mb=memory_mb,
            cpus=cpus,
            image_tag=image_tag,
        )
        if result.passed():
            tmp_path.unlink()
        return result
    except Exception:
        # Preserve the temp file on any unexpected error
        raise
