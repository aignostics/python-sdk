Feature: TEST-SWR-VISUALIZATION-10-GENERATE-IMAGE-THUMBNAILS-AND-PREVIEWS

  Background:
    Given user has whole slide image files

  @tests:SWR-VISUALIZATION-10 @id:TEST-SWR-VISUALIZATION-10-THUMBNAIL-GENERATION
  Scenario: System generates thumbnails with format conversion and fallback support
    When User requests thumbnails via HTTP endpoints with source parameters
    Then System should return HTTP status code 200 with Content-Type "image/png"
    And System should generate PNG format thumbnails with valid dimensions
    And System should support JPEG format conversion with Content-Type "image/jpeg"
    And System should provide fallback thumbnail images for missing or unsupported files