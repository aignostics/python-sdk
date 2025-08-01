Feature: TEST-SWR-VISUALIZATION-9-INSPECT-WHOLE-SLIDE-IMAGE-METADATA

  Background:
    Given user installed the Python SDK

  @tests:SWR-VISUALIZATION-9 @id:TEST-SWR-VISUALIZATION-9-METADATA-INSPECTION
  Scenario: System inspects whole slide images and extracts structured metadata
    When User runs image inspection commands on DICOM files and other supported formats
    Then System should extract metadata including format type, pixel dimensions, tile size
    And System should extract microns per pixel (MPP) values
    And System should display Format, MPP (x), MPP (y), Dimensions in pixels, Tile size