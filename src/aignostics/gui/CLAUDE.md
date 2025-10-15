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
- `_error.py` - Error page handling (`ErrorPageBuilder`)

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

- `HEALTH_UPDATE_INTERVAL` - Configurable health check frequency
- Real-time service status display in UI
- Centralized health aggregation and reporting

**Error Handling:**

- Standardized error page layout
- User-friendly error messages
- Recovery guidance and troubleshooting tips
