import marimo

__generated_with = "0.10.0"
app = marimo.App(width="full", layout_file="layout.json")


@app.cell
def __():
    import marimo as mo
    import cyto_assist as pkg
    import torch
    import numpy as np

    mo.md(
        """
        # cyto-assist Marimo Tutorial

        Welcome to the reactive Cytognosis tutorial framework.
        """
    )
    return mo, pkg, np, torch

@app.cell
def __(mo, pkg, torch):
    mo.md(
        f"""
        ## Environment Overview

        - **Package Version**: `{pkg.__version__}`
        - **Compute Backend**: `rocm`
        - **HW Acceleration**: `{'Available' if torch.cuda.is_available() else 'Disabled'}`
        """
    )
    return


@app.cell
def __(np, mo):
    mo.md("## Analysis Workflow")
    arr = np.random.randn(100, 100)

    mo.ui.table(arr[:5, :5])
    return arr,


if __name__ == "__main__":
    app.run()
