# Repository Guidelines

## Project Structure & Module Organization

This project folder currently contains course/project documents only:

- `CloudIntegration.pdf` - cloud integration reference material.
- `DevOps projet.pdf` - project brief or assignment document.

No application source, tests, build scripts, or asset directories are present in this directory yet. If implementation files are added, keep them organized by concern, for example `src/` for production code, `tests/` for automated tests, `docs/` for supporting documentation, and `assets/` for images or static resources. Avoid placing generated outputs or temporary files at the repository root.

## Build, Test, and Development Commands

There are no project-specific build or test commands in this folder at the moment. Before adding code, include a README or tool-specific manifest so contributors can run the project consistently.

Suggested examples for future additions:

- `npm install` / `npm test` for a Node.js project.
- `python -m venv .venv` and `pip install -r requirements.txt` for Python.
- `make test` if a Makefile is introduced as the command entry point.

Document every required command when the matching toolchain is added.

## Coding Style & Naming Conventions

Use clear, descriptive filenames and keep names consistent within each language ecosystem. Prefer lowercase directory names such as `src`, `tests`, and `docs`. For scripts, use meaningful action names such as `generate_report.py` or `deploy_app.sh`.

When code is introduced, configure standard formatting and linting for the chosen stack, for example Prettier/ESLint for JavaScript or Black/Ruff for Python. Do not commit editor-specific formatting changes unless they are enforced by project tooling.

## Testing Guidelines

No tests are currently present. Add automated tests alongside any new source code. Place test files under `tests/` or use the framework's conventional layout. Use names that describe behavior, such as `test_database_connection.py` or `user-service.test.js`.

## Commit & Pull Request Guidelines

Recent git history uses short, imperative commit messages, for example `Configure PostgreSQL data source and dependencies`. Continue that style: start with a verb, keep the subject concise, and describe one logical change per commit.

Pull requests should include a short summary, relevant issue or assignment references, test results, and screenshots or generated artifacts when visual or document output changes. Keep unrelated filesystem changes out of commits, especially because the git root is above this project folder.

## Agent-Specific Instructions

Before editing, check for existing files and avoid overwriting user work. Keep changes scoped to this directory unless explicitly instructed otherwise.
