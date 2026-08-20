# Contributing

Conventions for this repository: branching, commit and PR format, and
what a change needs before it merges.

## Workflow

Trunk-based development. `main` is protected and always deployable;
work happens on short-lived branches that squash-merge back.

1. `git checkout main && git pull`
2. `git checkout -b type/issue-short-slug`
3. Make the change. Run locally before pushing:
   ```bash
   uv run ruff format .
   uv run ruff check .
   uv run pytest
   ```
4. `git push -u origin <branch>` and open a PR.
5. Address feedback in additional commits on the same branch.
6. Squash-merge once CI is green.

Branches are deleted after merge.

## Branch naming

`type/issue-short-slug`:

- `feat/1232-mlflow-training`
- `fix/473-em-dash-mojibake`
- `docs/2314-pr-review-sla`

## PR titles and commits

Both follow Conventional Commits with an issue reference:

```
type(#issue): short imperative description
```

Allowed types: `feat`, `fix`, `hotfix`, `docs`, `chore`, `test`,
`style`, `refactor`, `ci`.

Examples:

- `feat(#1232): add MLflow-logged training script`
- `fix(#473): correct em-dash mojibake in docs`
- `docs(#2314): document PR review SLA`

This is enforced, not just recommended — the `pr-title` workflow
rejects any PR whose title does not match the pattern, and the
`#issue` number is required.

`commitizen` is configured in `pyproject.toml` and wired into
pre-commit. Run `uv run cz commit` for guided commit creation.

## Branch protection on `main`

- Pull request required; no direct pushes.
- CI status checks must pass before merge (lint, tests, docs build,
  frontend build).
- Squash and merge is the merge strategy.
- Branches are deleted after merge.

## What CI checks

Every pull request runs:

- `ruff check` and `ruff format --check` across the repo
- `pytest` for `packages/cv-pipeline` and `apps/backend`, with coverage
  reported to Codecov
- `eslint`, the frontend test suite, and a production `next build`
- a Sphinx docs build

Install the pre-commit hooks to catch the lint failures before pushing:

```bash
uv run pre-commit install
```

## Self-review checklist

Before requesting review:

- [ ] PR title matches `type(#issue): description`
- [ ] All CI checks green
- [ ] Scoped to a single concern — no unrelated changes mixed in
- [ ] Tests added or updated for changed behaviour
- [ ] Docs updated if the change affects user-facing behaviour
- [ ] Description explains the why, links the issue, lists follow-ups
- [ ] No debug or temporary artifacts committed — no `response.json`,
      `tmp_*` dumps, training run outputs, or secrets

## What reviewers look for

- Logic is correct and edge cases are handled
- New behaviour has tests, and existing tests still pass
- Public functions and classes have Google-style docstrings
- No hardcoded values that belong in config or environment variables
- No data files, model weights, caches, or run artifacts committed
- Code passes ruff formatting and linting

## Code conventions

- Python 3.11, formatted with ruff at 88 columns, double quotes.
- Google-style docstrings on every public function and class, covering
  Args, Returns, and Raises.
- Type hints on all function signatures.
- `logging`, never `print`.
- Specific exceptions, never bare `except:`.
- Configuration through environment variables — no hardcoded paths,
  thresholds, model versions, or connection strings.
