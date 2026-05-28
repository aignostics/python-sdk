"""Navigation infrastructure for NiceGUI sidebar.

This module provides:
- NavItem: Individual navigation item dataclass
- NavGroup: Group of navigation items
- BaseNavBuilder: Abstract base class for module navigation builders
- gui_get_nav_groups: Collect and sort navigation groups from all NavBuilders
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass, field

from ._di import locate_subclasses


@dataclass
class NavItem:
    """Navigation item for sidebar.

    Attributes:
        icon: Material icon name (e.g., 'waving_hand', 'settings').
        label: Display label for the navigation item.
        target: URL path or external URL for the link.
        marker: Test marker for the item. Auto-generated from label if None.
        new_tab: Whether to open the link in a new tab. Defaults to False (same tab).
    """

    icon: str
    label: str
    target: str
    marker: str | None = None
    new_tab: bool = False

    def __post_init__(self) -> None:
        """Auto-generate marker from label if not provided."""
        if self.marker is None:
            # Convert label to SCREAMING_SNAKE_CASE marker
            self.marker = "LINK_" + self.label.upper().replace(" ", "_").replace("(", "").replace(")", "")


@dataclass
class NavGroup:
    """Group of navigation items from a NavBuilder.

    Used internally for rendering navigation in the sidebar.
    """

    name: str
    icon: str = "folder"
    items: list[NavItem] = field(default_factory=list)
    position: int = 1000
    use_expansion: bool = True


class BaseNavBuilder(ABC):
    """Base class for navigation builders.

    Each module should have ONE NavBuilder that defines its navigation items.
    NavBuilders are auto-discovered and used to populate the sidebar.

    Example:
        class NavBuilder(BaseNavBuilder):
            @staticmethod
            def get_nav_name() -> str:
                return "My Module"

            @staticmethod
            def get_nav_items() -> list[NavItem]:
                return [
                    NavItem(icon="home", label="Home", target="/my-module"),
                    NavItem(icon="settings", label="Settings", target="/my-module/settings"),
                ]

            @staticmethod
            def get_nav_position() -> int:
                return 200  # Lower = higher in sidebar
    """

    @staticmethod
    @abstractmethod
    def get_nav_name() -> str:
        """Return the display name for this module's navigation group.

        Returns:
            str: Display name shown in sidebar (e.g., 'Hello World', 'System').
        """

    @staticmethod
    @abstractmethod
    def get_nav_items() -> list[NavItem]:
        """Return navigation items for the sidebar.

        Items are rendered in list order within the module's group.

        Returns:
            list[NavItem]: Navigation items for this module.
        """

    @staticmethod
    def get_nav_position() -> int:
        """Return position in sidebar (lower = higher).

        Convention:
            - 100-199: Core demo/example pages
            - 200-499: Feature modules
            - 500-799: Default (unspecified)
            - 800-899: System/admin pages
            - 900-999: External links (API docs, status, repo)

        Returns:
            int: Position value. Defaults to 1000.
        """
        return 1000

    @staticmethod
    def get_nav_icon() -> str:
        """Return the icon for the navigation group expansion panel.

        Uses Material Icons names. See: https://fonts.google.com/icons

        Returns:
            str: Material icon name. Defaults to 'folder'.
        """
        return "folder"

    @staticmethod
    def get_nav_use_expansion() -> bool:
        """Return whether to render items in an expansion panel.

        If True, items are grouped in a collapsible expansion with get_nav_name().
        If False, items are rendered flat without grouping.

        Returns:
            bool: Use expansion panel. Defaults to True.
        """
        return True


def gui_get_nav_groups() -> list[NavGroup]:
    """Collect navigation groups from all NavBuilders.

    Returns:
        list[NavGroup]: Navigation groups sorted by position.
    """
    nav_builders = locate_subclasses(BaseNavBuilder)
    groups: list[NavGroup] = []

    for nav_builder in nav_builders:
        items = nav_builder.get_nav_items()
        if items:  # Only include builders with nav items
            groups.append(
                NavGroup(
                    name=nav_builder.get_nav_name(),
                    icon=nav_builder.get_nav_icon(),
                    items=items,
                    position=nav_builder.get_nav_position(),
                    use_expansion=nav_builder.get_nav_use_expansion(),
                )
            )

    # Sort by position (lower = higher in sidebar)
    return sorted(groups, key=lambda g: g.position)
