import pytest

import cyto_assist


def test_package_has_version() -> None:
    """Test that the package has a version defined."""
    version = getattr(cyto_assist, "__version__", None)
    assert version is not None, "Package __version__ is not defined"


def test_package_import() -> None:
    """Test that the main components can be imported."""
    assert hasattr(cyto_assist, "pl")
    assert hasattr(cyto_assist, "pp")
    assert hasattr(cyto_assist, "tl")


def test_basic_benchmark() -> None:
    """Test standard array allocations and basic math for naive benchmarking."""
    import numpy as np
    import time

    start = time.time()
    arr = np.random.randn(1000, 1000)
    res = arr @ arr.T
    duration = time.time() - start

    assert res.shape == (1000, 1000)
    assert duration < 5.0, f"Benchmark took too long: {duration}s"


@pytest.mark.skip(reason="This decorator should be removed when test passes.")
def test_example():
    assert 1 == 0  # This test is designed to fail.


@pytest.mark.skip(reason="This decorator should be removed when test passes.")
@pytest.mark.parametrize(
    "transform,layer_key,max_items,expected_len,expected_substring",
    [
        # Test default parameters
        (lambda vals: f"mean={vals.mean():.2f}", None, 100, 1, "mean="),
        # Test with layer_key
        (lambda vals: f"mean={vals.mean():.2f}", "scaled", 100, 1, "mean=0."),
        # Test with max_items limit (won't affect single item)
        (lambda vals: f"max={vals.max():.2f}", None, 1, 1, "max=6.70"),
    ],
)
def test_elaborate_example_adata_only_simple(
    adata,  # this tests uses the adata object from the fixture in the conftest.py
    transform,
    layer_key,
    max_items,
    expected_len,
    expected_substring,
):
    result = cyto_assist.pp.elaborate_example(
        items=[adata], transform=transform, layer_key=layer_key, max_items=max_items
    )

    assert len(result) == expected_len
    assert expected_substring in result[0]
