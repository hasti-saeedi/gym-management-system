# Gym Management System API

A production-style RESTful backend API for managing gyms, users, classes, sessions, enrollments, payments, attendance, and reports.

The project is built with **Python, Django, Django REST Framework, and PostgreSQL**, with a focus on clean architecture, separation of business logic, role-based access control, automated testing, API documentation, and maintainable backend development.

---

## Key Highlights

* RESTful API built with **Django REST Framework**
* **Service Layer Architecture** for separating business logic from HTTP and validation concerns
* **JWT-based authentication** and role-based authorization
* Multi-gym architecture with gym-level access control
* **PostgreSQL** database
* API documentation with **Swagger / OpenAPI**
* API testing with **Postman**
* Automated tests for API behavior and business logic
* **GitHub Actions CI** for automated test execution
* Transaction-safe business operations using Django transactions
* Permission-based access control for different gym roles

---

## Tech Stack

* **Language:** Python
* **Framework:** Django, Django REST Framework
* **Database:** PostgreSQL
* **Authentication:** JWT, SimpleJWT
* **API Documentation:** Swagger / OpenAPI
* **API Testing:** Postman
* **Automated Testing:** Django Test Framework
* **CI:** GitHub Actions
* **Architecture:** Service Layer Architecture

---

## Overview

The Gym Management System is designed to manage the core operations of a gym through a structured REST API.

The system supports multiple gyms and provides different levels of access based on a user's role within a gym.

### User Roles

* **Owner** — manages the gym and has the highest level of access
* **Manager** — manages day-to-day gym operations
* **Staff** — handles operational tasks
* **Trainer** — manages classes and training-related activities
* **Member** — accesses membership and enrollment-related functionality

Roles are assigned at the **gym membership level**, allowing the same user to have different roles in different gyms.

---

## Architecture

A key design goal of the project is to keep business logic separate from HTTP handling and validation.

The project follows a **Service Layer Architecture**:

```text
View
  ↓
Serializer
  ↓
Service
  ↓
Model
```

### Responsibilities

**Views**

* Handle HTTP requests and responses
* Delegate business operations to services
* Keep request-handling logic lightweight

**Serializers**

* Validate incoming data
* Serialize API responses
* Handle API input/output representation

**Services**

* Contain business logic
* Coordinate operations across models
* Handle complex workflows
* Use database transactions where necessary

**Models**

* Define database structure
* Handle model-level validation and constraints

**Permissions**

* Handle role-based and gym-level access control

This separation makes the codebase easier to test, maintain, and extend.

---

## Core Features

### Authentication & Authorization

* JWT authentication
* User registration and authentication
* Role-based access control
* Gym-level permissions
* Separate permissions for Owner, Manager, Staff, Trainer, and Member roles

### Gym Management

* Create and manage gyms
* Manage gym memberships
* Assign roles to users
* Control access based on gym membership

### Class & Session Management

* Create and manage gym classes
* Assign trainers
* Manage class sessions
* Track session attendance

### Enrollment & Payments

* Member enrollment in classes
* Enrollment management
* Payment management
* Gym-level access control for enrollments and payments

### Attendance

* Track attendance for class sessions
* Store attendance information for gym members

### Reports

* Reporting functionality for gym-related data

---

## API Documentation

The API is documented using **Swagger / OpenAPI**, making it easier to explore and test available endpoints.

The project uses **drf-spectacular** to generate the API schema and documentation.

---

## Testing

The project includes automated tests covering important API and business-logic behavior.

Testing focuses on areas such as:

* Authentication
* Permissions
* Role-based access control
* API endpoints
* Validation
* Business logic
* Database behavior

API requests can also be tested through the project's **Postman collection**.

---

## Continuous Integration

The project uses **GitHub Actions** to automatically run the test suite in CI.

This helps ensure that changes pushed to the repository are checked automatically and helps prevent regressions during development.

---

## Database

The project uses **PostgreSQL** as its primary database.

Database configuration and migrations are managed through Django's migration system.

---

## Project Structure

```text
gym-management-system/
│
├── accounts/
├── gyms/
├── classes/
├── enrollments/
├── payments/
├── reports/
│
├── config/
├── manage.py
├── requirements.txt
└── README.md
```

Each Django app is responsible for a specific domain of the system, while business logic is handled through dedicated service modules.

---

## API Endpoints

The API is organized around the main resources of the system:

```text
/accounts
/gyms
/classes
/enrollments
/payments
/reports
```

The project currently contains a broad set of REST endpoints covering authentication, gym management, classes, sessions, enrollments, payments, attendance, and reporting.

For the complete list of endpoints and request/response schemas, see the Swagger / OpenAPI documentation.

---

## Getting Started

### 1. Clone the repository

```bash
git clone https://github.com/hasti-saeedi/gym-management-system.git
cd gym-management-system
```

### 2. Create a virtual environment

```bash
python -m venv venv
```

Activate the virtual environment:

**Windows:**

```bash
venv\Scripts\activate
```

**Linux / macOS:**

```bash
source venv/bin/activate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure PostgreSQL

Create a PostgreSQL database and configure the database settings using your environment variables.

### 5. Run migrations

```bash
python manage.py migrate
```

### 6. Run the development server

```bash
python manage.py runserver
```

The API will then be available locally.

---

## Running Tests

Run the automated test suite with:

```bash
python manage.py test
```

---

## Future Improvements

Potential future improvements include:

* Docker containerization
* Redis and Celery for asynchronous/background tasks
* Expanded reporting functionality
* Additional integration tests
* Deployment to a cloud platform

---

## Project Goals

This project was built as a practical backend project to demonstrate experience with:

* REST API development
* Django & Django REST Framework
* Relational database design
* Authentication and authorization
* Service-oriented business logic
* Automated testing
* API documentation
* Continuous Integration
* Maintainable backend architecture
