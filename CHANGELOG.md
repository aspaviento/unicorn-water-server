# Changelog

## [1.0.0] - 2026-10-25

First tagged release of Unicorn Water Server, collecting the functionality
developed since the initial public source publication on 2026-06-18.

### Included

- Native 17x7 Unicorn HAT Mini water-consumption display with animated bucket
  fill and three-digit litre readings.
- Overflow handling: values above 999 retain their actual API value while the
  display shows red 999 digits and status reports the overflow.
- Compact pH and ORP indicators with ok, warning, and critical states, updated
  through `/api/pool` without changing the current display mode.
- React control panel with matrix preview and API documentation.
- Startup rainbow, full pixel-off control, and a distinct idempotent standby
  mode showing a dim clock. Water updates resume the water display.
- Status and endpoint-discovery APIs, plus Home Assistant REST and dashboard
  examples covering water, pool indicators, and standby.
- Raspberry Pi installation with an isolated Python runtime, configurable
  service user and paths, systemd assets, and deployment-copy update guidance.
- Hardware-free dummy mode, backend tests, and frontend build checks in CI.
- Security policy and private vulnerability reporting.

### Compatibility and upgrading

This release labels the existing functionality; it introduces no API or display
behavior changes relative to the preceding main-branch commit. The private
frontend package metadata is aligned with version 1.0.0.

Publishing a release does not deploy it to an existing installation. Follow the
README deployment guidance to update runtime files deliberately, and restart
the service when updating server code, dependencies, or its systemd unit.

[1.0.0]: https://github.com/aspaviento/unicorn-water-server/releases/tag/v1.0.0
