Feature: TEST-SWR-DATASET-6-QUERY-AND-PREVIEW-DATASET-CONTENTS

  Background:
    Given user installed the Python SDK

  @tests:SWR-DATASET-6 @id:TEST-SWR-DATASET-6-CONTENT-QUERY
  Scenario: System enables dataset querying with result counting and dry-run capabilities
    When User executes dataset queries with dry-run options
    Then System should execute queries with result counting in rows and columns format
    And System should validate without file transfer for dry-run operations
    And System should help users explore datasets before downloading