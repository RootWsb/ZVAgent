# Project Structure

This repository intentionally keeps source code, built-in assets, runtime state,
and experiments in separate places. Use this as the placement rule before adding
new files.

## Source Code

- `agent/` - Agent services, protocols, tools, memory, reports, and skill logic.
- `bridge/` - Adapters between chat channels and the agent runtime.
- `channel/` - Chat and web channel implementations plus static web assets.
- `cli/` - Command line entry points and CLI commands.
- `common/` - Shared utilities, logging, quotas, config helpers, and primitives.
- `models/` - Model provider integrations.
- `plugins/` - Built-in plugins that are part of the repo.
- `translate/` - Translation providers.
- `voice/` - ASR, TTS, and voice provider integrations.

## Product Assets

- `skills/` - Built-in skills shipped with the project. Runtime-customized skills
  should live in `agent_workspace`, not here.
- `docs/` - Project documentation and documentation images.
- `docker/` - Container build and compose files.
- `scripts/` - Developer and operations scripts.
- `tests/` - Automated tests.

## Runtime State

The following are local runtime outputs and should not be committed:

- `config.json`, `config.yaml`
- `workspace/`
- `data/`
- `logs/`, `*.log`
- `user_datas.pkl`
- `~/` under the project root

`agent_workspace` defaults to `~/zvagent`. On Windows, prefer an absolute path in
`config.json`, such as `D:/tmp/zvagent-workspace`, so runtime data does not get
created under the repository by accident.

## Experiments And Training

Keep reusable training code under `training/`, but keep large or generated
training artifacts out of source control:

- `training/**/checkpoints/`
- `training/**/comparison_report/`
- `training/**/plots/`
- `training/**/*.errors.log`

Small seed datasets, scripts, and README files may stay under `training/` when
they are required to reproduce the experiment.

## Generated Files

Remove these when tidying the tree:

- `__pycache__/`, `**/__pycache__/`
- `.pytest_cache/`
- `*.pyc`, `*.pyo`, `*.pyd`
- `*.egg-info/`

Use `scripts/clean_workspace.ps1 -DryRun` to preview a cleanup before deleting
anything.
