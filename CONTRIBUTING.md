# Contributing / Git Workflow

**Git Workflow & Management**.
Follow this for every change, not just at the end.

## Branch naming

- `feature/<short-name>` — new functionality (e.g. `feature/waitlist`, `feature/fine-calculation`)
- `bugfix/<short-name>` — fixing something broken (e.g. `bugfix/duplicate-user-id`)
- `chore/<short-name>` — non-feature work: docs, config, cleanup (e.g. `chore/update-readme`)

Never commit directly to `main`. Every change goes through a branch and a PR.

## Commit messages

Prefix every commit with what kind of change it is:

- `feat: add waitlist queue to LibraryService`
- `fix: prevent duplicate user ids across processes`
- `test: add coverage for tiered fine calculation`
- `chore: update README setup instructions`

Keep the first line under ~70 characters. Add detail in the body if the change needs it.

## Pull requests

1. Push your branch, open a PR against `main`.
2. Fill out the PR template (auto-loads from `.github/PULL_REQUEST_TEMPLATE.md`).
3. At least one other teammate reviews and approves before merge.
4. Run `pytest` locally before opening the PR — a PR with failing tests should not
   be opened, let alone merged.
5. Squash or clean up commit history on merge so `main`'s log stays readable.

## Before you start work each day

```bash
git checkout main
git pull
git checkout -b feature/your-thing
```

## Test-Driven Development contract

Because we're doing TDD, a function's **name, arguments, return value, and what it
raises** are a contract the whole team agrees on before either the test or the
implementation is written. If you need to change a function's signature after
Victor has already written a test against it, say so in the team channel before
changing it — otherwise the test breaks for a reason that has nothing to do with
a real bug.


