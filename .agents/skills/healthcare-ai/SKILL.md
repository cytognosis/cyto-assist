---
name: healthcare-ai
description: Healthcare AI development practices, HIPAA compliance, and clinical ML patterns
---

# Healthcare AI Development Skill

## Domain Context
Cytognosis develops AI-native technology for preventive healthcare and disease detection. All code must consider clinical safety and regulatory compliance.

## Data Handling
- **Never** log or expose patient identifiers (PHI)
- Use anonymized/de-identified data for development
- Follow HIPAA minimum necessary principle
- Validate all input data rigorously

## Model Development
- Document model assumptions and limitations
- Track all experiments with Weights & Biases
- Use reproducible training pipelines (seed everything)
- Validate on clinically relevant metrics, not just accuracy

## Code Patterns
- Use type-safe data structures for clinical data
- Implement input validation at API boundaries
- Add comprehensive error handling for edge cases
- Write audit-friendly logging (what, when, who, why)

## Dependencies
- PyTorch/Lightning for deep learning
- scanpy/anndata for single-cell analysis
- scvi-tools for variational inference
- pertpy for perturbation analysis
