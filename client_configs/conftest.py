default_label_set = {"unit-test", "automated-test"}


# see https://docs.getxray.app/display/XRAYCLOUD/Taking+advantage+of+JUnit+XML+reports
# as well as https://docs.pytest.org/en/6.2.x/reference.html#collection-hooks
def pytest_collection_modifyitems(session, config, items):
    """Iterate over markers and add properties."""
    for item in items:
        jira_issues_set = set()

        for marker in item.iter_markers(name="requirements"):
            jira_issues_set.update(req.strip() for req in marker.args[0].split(","))

        for marker in item.iter_markers(name="specifications"):
            jira_issues_set.update(spec.strip() for spec in marker.args[0].split(","))

        if jira_issues_set:
            jira_issues = ",".join(jira_issues_set)
            item.user_properties.append(("requirements", jira_issues))

        for marker in item.iter_markers(name="labels"):
            default_label_set.update(marker.args[0].split(","))

        if default_label_set:
            labels = ",".join(default_label_set)
            item.user_properties.append(("tags", labels))

        for marker in item.iter_markers(name="description"):
            item.user_properties.append(("test_description", marker.args[0]))
