import sys
import pytest
from loguru import logger

def test_python_version():
    """Verify the environment Python version matches expectations."""
    assert sys.version_info >= (3, 11), "Python version must be 3.11+"


def test_core_dependencies():
    """Verify core scientific libraries are importable."""
    import numpy as np
    import pandas as pd
    import scipy

    assert np.__version__
    assert pd.__version__
    assert scipy.__version__

def test_pytorch_installation():
    """Verify PyTorch is installed and properly configured."""
    import torch

    logger.info(f"Testing PyTorch version: {torch.__version__}")
    assert torch.__version__ is not None

    backend = "rocm"

    if backend == "cuda":
        if not torch.cuda.is_available():
            pytest.skip("CUDA hardware not detected on host, skipping hardware binding check.")
        logger.info(f"CUDA Version: {torch.version.cuda}")
        logger.info(f"GPU Count: {torch.cuda.device_count()}")
    elif backend == "rocm":
        if not torch.cuda.is_available():
            pytest.skip("ROCm hardware not detected on host, skipping hardware binding check.")
        logger.info(f"HIP/ROCm Version: {torch.version.hip}")
    else:
        logger.info("Using CPU backend for PyTorch")

def test_jax_installation():
    """Verify JAX is installed and configured."""
    try:
        import jax
    except ImportError:
        pytest.skip("JAX not installed in this environment.")

    logger.info(f"Testing JAX version: {jax.__version__}")

    backend = "rocm"
    devices = jax.devices()
    logger.info(f"JAX Devices: {devices}")

    if backend in ["cuda", "rocm"]:
        if not any(d.device_kind.lower() != "cpu" for d in devices):
            pytest.skip(f"JAX requested {backend} but physical GPU hardware was not detected.")
