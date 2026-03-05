# cyto-assist Workflow HOWTO

Welcome to the development workflow guide.

## 1. Updating the Template with Cruft

This repository inherently tracks the Cytognosis cookiecutter template it was generated from using `cruft`.
When upstream standards (e.g., PyTorch baselines, formatting rules, Nox sessions) evolve, you pull those updates directly into your active repository:

```bash
uv tool run cruft update
```

Cruft will automatically execute a 3-way merge strategy. If conflicts exist, it drops a `.rej` file that you resolve manually.

## 2. Interactive Notebooks & Publishing

We provide Quarto (`tutorial.qmd`) and Marimo (`tutorial.py`) within `docs/notebooks/`.
Launch them interactively via Nox:

```bash
nox -s quarto_preview
nox -s marimo_edit
```

To natively publish your Quarto documents to your active GitHub Pages deployment:

```bash
nox -s quarto_publish
```

## 3. Strict Resource Allocation

When running large data processing pipelines or debugging AMD APU bottlenecks on standard consumer hardware, use the Nox environment variables provided globally through `resource_allocated_run`:

- `CYTO_LIMIT_CPUS=N`: Throttles execution to `N` cores via `taskset`.
- `CYTO_LIMIT_MEM=Bytes`: Throttles total memory bound via `prlimit`.
- `CYTO_LIMIT_GPUS=N`: Disables visibility of N+1 GPUs (injects `CUDA_VISIBLE_DEVICES`).
- `CYTO_APU_GFX_OVERRIDE=10.3.0`: Injects AMD APU Overrides (`HSA_OVERRIDE_GFX_VERSION`) universally across underlying PyTorch calls.

Example usage:

```bash
CYTO_APU_GFX_OVERRIDE=10.3.0 CYTO_LIMIT_CPUS=4 nox -s test
```
