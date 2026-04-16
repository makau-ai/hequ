# Sandboxed notebook executor for Phase 13 composite problems.
# Pinned base image by SHA256 per design v4 §11b. Upgrades to a
# newer base require an explicit design-doc update + Round 2
# discharge review.
FROM python:3.12-slim@sha256:c24c34b502635f1f7c4e99dc09a2cbd85d480b7dcfd077198c6b5af138906390

# Non-root user for defense in depth
ARG UID=1000
ARG GID=1000
RUN groupadd -g ${GID} hequ && \
    useradd -m -u ${UID} -g ${GID} -s /bin/bash hequ

# System packages kept minimal — no curl, no wget, no git
# (attack surface reduction). Build deps only where the pinned
# wheels require them.
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
        libgmp-dev \
        libmpfr-dev \
        libmpc-dev && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

# Copy the frozen requirements with pip hashes and install.
# The image's sole purpose is to execute pre-generated
# notebooks against the standard scientific Python stack plus
# python-flint (for Check D in the verification pipeline).
COPY requirements.txt /tmp/requirements.txt
RUN pip install --no-cache-dir --require-hashes -r /tmp/requirements.txt && \
    rm /tmp/requirements.txt

# Workspace tmpfs mount happens at `docker run` time via
# `--tmpfs /workspace:rw,size=64m`. The Dockerfile creates the
# mount point but does not populate it.
WORKDIR /workspace
RUN chown hequ:hequ /workspace

# Drop privileges — all notebook execution runs as uid 1000
USER hequ:hequ

# Matplotlib default backend must not try to open a GUI.
ENV MPLBACKEND=Agg
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Default entrypoint: execute a single notebook via nbclient
# with a 60-second per-cell timeout. The notebook path is
# passed as a positional argument at `docker run` time.
ENTRYPOINT ["python", "-m", "nbclient", "--timeout=60"]
CMD ["/workspace/in.ipynb"]
