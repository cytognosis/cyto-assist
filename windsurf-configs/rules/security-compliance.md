---
description: Security and compliance guidelines
globs: ["**/*.py", "**/*.yaml", "**/*.toml", "Dockerfile"]
---
# Security & Compliance

## Data Protection
- **Encryption**: Encrypt data at rest and in transit.
- **Access Control**: Minimize access to data (Principle of Least Privilege).
- **Sanitization**: Sanitize inputs to prevent injection attacks.

## Dependencies
- Pin all dependencies in `uv.lock` or `requirements.txt`.
- Scan dependencies for vulnerabilities (`nox -s security`).
- Remove unused dependencies regularly.

## Container Security
- Run containers as non-root users.
- Minimal base images (e.g., `distroless` or `python:slim`).
- Do not include secrets in Dockerfiles.

## Secrets Management
- Use environment variables for secrets.
- Never commit `.env` files.
- Use a secret manager in production.
