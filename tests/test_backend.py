import subprocess
import sys
from importlib.util import find_spec

import pytest


def test_python_version():
    """Verify standard python version meets minimum requirements."""
    assert sys.version_info >= (3, 10), "Python version must be 3.10 or higher"

def test_package_import():
    """Verify that the primary project package can be imported."""
    package_name = "cyto_assist"
    assert find_spec(package_name) is not None, f"Could not import package: {package_name}"

def test_compute_backend():
    """Verify the compute backend (CUDA, ROCm, CPU) matches expectations if PyTorch is installed."""
    has_torch = find_spec("torch") is not None
    if not has_torch:
        pytest.skip("PyTorch is not installed. Skipping compute backend checks.")

    import torch

    expected_backend = "rocm"
    if expected_backend == "cuda":
        assert "cu" in torch.__version__ or (hasattr(torch.version, 'cuda') and torch.version.cuda is not None and "rocm" not in torch.__version__), f"Expected CUDA backend but PyTorch version is {torch.__version__}."
    elif expected_backend == "rocm":
        assert "rocm" in torch.__version__ or (hasattr(torch.version, 'hip') and torch.version.hip is not None) or (hasattr(torch.version, 'cuda') and torch.version.cuda is not None), f"Expected ROCm backend but PyTorch version is {torch.__version__}."
    elif expected_backend == "cpu":
        assert "cu" not in torch.__version__ and "rocm" not in torch.__version__, f"Expected strictly CPU backend, but a GPU build ({torch.__version__}) was detected."
    else:
        pytest.fail(f"Unknown compute backend specified: {expected_backend}")
