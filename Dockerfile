# =============================================================================
# hequ — Critical Equations Lab Environment
# =============================================================================
# Purpose:
#   Reproducible container for authoring, executing, and verifying
#   Hoare-triple-annotated exploratory labs over the critical-equations corpus.
#
# Base image:
#   jupyter/scipy-notebook ships with numpy, scipy, matplotlib, sympy, pandas,
#   jupyter, and a non-root user (jovyan). We add a small set of verification
#   and notebook-source-control tools on top.
#
# Build:
#   docker build -t hequ-labs:latest /Users/matthewluallen/hequ
#
# Run (interactive Jupyter Lab):
#   docker run --rm -p 8888:8888 \
#     -v /Users/matthewluallen/hequ:/home/jovyan/work \
#     hequ-labs:latest
#
# Run (headless notebook execution — used by the build pipeline):
#   docker run --rm \
#     -v /Users/matthewluallen/hequ:/home/jovyan/work \
#     hequ-labs:latest \
#     bash -lc "cd /home/jovyan/work && python labs/00_framework/build_notebooks.py"
#
# Migration notes:
#   See MIGRATION.md for guidance on moving this environment to
#   (a) bare-metal Python, (b) conda/mamba, (c) a different container
#   runtime (Podman, Apptainer), or (d) a managed notebook service.
# =============================================================================

FROM quay.io/jupyter/scipy-notebook:2024-10-14

LABEL org.opencontainers.image.title="hequ-labs"
LABEL org.opencontainers.image.description="Hoare-verified exploratory labs for the critical-equations corpus"
LABEL org.opencontainers.image.source="local"

USER root

# System packages: graphviz for derivation-chain diagrams, git for provenance.
RUN apt-get update && apt-get install -y --no-install-recommends \
        graphviz \
        git \
    && rm -rf /var/lib/apt/lists/*

USER ${NB_UID}

# Python packages pinned for reproducibility. See requirements.txt for rationale.
COPY --chown=${NB_UID}:${NB_GID} requirements.txt /tmp/requirements.txt
RUN pip install --no-cache-dir -r /tmp/requirements.txt

# Lean 4 toolchain via elan. This is the formal-verification backend
# for the labs_v2 Layer 4 certification pass. We install the toolchain
# unconditionally (no mathlib — the Small-plus scope only needs bare
# Lean 4 core to compile standalone theorems). elan sets up a user-
# local toolchain under ~/.elan; the PATH export makes `lean` and
# `lake` available.
#
# elan defers the actual toolchain tarball download until first use
# of `lean`. Without the dummy compile below, every `docker run --rm`
# would re-download at run time. We force the download into the image
# layer by compiling a trivial file during build.
RUN curl -sSfL https://raw.githubusercontent.com/leanprover/elan/master/elan-init.sh \
        -o /tmp/elan-init.sh && \
    bash /tmp/elan-init.sh -y --default-toolchain leanprover/lean4:v4.12.0 && \
    rm /tmp/elan-init.sh && \
    echo '#eval "bake the toolchain into the image layer"' > /tmp/dummy.lean && \
    /home/jovyan/.elan/bin/lean /tmp/dummy.lean && \
    rm /tmp/dummy.lean
ENV PATH="/home/jovyan/.elan/bin:${PATH}"

WORKDIR /home/jovyan/work

# Default command: launch Jupyter Lab on 0.0.0.0:8888 with no token for local
# development. Override at `docker run` time for headless execution.
CMD ["start-notebook.sh", "--ServerApp.token=''", "--ServerApp.password=''"]
