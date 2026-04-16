"""Pipeline: convert and execute every labs_v2 notebook.

Discovers `notebook.py` files under `labs_v2/equations/**/EQ-*/`,
converts each to `.ipynb` with jupytext, executes it in a clean
kernel, and writes the executed notebook to
`labs_v2/notebooks_out/`. Reports pass/fail per lab and exits
non-zero if any notebook failed.

Usage (inside the v2 container)::

    PYTHONPATH=labs_v2 python labs_v2/framework/build_notebooks.py

Design: mirrors the v1 pipeline's shape but targets labs_v2. Every
lab is its own file; the runner is deliberately dumb so adding a new
equation requires zero changes here.
"""

from __future__ import annotations

import sys
import time
import traceback
from pathlib import Path
from typing import List, Optional, Tuple

import jupytext
import nbformat
from nbclient import NotebookClient


LABS_V2 = Path("/home/jovyan/work/labs_v2")
EQUATIONS_DIR = LABS_V2 / "equations"
OUT_DIR = LABS_V2 / "notebooks_out"


def discover_notebooks() -> List[Path]:
    """Find every notebook.py under labs_v2/equations/**/EQ-*/."""
    return sorted(EQUATIONS_DIR.rglob("EQ-*/notebook.py"))


def convert_and_execute(source_py: Path) -> Tuple[Path, float, Optional[Exception]]:
    eq_dir = source_py.parent
    eq_id = eq_dir.name
    domain = eq_dir.parent.name
    out_sub = OUT_DIR / domain
    out_sub.mkdir(parents=True, exist_ok=True)
    out_path = out_sub / f"{eq_id}.ipynb"

    started = time.perf_counter()
    try:
        nb = jupytext.read(source_py)
        client = NotebookClient(
            nb,
            timeout=600,
            kernel_name="python3",
            resources={"metadata": {"path": str(eq_dir)}},
        )
        client.execute()
        nbformat.write(nb, out_path)
    except Exception as exc:  # noqa: BLE001
        return out_path, time.perf_counter() - started, exc
    return out_path, time.perf_counter() - started, None


def main() -> int:
    notebooks = discover_notebooks()
    if not notebooks:
        print("No notebook.py files found under labs_v2/equations/", file=sys.stderr)
        return 1

    print(f"Discovered {len(notebooks)} notebook(s):")
    for p in notebooks:
        print(f"  - {p.relative_to(LABS_V2)}")
    print()

    results = []
    for nb_path in notebooks:
        print(f"==> Executing {nb_path.relative_to(LABS_V2)} ...", flush=True)
        out, elapsed, err = convert_and_execute(nb_path)
        if err is None:
            print(f"    OK ({elapsed:.1f}s)  ->  {out.relative_to(LABS_V2)}")
        else:
            print(f"    FAIL ({elapsed:.1f}s): {type(err).__name__}: {err}",
                  file=sys.stderr)
            traceback.print_exception(type(err), err, err.__traceback__,
                                      file=sys.stderr)
        results.append((nb_path, out, elapsed, err))

    print()
    print("Summary")
    print("-------")
    passed = sum(1 for _, _, _, e in results if e is None)
    failed = len(results) - passed
    for src, out, elapsed, err in results:
        status = "PASS" if err is None else "FAIL"
        print(f"  [{status}] {elapsed:6.1f}s  {src.relative_to(LABS_V2)}")
    print(f"\n{passed} passed, {failed} failed.")
    return 0 if failed == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
