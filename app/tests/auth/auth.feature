Feature: Authentication and Authorization
  Scenario: Employee successfully logs in
    Given there is a user with the employee role
    When the user logs in with correct credentials
    Then login is successful and the role is verified