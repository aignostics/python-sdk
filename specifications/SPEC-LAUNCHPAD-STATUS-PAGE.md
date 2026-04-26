---
itemId: SPEC-LAUNCHPAD-STATUS-PAGE
itemTitle: Per-Environment Betterstack Status Page in Launchpad
itemType: Software Item Spec
itemFulfills: SWR-SYSTEM-GUI-STATUS-PAGE-1
itemIsRelatedTo: SPEC_GUI_SERVICE, SPEC_PLATFORM_SERVICE, SPEC_SYSTEM_SERVICE
Module: System
Layer: GUI / Platform Service
Version: 1.0.0
Date: 2026-04-26
---

## 1. Description

### 1.1 Purpose

This specification describes how the Aignostics Launchpad (Desktop Application, NiceGUI-based) renders the embedded Betterstack status badge in its footer and the "Check Platform Status" link in its right-side menu so that both reflect only the Aignostics Platform environment the Launchpad is currently connected to (i.e., the environment selected by `AIGNOSTICS_API_ROOT`).

The motivation is that the legacy aggregate page at `https://status.aignostics.com` covers production *and* staging *and* unrelated services (Console, Portal, Career Site, Website). A user running the Launchpad against a single environment is best served by the corresponding **narrower** Betterstack property of that same environment, with no badge or link rendered when no per-environment Betterstack property exists (dev, test, or unknown environments).

### 1.2 Functional Requirements

The Launchpad shall:

- **[FR-01]** Resolve the public Betterstack status page URL from the configured `api_root` of the platform `Settings` model.
- **[FR-02]** Use `https://status.platform.aignostics.com` for production (`https://platform.aignostics.com`) and `https://status.platform-staging.aignostics.com` for staging (`https://platform-staging.aignostics.com`).
- **[FR-03]** Use `None` (i.e., no public per-environment status page) for the dev environment (`https://platform-dev.aignostics.ai`) and the test environment (`https://platform-test.aignostics.ai`), and for any unknown `api_root` whose auth fields are otherwise fully provided.
- **[FR-04]** Allow the user to override the resolved value through the `AIGNOSTICS_STATUS_PAGE_URL` environment variable or the `status_page_url` constructor argument of `Settings`. An empty string is treated as `None`.
- **[FR-05]** Validate the resolved value at `Settings` construction time, rejecting values that are not well-formed http(s) URLs and values that contain `"`, `'`, `<`, `>`, backtick, backslash, or whitespace characters.
- **[FR-06]** When the resolved value is non-`None`, render the Betterstack badge in the footer (as a 250×30 iframe pointing at `<status_page_url>/badge?theme=dark`) and a "Check Platform Status" link in the right-side menu pointing at `<status_page_url>`.
- **[FR-07]** When the resolved value is `None`, omit the Betterstack badge from the footer and omit the "Check Platform Status" item from the right-side menu — no degraded-state placeholder is rendered.
- **[FR-08]** Refresh the Betterstack iframe every 30 seconds (in alignment with the existing health-update interval), guarded so the refresh is a safe no-op when the iframe is absent from the DOM.

### 1.3 Non-Functional Requirements

- **Security**: User-controlled values must not be able to inject markup into the Launchpad webview. Defence-in-depth: (1) `Settings.status_page_url` is validated by `_validate_optional_url` before reaching the GUI layer; (2) the iframe is rendered via NiceGUI's `ui.element('iframe')` with attributes assigned through the props dict, so attribute values flow through Vue data binding rather than raw HTML construction.
- **Backwards compatibility**: An unknown `api_root` (with all auth fields provided) must produce a safe default (`None`, no badge, no link) rather than raising an error. The aggregate `https://status.aignostics.com` page must remain unchanged and reachable for users who navigate to it directly.
- **Resilience**: The 30-second iframe-refresh JS must remain safe when the iframe is absent from the DOM (dev/test or override-to-`None` cases). The behaviour shall not depend on the order in which the timer first fires relative to first DOM mount.

### 1.4 Constraints and Limitations

- The dev and test environments do not currently have a dedicated public Betterstack property; this specification deliberately treats that as a "no badge, no link" state, not an error.
- The `Settings` `pre_init` model validator returns early when all auth fields are explicitly provided. In that path, the per-environment match block is skipped, and `status_page_url` retains its declared default (`None`) unless the caller supplied it explicitly.

---

## 2. Architecture and Design

### 2.1 Files Touched

