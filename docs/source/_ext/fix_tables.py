"""Sphinx extension to fix table structures for LaTeX output.

This extension ensures that all table nodes have tbody children before
LaTeX processing, preventing StopIteration errors during table rendering.
"""

from docutils import nodes
from docutils.transforms import Transform
from sphinx.application import Sphinx


class EnsureTableBodies(Transform):
    """Transform to ensure all tables have tbody elements."""

    # Run with high priority (lower number = earlier) to execute before LaTeX transforms
    default_priority = 100

    def apply(self) -> None:
        """Apply the transformation to the document."""
        for table in self.document.findall(nodes.table):
            # Check if table has a tgroup child
            tgroups = list(table.findall(nodes.tgroup))

            if not tgroups:
                continue

            for tgroup in tgroups:
                # Check if tgroup has tbody
                tbodies = list(tgroup.findall(nodes.tbody))

                if not tbodies:
                    # Check if there's a thead
                    theads = list(tgroup.findall(nodes.thead))

                    if theads and len(theads) > 0:
                        # thead exists but no tbody - add empty tbody for LaTeX builder
                        tbody = nodes.tbody()
                        tgroup.append(tbody)
                    else:
                        # No thead either - try moving rows
                        tbody = nodes.tbody()

                        # Move all row children to tbody
                        rows = [child for child in tgroup.children if isinstance(child, nodes.row)]

                        for row in rows:
                            tgroup.remove(row)
                            tbody.append(row)

                        # Append tbody to tgroup if it has rows
                        if len(tbody.children) > 0:
                            tgroup.append(tbody)


def setup(app: Sphinx) -> dict[str, bool | str]:
    """Setup the Sphinx extension.

    Args:
        app: Sphinx application instance

    Returns:
        Extension metadata
    """
    app.add_transform(EnsureTableBodies)

    return {
        "version": "1.0",
        "parallel_read_safe": True,
        "parallel_write_safe": True,
    }
