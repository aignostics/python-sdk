---
itemId: SWR-SYSTEM-GUI-STATUS-PAGE-1
itemTitle: Per-Environment Betterstack Status Page in Launchpad
itemHasParent: SHR-SYSTEM-1
itemType: Requirement
Requirement type: FUNCTIONAL
Module: System
Layer: GUI
---

As a Launchpad user, I expect the embedded Betterstack status badge and the "Check Platform Status" link to reflect only the Aignostics Platform environment my Launchpad is connected to (as configured by `AIGNOSTICS_API_ROOT`), so that I can assess the operational health of the services I actually depend on without being distracted by, or misled by, the health of unrelated environments.

The Launchpad shall resolve the public Betterstack status page URL from the configured platform environment as follows:

- when connected to the production environment (`AIGNOSTICS_API_ROOT` = `https://platform.aignostics.com`), the Launchpad shall embed the badge of, and link to, `https://status.platform.aignostics.com`;
- when connected to the staging environment (`AIGNOSTICS_API_ROOT` = `https://platform-staging.aignostics.com`), the Launchpad shall embed the badge of, and link to, `https://status.platform-staging.aignostics.com`;
- when connected to a dev or test environment, or to any other environment for which no per-environment public Betterstack status page is configured, the Launchpad shall not render the Betterstack badge in its footer and shall not render the "Check Platform Status" item in its right-side menu.

The user shall be able to override the resolved status page URL through the `AIGNOSTICS_STATUS_PAGE_URL` environment variable or the equivalent constructor argument, including overriding it to an empty value to suppress the badge and link.

The Launchpad shall validate any user-supplied status page URL at configuration time and reject values that are not well-formed http(s) URLs or that contain characters that could break out of an HTML attribute when rendered (`"`, `'`, `<`, `>`, backtick, backslash, whitespace), so that the Launchpad cannot be tricked into rendering attacker-controlled markup through this configuration.

When the Launchpad does not render the badge or the menu link, no degraded-state placeholder is shown — both surfaces are simply omitted from the layout.