| File | Role |
| --- | --- |
| `src/aignostics/platform/_constants.py` | Per-environment URL constants `STATUS_PAGE_URL_DEV`, `STATUS_PAGE_URL_TEST`, `STATUS_PAGE_URL_STAGING`, `STATUS_PAGE_URL_PRODUCTION`. |
| `src/aignostics/platform/_settings.py` | `Settings.status_page_url: str \| None` field with `BeforeValidator(_validate_optional_url)`; resolution inside the existing `pre_init` `match...case` block alongside the auth endpoints; helper `_validate_optional_url(value: str \| None) -> str \| None`. |
| `src/aignostics/platform/__init__.py` | Re-exports the four `STATUS_PAGE_URL_*` constants for downstream consumers. |
| `src/aignostics/gui/_frame.py` | Reads `settings().status_page_url` once after the context manager `yield`. Conditionally renders the right-menu "Check Platform Status" item, the footer iframe, and the 30-s refresh JS based on this value. Defensive JS element guard `if (iframe) { iframe.src = iframe.src; }` so the refresh never throws when the iframe is absent. |
| `tests/aignostics/platform/settings_test.py` | Per-environment assertions on `status_page_url` and parametrised rejection of invalid/unsafe URLs. |

### 2.2 Resolution Algorithm

```text
input:  api_root (string), explicit overrides (env var, constructor argument)
output: status_page_url: str | None

1. If the user provided `status_page_url` explicitly (constructor arg or
   `AIGNOSTICS_STATUS_PAGE_URL` env var):
     → run `_validate_optional_url`; on success use that value.
2. Else, in the existing `pre_init` `match...case`:
     - api_root == API_ROOT_DEV         → setdefault to STATUS_PAGE_URL_DEV (None)
     - api_root == API_ROOT_TEST        → setdefault to STATUS_PAGE_URL_TEST (None)
     - api_root == API_ROOT_STAGING     → setdefault to STATUS_PAGE_URL_STAGING
     - api_root == API_ROOT_PRODUCTION  → setdefault to STATUS_PAGE_URL_PRODUCTION
     - any other api_root with all auth fields supplied:
                                         → field default applies (None)
     - any other api_root without auth fields:
                                         → ValueError UNKNOWN_ENDPOINT_URL
```

### 2.3 Validation

`_validate_optional_url(value: str | None) -> str | None` is registered as a Pydantic `BeforeValidator` on the field:

1. `None` → `None`.
2. `""` → `None` (env-var loaders may produce an empty string when the variable is set but empty; treating it as `None` matches the dev/test default).
3. Non-empty string:
   1. Reject if it contains any of `"`, `'`, `<`, `>`, backtick, backslash, or whitespace (RFC 3986 requires those to be percent-encoded; raw forms are either malformed or an injection attempt).
   2. Otherwise, delegate to the existing `_validate_url` (scheme must be `http` or `https`; netloc must be non-empty).

### 2.4 Rendering

In `gui/_frame.py`:

```python
status_page_url = settings().status_page_url   # resolved once, reused

if status_page_url:
    # right-menu: "Check Platform Status" item with ui.link(...)

if status_page_url:
    # footer: NiceGUI iframe element, attributes via props dict (no raw HTML)
    iframe = ui.element("iframe")
    iframe.props["id"] = "betterstack"
    iframe.props["src"] = urljoin(status_page_url + "/", "badge?theme=dark")
    iframe.props["width"] = "250"
    iframe.props["height"] = "30"
    iframe.props["frameborder"] = "0"
    iframe.props["scrolling"] = "no"
    iframe.style("color-scheme: dark; margin-left: 0px;")

# 30-s refresh, runs unconditionally; element existence is guarded in JS.
ui.run_javascript(
    "var iframe = document.getElementById('betterstack');"
    "if (iframe) { iframe.src = iframe.src; }"
)
```

The iframe is rendered as a NiceGUI `ui.element('iframe')` rather than `ui.html('<iframe …>', sanitize=False)` so attribute values are set via Vue data binding, eliminating the raw-HTML interpolation pattern that previously existed in this code path.

---

## 3. Inputs and Outputs

### 3.1 Inputs

| Input | Source | Type | Validation | Effect |
| --- | --- | --- | --- | --- |
| `api_root` | constructor arg / `AIGNOSTICS_API_ROOT` env var | str | http(s) URL | Selects the per-environment default for `status_page_url`. |
| `status_page_url` | constructor arg / `AIGNOSTICS_STATUS_PAGE_URL` env var | str \| None | `_validate_optional_url`: None / "" / valid http(s) URL with no HTML-breaking chars | Overrides the per-environment default. Empty / None → no badge + no menu link. |

