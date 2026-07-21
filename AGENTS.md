# Agent Guidance

## Project Scope

This repository is the public source for Unicorn Water Server: a Flask/Vite
service that displays domestic water consumption and compact pool chemistry
indicators on a Pimoroni Unicorn HAT Mini.

The project is derived from `unicorn-solar-server`, which is derived from
`unicorn-busy-server`. It reuses the same general service shape while replacing
solar behavior with water and pool-status APIs.

## Repository Layout

- `server.py`: Flask API and display behavior.
- `lib/unicorn_wrapper.py`: hardware and dummy display wrapper.
- `test_server.py`: backend unit tests.
- `frontend/`: Vite/React control panel.
- `docs/`: public integration documentation.
- `install.sh`, `start.sh`, `unicorn-water.service`: public install and service
  assets.

## Local Validation

Use the project README as the primary source for setup. Before committing code
changes, run the relevant checks:

```bash
python3 -m venv .venv
.venv/bin/python -m pip install flask flask-cors jsmin
.venv/bin/python -m unittest -v
```

For frontend changes:

```bash
cd frontend
npm ci
npm run build
```

## Operating Rules

- Keep this repository public-safe. Do not add private hostnames, private paths,
  tokens, cron entries, local network details, or home deployment notes.
- Do not assume the service is currently deployed or running anywhere. Verify
  live deployment state outside this public repository before operational work.
- Keep private operation notes in a private location outside this repo.
- Preserve the public service identity documented here: `unicorn-water.service`
  and default HTTP port `9002`.
- Only one Unicorn HAT Mini service should control the hardware at a time; keep
  service-conflict behavior explicit when changing install or systemd files.
- The native display target is a 17x7 Unicorn HAT Mini layout. Do not silently
  change dimensions, rotation, overflow behavior, or display assumptions.
- The public API is intentionally focused on water, pool indicators, rainbow,
  status, discovery, and off behavior. Do not reintroduce solar tariff, solar
  battery, or busy-presence endpoints unless explicitly requested.

## Change Expectations

- Keep API changes backward-compatible unless the user explicitly asks for a
  breaking change.
- Update README or public docs when public API, install behavior, or display
  behavior changes.
- For deployment-sensitive changes, propose and validate locally first; do not
  restart remote services or change private cron jobs from this repo context
  without explicit live-operation instructions.
