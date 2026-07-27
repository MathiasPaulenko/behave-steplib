Feature: API health check

  Scenario: GET users returns 200
    Given the API base url is "https://api.example.com"
    When I send a GET request to "/users"
    Then the response status is 200
    And the response body is valid JSON
    And the JSON path "$.users[0].name" equals "Ada"
