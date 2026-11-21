---
paths:
  - "**/*.py"
  - "**/pyproject.toml"
---

# Python

The project's own configuration decides: use the package manager, formatter, linter, type checker, and test runner that `pyproject.toml`, the lockfile, and CI already name. The points below apply where the project is silent.

- Run tools through the project's environment (`uv run`, `poetry run`, or the project's virtual environment), so that the versions the lockfile pins are the ones that run. Add a dependency with the package manager, so the manifest and lockfile change together.
- Annotate the parameters and return type of every function you add or change, and avoid `Any`; some type checkers skip the body of an unannotated function by default.
- Validate data at the point it enters the program (request bodies, files, environment variables, API responses) and pass typed values inward.
- Catch the specific exception you can handle. Let the rest propagate; when re-raising as another type, use `raise ... from err` to keep the cause.
- Use `pathlib.Path` for file paths, a context manager for anything that must be closed, and timezone-aware `datetime` values.
- Log through the `logging` module with a module-level logger, passing values as arguments (`logger.info("loaded %s", name)`) so formatting is skipped when the level is off.
