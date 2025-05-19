"""Tests for the utility functions used in the client resources modules.

This module contains unit tests for the utility functions, particularly focusing
on pagination functionality that is used across resource modules.
"""

from unittest.mock import Mock

from aignostics.platform.resources.utils import PAGE_SIZE, paginate


def test_paginate_stops_when_results_less_than_page_size() -> None:
    """Test that paginate stops yielding when a page has fewer items than the page size.

    This test verifies that the paginate function correctly stops requesting new pages
    when a response contains fewer items than the page size, indicating it's the last page.
    """
    # Arrange
    mock_func = Mock()
    # First call returns full page, second call returns partial page
    mock_func.side_effect = [
        [f"item_{i}" for i in range(PAGE_SIZE)],  # Full page
        [f"item_{i + PAGE_SIZE}" for i in range(5)],  # Partial page (5 items)
    ]

    # Act
    results = list(paginate(mock_func))

    # Assert
    assert len(results) == PAGE_SIZE + 5
    assert mock_func.call_count == 2
    # Check first call
    mock_func.assert_any_call(page=1, page_size=PAGE_SIZE)
    # Check second call
    mock_func.assert_any_call(page=2, page_size=PAGE_SIZE)


def test_paginate_handles_empty_first_page() -> None:
    """Test that paginate handles an empty first page correctly.

    This test verifies that the paginate function correctly handles the case where
    the first page of results is empty, and doesn't make additional API requests.
    """
    # Arrange
    mock_func = Mock(return_value=[])

    # Act
    results = list(paginate(mock_func))

    # Assert
    assert len(results) == 0
    mock_func.assert_called_once_with(page=1, page_size=PAGE_SIZE)


def test_paginate_passes_additional_arguments() -> None:
    """Test that paginate correctly passes additional arguments to the function.

    This test verifies that the paginate function correctly forwards both positional
    and keyword arguments to the paginated function.
    """
    # Arrange
    mock_func = Mock(return_value=[])
    additional_arg = "test"
    additional_kwarg = {"key": "value"}

    # Act
    # Use a keyword argument for page_size to avoid confusion with positional args
    list(paginate(mock_func, *[additional_arg], keyword=additional_kwarg))

    # Assert
    mock_func.assert_called_once_with(additional_arg, keyword=additional_kwarg, page=1, page_size=PAGE_SIZE)


def test_paginate_custom_page_size() -> None:
    """Test that paginate correctly uses custom page size.

    This test verifies that the paginate function correctly uses a custom page size
    when provided and passes it to the wrapped function.
    """
    # Arrange
    mock_func = Mock(return_value=[])
    custom_page_size = 50

    # Act
    list(paginate(mock_func, page_size=custom_page_size))

    # Assert
    mock_func.assert_called_once_with(page=1, page_size=custom_page_size)


def test_paginate_multiple_pages() -> None:
    """Test that paginate correctly iterates through multiple pages.

    This test verifies that the paginate function correctly requests and yields
    items from multiple pages in sequence, until reaching a page with fewer items
    than the page size.
    """
    # Arrange
    mock_func = Mock()
    # Three pages of results, each with PAGE_SIZE items
    mock_func.side_effect = [
        [f"page1_item_{i}" for i in range(PAGE_SIZE)],
        [f"page2_item_{i}" for i in range(PAGE_SIZE)],
        [f"page3_item_{i}" for i in range(5)],  # Last page with fewer items
    ]

    # Act
    results = list(paginate(mock_func))

    # Assert
    assert len(results) == 2 * PAGE_SIZE + 5
    assert mock_func.call_count == 3

    # Verify items are yielded in correct order
    assert results[0] == "page1_item_0"
    assert results[PAGE_SIZE] == "page2_item_0"
    assert results[2 * PAGE_SIZE] == "page3_item_0"
