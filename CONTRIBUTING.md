# Contributing

Contributions are welcome if they keep the helper small, reproducible, and public-safe.

Good contributions include:

- Better LaTeX structure scanning.
- More journal handoff checks.
- Improvements to the generated Word checklist.
- Synthetic fixtures and tests.

Before opening a pull request:

- Use synthetic LaTeX projects only.
- Do not commit real manuscripts, unpublished figures, real bibliography exports, local paths, or credentials.
- Run `python -m unittest discover -s tests`.
- Run `python scripts/validate_public_assets.py`.
