# CLAUDE.md - GUI Module

This file provides guidance to Claude Code when working with the `gui` module in this repository.

## Module Overview

The gui module provides common GUI framework components and theming for the Aignostics Desktop Launchpad:

- **Shared UI Framework**: Common layouts, themes, and components
- **Error Handling**: Standardized error page components
- **Health Monitoring**: Real-time service health display
- **Responsive Design**: Cross-platform desktop application interface

## Key Components

**Core Framework:**

- `_theme.py` - Application theme and styling (`PageBuilder`, `theme`)
- `_frame.py` - Common layout components and health updates
- `_error.py` - Error page handling (in-file class `PageBuilder`, imported as `ErrorPageBuilder`)

**Usage Pattern:**

- Provides shared `PageBuilder` class for module auto-discovery
- Conditional import based on NiceGUI availability
- Health update intervals and monitoring infrastructure

## Integration Notes

**Module Pattern:**

- Each module's GUI components inherit from this base framework
- Consistent theming and layout across all modules
- Auto-discovery pattern for PageBuilder classes

**Health Monitoring:**

- `HEALTH_UPDATE_INTERVAL` - Configurable health check frequency (default: 30 seconds)
- `USERINFO_UPDATE_INTERVAL` - User info refresh interval (default: 60 minutes)
- Real-time service status display in UI footer
- Centralized health aggregation and reporting via `SystemService.health_static()`

**Health Check Enforcement:**

The GUI enforces health checks before allowing critical operations:

- **Footer Health Indicator**: Shows "Launchpad is healthy" (green) or "Launchpad is unhealthy" (red)
- **Application Run Submission**: The "Next" button in the application workflow stepper is disabled when unhealthy
- **Tooltip Feedback**: Users see "System is unhealthy, you cannot prepare a run at this time."
- **Force Override**: Internal users (Aignostics, pre-alpha-org, LMU, Charite organizations) can enable a "Force (skip health check)" checkbox

**Health State Management (`_frame.py`):**

A `ui.timer` fires every `HEALTH_UPDATE_INTERVAL` seconds; the callback sets a
`launchpad_healthy: bool | None` state (`None` while loading) from
`await SystemService.health_static()` and refreshes the display components.
Health-enforcement semantics are owned by `system/CLAUDE.md` — see it for details.

**Health Display Components:**

- `health_icon()` - Settings menu icon (green check or red error)
- `health_link()` - Footer link with status text and icon

**Error Handling:**

- Standardized error page layout
- User-friendly error messages
- Recovery guidance and troubleshooting tips
