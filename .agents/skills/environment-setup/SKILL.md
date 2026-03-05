---
name: environment-setup
description: Environment initialization and management for Cytognosis projects
---

# Environment Setup Skill

## Package Manager
This project uses **uv** for Python dependency management.

## Environment Initialization
```bash
# Create/reset the environment
python scripts/setup_env.py --strategy resolve --env-name ml --compute-backend rocm

# Or use nox
nox -s setup_env
```

## Environment Strategies
- **prelocked**: Install from pre-built lockfiles (fastest, deterministic)
- **resolve**: Dynamically resolve dependencies via Cytoskeleton components
- **empty**: Standard `uv sync` with only pyproject.toml dependencies

## Cytoskeleton Integration
When `use_cytoskeleton` is enabled:
- Submodule at `modules/cytoskeleton/`
- Environment configs in `modules/cytoskeleton/configs/environments/`
- Component definitions in `modules/cytoskeleton/configs/components/`
- Pre-built lockfiles in `modules/cytoskeleton/locked/`

## Compute Backends
- **rocm**: AMD GPU acceleration (ROCm 7.2+)
- **cuda**: NVIDIA GPU acceleration (CUDA 12+)
- **cpu**: CPU-only execution
