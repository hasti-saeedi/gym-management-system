# Gym Management System API

A RESTful backend API for managing gyms, users, classes, sessions, enrollments, payments, attendance, and reports.

This project is built with **Python, Django, Django REST Framework, and PostgreSQL**, with a focus on clean architecture, business logic separation, role-based access control, automated testing, API documentation, and maintainable backend development.

API development and testing are supported with **Swagger/OpenAPI and Postman**, while **JWT authentication** is used for secure API access.

---

## Overview

The Gym Management System is designed to manage the core operations of a gym through a structured REST API.

The system supports multiple gyms and provides different levels of access based on a user's role within a gym.

The main roles are:

* Owner
* Manager
* Staff
* Trainer
* Member

A key design goal of the project is to keep business logic separate from HTTP and validation concerns by following a **Service Layer Architecture**.

The general responsibility of each layer is:

```text
View
  ↓
Serializer
  ↓
Service
  ↓
Model
```
