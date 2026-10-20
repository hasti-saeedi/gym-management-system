# Manual API Testing — Gym Management System

## 1. Overview

This document describes the manual API testing performed on the Gym Management System REST API using Postman, with the API endpoints referenced from the project's Swagger/OpenAPI documentation.

The purpose of testing was to validate API behavior under different input conditions, verify authentication and access control, and compare actual responses with expected results.

## 2. Testing Scope

The following testing areas were covered during manual execution:

- **API Coverage:** Executing the API endpoints documented in Swagger.
- **Positive Testing:** Sending requests with different valid input data.
- **Negative Testing:** Testing invalid inputs and missing fields.
- **Authentication Testing:** Testing authentication-related API behavior.
- **Authorization Testing:** Checking access permissions for API operations.
- **CRUD Testing:** Testing Create, Read, Update, and Delete operations where applicable.
- **HTTP Response Validation:** Reviewing HTTP status codes and response bodies.
- **Expected vs. Actual Results:** Comparing actual API responses with expected behavior.

## 3. Test Approach

1. Identify the API endpoints from the Swagger/OpenAPI documentation.
2. Execute the corresponding requests in Postman.
3. Use different input values and request payloads.
4. Test applicable invalid-input and authentication/authorization scenarios.
5. Review HTTP status codes and response bodies.
6. Compare actual responses against the expected behavior.
7. Record the results and document any unexpected behavior observed.

## 4. Test Case Documentation

Each test case should record the endpoint, input data, expected result, actual result, and execution status.

| Test Case ID | Test Scenario | Expected Result | Actual Result | Status |
|---|---|---|---|---|
| TC-001 | Valid request with different input data | Response matches the API specification and supplied data | Record observed response | Record result |
| TC-002 | Request with invalid input | Appropriate validation response is returned | Record observed response | Record result |
| TC-003 | Request with missing required fields | Missing-field validation is handled appropriately | Record observed response | Record result |
| TC-004 | Authentication-related request | Authentication behavior matches the endpoint's requirements | Record observed response | Record result |
| TC-005 | Request with insufficient permissions | Access is handled according to the authorization rules | Record observed response | Record result |
| TC-006 | Create operation | Resource is created according to the API specification | Record observed response | Record result |
| TC-007 | Read operation | Correct resource data is returned | Record observed response | Record result |
| TC-008 | Update operation | Resource is updated according to the request | Record observed response | Record result |
| TC-009 | Delete operation | Resource deletion follows the endpoint's expected behavior | Record observed response | Record result |
| TC-010 | HTTP status code and response body validation | Status code and response body match the expected behavior | Record observed response | Record result |

**Note:** These are documentation templates for the testing scenarios described. Record actual results and final statuses based on execution evidence. Not every scenario necessarily applies to every endpoint.

## 5. Test Environment

- **API Documentation:** Swagger/OpenAPI
- **API Testing Tool:** Postman
- **Application:** Gym Management System REST API
- **Test Type:** Manual API Testing

## 6. Test Results and Evidence

Detailed execution results should be recorded for individual test cases, including:

- Request method and endpoint
- Relevant request parameters or payload
- Expected HTTP status code and response
- Actual HTTP status code and response
- Pass/Fail status
- Notes or screenshots, where useful

No aggregate pass rate or defect count is reported in this document because verified execution totals have not been recorded here.

## 7. Related Automated Tests

The project also contains automated tests implemented using the Django testing framework. These are separate from the manual API requests executed in Postman.

To run the project's automated tests, use:

```bash
python manage.py test
```

Run the command in the project's configured Python environment and follow the project's setup instructions.

## 8. Notes

This document summarizes the manual API testing activities performed on the project. Detailed test results should reflect the actual observed behavior of the API and should not be inferred solely from the expected results.