### 3.2 Outputs

| Output | Surface | Condition |
| --- | --- | --- |
| Betterstack iframe (`<iframe id="betterstack" src="…/badge?theme=dark" …>`) | Launchpad footer | `status_page_url` is non-`None`. |
| "Check Platform Status" right-menu item linking to `status_page_url` | Right-side hamburger menu | `status_page_url` is non-`None`. |
| (nothing) | both surfaces | `status_page_url` is `None`. |

---

## 4. Verification

### 4.1 Automated Tests

Located in `tests/aignostics/platform/settings_test.py`:

- `test_authentication_settings_production` / `_staging` / `_dev` / `_test` — assert the per-environment `status_page_url` value.
- `test_status_page_url_env_override_takes_precedence` — `AIGNOSTICS_STATUS_PAGE_URL` overrides the production default.
- `test_status_page_url_explicit_argument_overrides_default` — constructor arg overrides the default.
- `test_status_page_url_explicit_none_argument` — explicit `None` is preserved.
- `test_status_page_url_empty_string_coerced_to_none` — empty env-var coerces to `None`.
- `test_status_page_url_unknown_api_root_with_full_auth_defaults_to_none` — unknown api_root + all auth fields supplied → `None`.
- `test_status_page_url_rejects_invalid_or_unsafe[…]` — parametrised rejection of 13 inputs covering non-http(s) schemes (incl. `javascript:`, `file:`, `ftp://`), missing scheme/netloc, quotes, angle brackets, whitespace, backtick, backslash, newline, tab.

### 4.2 Manual Verification (smoke)

Run `aignostics system serve` on three ports with the corresponding `AIGNOSTICS_API_ROOT` and inspect the live DOM:

| Environment | Iframe `src` | Menu link `href` |
| --- | --- | --- |
| production (`https://platform.aignostics.com`) | `https://status.platform.aignostics.com/badge?theme=dark` | `https://status.platform.aignostics.com` |
| staging (`https://platform-staging.aignostics.com`) | `https://status.platform-staging.aignostics.com/badge?theme=dark` | `https://status.platform-staging.aignostics.com` |
| dev (`https://platform-dev.aignostics.ai`) | iframe absent in DOM | menu item absent in DOM |

---

## 5. Dependencies and Integration

### 5.1 Internal

| Module | Role |
| --- | --- |
| `platform` ([SPEC_PLATFORM_SERVICE](SPEC_PLATFORM_SERVICE.md)) | Owns the `Settings` model, the per-environment auth/URL constants, the `_validate_optional_url` helper, and the `pre_init` model validator. |
| `gui` ([SPEC_GUI_SERVICE](SPEC_GUI_SERVICE.md)) | Owns `gui/_frame.py` and is responsible for the conditional rendering of the menu link and the footer iframe. |
| `system` ([SPEC_SYSTEM_SERVICE](SPEC_SYSTEM_SERVICE.md)) | Owns the existing health-update interval (`HEALTH_UPDATE_INTERVAL`) and the broader operational-health surface that this specification extends. |

### 5.2 External

| Dependency | Purpose | Notes |
| --- | --- | --- |
| Better Stack (status pages) | Hosts the per-environment status pages and renders the embedded badge. | Property URLs are stable per-environment; failure to render the iframe is a Betterstack-side outage and is out of scope for this specification (it would be visible as a missing badge area in the footer). |
| NiceGUI | Renders the `ui.element('iframe')` and the right-menu items. | Attribute escaping via Vue data binding is relied upon as the second layer of defence after `_validate_optional_url`. |

---

## 6. Out of Scope

- Replacing the Betterstack iframe with a native NiceGUI / Quasar component.
- Adding a per-environment public Betterstack property for dev or test.
- Repointing the legacy aggregate page at `https://status.aignostics.com` (the aggregate remains unchanged and continues to serve users who navigate to it directly).
- API endpoints to query the platform's status programmatically (covered by `Service.health()` in `SPEC_PLATFORM_SERVICE`).

---

*This specification was authored alongside [PYSDK-107](https://aignx.atlassian.net/browse/PYSDK-107) / PR #599 and supersedes the implementation initially proposed in PR #434.*
