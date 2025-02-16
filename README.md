# GridKey

This project is a Django REST Framework-based backend for managing stock transactions (BUY, SELL, SPLIT) using FIFO processing, JWT authentication, and stock summary calculations. It is designed to run as an ASGI application served by Uvicorn and can be containerized with Docker.

---

## Table of Contents

- [Project Overview](#project-overview)
- [Prerequisites](#prerequisites)
- [Setup Instructions](#setup-instructions)
- [API Endpoints](#api-endpoints)
---

## Project Overview

The Grid Key (Trade Simulation) implements:
- **Trade Operations:**  
  - **BUY:** Record buy transactions.
  - **SELL:** Process sell transactions using FIFO logic.
  - **SPLIT:** Adjust existing BUY trades when a stock split occurs.
- **Stock Summary:**  
  Calculate volume-weighted average buy price and total remaining quantity per company.
- **Authentication:**  
  Uses JWT for authentication with an extended access token lifetime.
- **ASGI Server:**  
  Deployed with Uvicorn for asynchronous support.

---

## Prerequisites

- **Python 3.8+**
- **PostgreSQL** (configured in `settings.py`)
- **Docker** (optional, for containerized deployment)

---

## Setup Instructions

### Local Setup

1. **Clone the Repository:**
   ```bash
   git clone <repository_url>
   cd GridKeyAsses

2. **Install Dependencies:**
   ```bash
   pip install -r requirements.txt

3. **Migrations**
   ```bash
   python manage.py makemigrations
   python manage.py migrate

4. **Start Server:**
   ```bash
   uvicorn GridView.asgi:application --host 0.0.0.0 --port 8000
   

## API Endpoints

### User Management

- **Register User**
  - **Endpoint:** `POST /api/users/register/`
  - **Description:** Registers a new user in the system.
  - **Request Body:**
    ```json
    {
      "username": "testuser",
      "email": "testuser@example.com",
      "password": "TestPass123!",
      "password2": "TestPass123!"
    }
    ```
  - **Response:**
    - **201 Created:** User registered successfully.
    - **400 Bad Request:** Validation errors or missing fields.

- **User Login**
  - **Endpoint:** `POST /api/users/login/`
  - **Description:** Authenticates a user and returns a JWT access token.
  - **Request Body:**
    ```json
    {
      "username": "testuser",
      "password": "TestPass123!"
    }
    ```
  - **Response:**
    - **200 OK:** Returns an access token.
      ```json
      {
        "access": "YOUR_ACCESS_TOKEN_HERE"
      }
      ```
    - **400 Bad Request:** Invalid credentials.

- **User Profile**
  - **Endpoint:** `GET /api/users/profile/`
  - **Description:** Retrieves the profile details of the authenticated user.
  - **Headers:**
    - `Authorization: Bearer YOUR_ACCESS_TOKEN_HERE`
  - **Response:**
    - **200 OK:** Returns user profile data.
    - **401 Unauthorized:** Token is missing or invalid.

---

### Trade Operations

- **Record Trade**
  - **Endpoint:** `POST /api/trades/record/<trade_type>/`
  - **Description:** Records a trade transaction for BUY, SELL, or SPLIT. The trade type is provided as a URL path parameter.
  - **Request Body Examples:**
    - **BUY Trade:**
      ```json
      {
        "company": "ABC Ltd.",
        "quantity": 50,
        "price": "260.00"
      }
      ```
    - **SELL Trade:**
      ```json
      {
        "company": "ABC Ltd.",
        "quantity": 20,
        "price": "275.00"
      }
      ```
    - **SPLIT Trade:**
      ```json
      {
        "company": "ABC Ltd.",
        "split_ratio": 5
      }
      ```
  - **Headers:**
    - `Authorization: Bearer YOUR_ACCESS_TOKEN_HERE`
  - **Response:**
    - **201 Created:** Returns details of the recorded trade.
    - **400 Bad Request:** Validation errors or processing issues.

---

### Stock Summary

- **Stock Summary**
  - **Endpoint:** `GET /api/trades/summary/`
  - **Description:** Retrieves a summary of BUY trades (remaining quantity and weighted average buy price) for the authenticated user.
  - **Query Parameters:**
    - `time_zone` (optional, default: `UTC`): The local time zone of the provided dates.
    - `period` (optional): Predefined period filter. Supported values:
      - `today` – Summary for the current day.
      - `this_month` – Summary for the current month.
      - `custom` – Custom date range (requires `start_date` and `end_date`).
    - `start_date` and `end_date` (required if period is `custom`): Dates in `YYYY-MM-DD` format.
    - `date` (optional): A specific day (in `YYYY-MM-DD` format) that overrides the period if provided.
    - `company` (optional): Filters the summary by company name.
  - **Headers:**
    - `Authorization: Bearer YOUR_ACCESS_TOKEN_HERE`
  - **Response:**
    - **200 OK:** Returns a list of summary objects. Example response:
      ```json
      [
        {
          "company": "ABC Ltd.",
          "total_quantity": 80,
          "avg_buy_price": 261.0
        }
      ]
      ```
    - **400 Bad Request:** Missing or invalid query parameters.
    - **401 Unauthorized:** Token is missing or invalid.
