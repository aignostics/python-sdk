"""Dummy nav builder for integration testing of plugin GUI page registration."""

from aignostics.utils import BaseNavBuilder, NavItem


class DummyPluginNavBuilder(BaseNavBuilder):
    """Dummy navigation builder exposed by the dummy plugin for integration testing."""

    @staticmethod
    def get_nav_name() -> str:
        """Return the nav group name."""
        return "Dummy Plugin"

    @staticmethod
    def get_nav_items() -> list[NavItem]:
        """Return dummy navigation items."""
        return [NavItem(icon="extension", label="Dummy Page", target="/dummy-plugin")]
