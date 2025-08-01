Feature: TEST-SWR-APPLICATION-11-EXECUTE-COMPLETE-APPLICATION-WORKFLOWS

  Background:
    Given user installed the Python SDK

  @tests:SWR-APPLICATION-11 @id:TEST-SWR-APPLICATION-11-COMPLETE-WORKFLOW
  Scenario: System executes complete application workflow from start to finish
    When User runs the CLI run execute command with file patterns and metadata annotations
    Then System should prepare metadata, upload images, submit runs, and wait for completion
    And System should download organized results to specified directories

  @tests:SWR-APPLICATION-11 @id:TEST-SWR-APPLICATION-11-RESULT-VALIDATION
  Scenario: System validates downloaded results contain expected analysis artifacts
    When User executes complete application workflow for "he-tme"
    Then System should create results directory with 9 expected files
    And Results should include "tissue_segmentation_csv_class_information.csv"
    And Results should include "cell_classification_geojson_polygons.json"