# Version Bumping Guide

Quick reference for managing project versions in `chemz` using `bump-my-version`.

---

## Commands Cheat Sheet

All commands can be run with `uvx` without global installation:

### 1. Patch Release (`0.1.0` ➔ `0.1.1`)

For bug fixes, small tweaks, and hotfixes:

```bash
uvx bump-my-version bump patch
```

### 2. Minor Release (`0.1.0` ➔ `0.2.0`)

For new features, format handlers, or API extensions:

```bash
uvx bump-my-version bump minor
```

### 3. Major Release (`0.1.0` ➔ `1.0.0`)

For major milestones, breaking changes, or stable public releases:

```bash
uvx bump-my-version bump major
```

---

## Custom Tag Messages (Release Names)

You can pass a custom release message directly to the tag:

```bash
uvx bump-my-version bump minor --tag-message "Release 0.2.0"
```

---

## Preview Before Applying (Dry Run)

To see what files will change without modifying anything:

```bash
uvx bump-my-version bump minor --dry-run --verbose
```

---

## Publishing the Release

Once the version is bumped, push the commit along with the new Git tag to trigger the automated CI/CD PyPI build, GitHub release, and changelog generation:

```bash
git push --follow-tags
```

---

## Files Synchronized Automatically

- [`pyproject.toml`](../pyproject.toml) (`version = "..."`)
- [`src/chemz/__init__.py`](../src/chemz/__init__.py) (`__version__ = "..."`)
- [`uv.lock`](../uv.lock) (`version = "..."`)
- [`.bumpversion.toml`](../.bumpversion.toml) (`current_version = "..."`)
