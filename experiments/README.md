# Experiments Directory

This directory contains ML experiments and research workflows for cyto-assist.

## Structure

```
experiments/
├── configs/          # Hydra configuration files
├── scripts/          # Training and evaluation scripts
├── notebooks/        # Exploratory analysis notebooks
├── results/          # Experiment outputs and metrics
├── checkpoints/      # Model checkpoints
└── logs/            # Training logs and artifacts
```

## Getting Started

1. **Set up Weights & Biases**:
   ```bash
   wandb login
   ```

2. **Run an experiment**:
   ```bash
   python scripts/train.py experiment=baseline
   ```

3. **View results**:
   - Check `results/` for metrics and outputs
- View experiments on [Weights & Biases](https://wandb.ai)
## Configuration Management

We use [Hydra](https://hydra.cc/) for configuration management. All experiment configs are in `configs/`.

## Best Practices

- Always version your experiments
- Document hyperparameter choices
- Save reproducible environment snapshots
- Follow HIPAA compliance for clinical data
