# Security policy

## Supported versions

Security fixes target the latest published release of Unicorn Water Server.
At publication of this policy, that release is **v1.0.0**. Older releases do
not receive separate security backports. Reports affecting development code
are welcome; reproduce against the latest release where practical.

This is a community-maintained project. Response and remediation times depend
on maintainer availability; no response deadline or support SLA is promised.

## Reporting a vulnerability

Use GitHub's private vulnerability reporting form:

[Report a vulnerability privately](https://github.com/aspaviento/unicorn-water-server/security/advisories/new)

You can also find it under **Security and quality > Advisories > Report a
vulnerability**. Do not open a public issue containing exploit details,
credentials, private addresses, or household configuration.

Include the affected version or commit, reproduction steps, expected and
observed behavior, and potential impact. Use synthetic examples and redact
tokens, personal information, and private network details. Coordinate
disclosure with the maintainer while the report is assessed. Report ordinary
bugs and feature requests through public issues.

## Deployment expectations

The service is intended for a trusted local environment. Its web panel and
HTTP API can change the physical display; the application does not provide
built-in authentication, authorization, or TLS. Do not expose it directly to
the public internet or grant untrusted clients access. Use appropriate network
access controls and, when needed, an access-controlled reverse proxy.

Keep provider credentials and real payloads in private configuration outside
the source repository. Generic examples and dummy mode are intended for
development and demonstration; they are not a security boundary.
