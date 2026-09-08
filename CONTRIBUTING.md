# Contributing

Use a branch and pull request. Install the pinned requirements, run `python -m pytest -q`, `ruff check .` and `ruff format --check .`, and include regression tests for fixes. Use synthetic fixtures only. Do not include credentials, personal correspondence or customer data. Dependencies and Actions updates require the same checks as code changes. CI uses GitHub-hosted runners; no runner is installed on the production host.

Releases are optional source snapshots. The manual release workflow runs CI first and creates a **draft** release of the tested commit. Review the draft and checksums before publishing; release execution is not needed to run these examples.

After activating the development environment, enable local pre-commit and pre-push gates with `git config core.hooksPath .githooks`. Do not bypass hooks. Server-side required checks apply even when hooks are not installed.
