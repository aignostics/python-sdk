Feature: TEST-SWR-NOTEBOOK-3-SERVE-NOTEBOOK-CONTENT-VIA-HTTP

  Background:
    Given user started notebook server

  @tests:SWR-NOTEBOOK-3 @id:TEST-SWR-NOTEBOOK-3-HTTP-ENDPOINTS
  Scenario: System serves notebook content through HTTP endpoints with iframe integration
    When User accesses notebook endpoint "/notebook/4711?results_folder=/tmp"
    Then System should return HTTP status code 200
    And System should serve content containing embedded iframe
    And Iframe should include source URL pointing to localhost or 127.0.0.1
    And URL should include application run ID parameters for integration