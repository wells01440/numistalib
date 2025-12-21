# § GitHub Actions Workflows

## § 0 Overview

Automated quality enforcement per **AGENTS.md §9**.

## § 1 Workflows

### § 1.0 docstring-agent.yml

**Purpose**: Maintain fastidious NumPy-style docstrings per **AGENTS.md §4.1.1**.

**Triggers**:
0. Pull requests modifying `src/**/*.py`
1. Pushes to `main`/`master` branches
2. Manual via `workflow_dispatch`

**Actions**:
0. **pydocstyle** - Validates NumPy convention compliance
1. **interrogate** - Measures docstring coverage (fail-under: 80%)
2. **darglint** - Validates parameter/return documentation matches signatures
3. **Issue Creation** - Auto-files GitHub issue with validation reports when failures detected
4. **PR Comments** - Posts coverage summary on pull requests
5. **Badge Generation** - Updates `docs/docstring-coverage.svg` on main branch

**Configuration**:
- Settings in `setup.cfg`
- Dev dependencies in `pyproject.toml`

**Reference Examples**:
- `src/numistalib/services/catalogues/service.py` - Complete NumPy docstrings
- **AGENTS.md §4.1** - Docstring standards

## § 2 Local Validation

Run validation locally before committing:

```bash
# Validate NumPy convention
uv run pydocstyle --convention=numpy --add-ignore=D100,D104,D105 src/

# Check coverage
uv run interrogate --verbose --fail-under=80 --exclude tests src/

# Validate arguments
uv run darglint --docstring-style=numpy src/
```

## § 3 Standards

### § 3.1 Public APIs

**Required sections** (NumPy format):

```python
def method_name(param1: str, param2: int) -> list[str]:
    """Short one-line summary.

    Optional extended description providing additional context.

    Parameters
    ----------
    param1 : str
        Description of param1
    param2 : int
        Description of param2

    Returns
    -------
    list[str]
        Description of return value

    Raises
    ------
    ValueError
        When invalid input provided
    """
```

### § 3.2 Private Methods

One-line docstrings only:

```python
def _internal_helper(self, data: dict) -> bool:
    """Process internal data structure."""
```

## § 4 Enforcement

**Merge Blocking**: Per **AGENTS.md §9.3**
0. All public APIs must have complete NumPy docstrings
1. Coverage must meet 80% threshold
2. Parameters/returns must match signatures

**Review Process**:
0. Workflow runs automatically on PR
1. Issues created for violations
2. PR comments guide fixes
3. Re-run after corrections

## § 5 Exceptions

Per **AGENTS.md §4.1.2**:
0. Tests excluded (`tests/` directory)
1. Private methods use simplified format
2. Magic methods may omit sections when self-evident

## § 6 References

0. **AGENTS.md §4.1** - Documentation standards
1. **AGENTS.md §9** - CI enforcement
2. [NumPy Docstring Guide](https://numpydoc.readthedocs.io/en/latest/format.html)
3. Example: `src/numistalib/services/catalogues/service.py`
