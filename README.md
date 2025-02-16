# GridKey

This project is a Django REST Framework-based backend for managing stock transactions (BUY, SELL, SPLIT) using FIFO processing, JWT authentication, and stock summary calculations. It is designed to run as an ASGI application served by Uvicorn and can be containerized with Docker.

---

## Table of Contents

- [Project Overview](#project-overview)
- [Prerequisites](#prerequisites)
- [Setup Instructions](#setup-instructions)
- [API Endpoints](#api-endpoints)
- [Assignment Simulation](#assignment-simulation)
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


#  Assignment Simulation

This simulation demonstrates the core API functionalities as per the assignment. The following steps cover:

1. **User Registration**
2. **User Login**
3. **Recording a BUY Trade**
4. **Recording a SELL Trade**
5. **Recording a SPLIT Trade**
6. **Fetching Today's Stock Summary**

> **Note:** Replace `access_token` with the JWT access token obtained from the login API.

---

## 1. Create User

Register a new user (investor):

```sh
curl --location 'http://127.0.0.1:8000/api/users/register/' \
--header 'Content-Type: application/json' \
--data-raw '{
    "username": "investor", 
    "email": "investor@example.com", 
    "password": "investor", 
    "password2": "investor" 
}'
```

---

## 2. Login

Authenticate the user to obtain the JWT access token:

```sh
curl --location 'http://127.0.0.1:8000/api/users/login/' \
--header 'Content-Type: application/json' \
--data '{
    "username": "investor", 
    "password": "investor" 
}'
```

After a successful login, copy the access token and set it as `access_token` in your Postman environment or replace it in subsequent cURL commands.

---

## 3. Record BUY Trade

Record a BUY trade for company "REL IND" (buy 50 shares at 260.00):

```sh
curl --location 'http://127.0.0.1:8000/api/trades/record/BUY/' \
--header 'Content-Type: application/json' \
--header 'Authorization: Bearer access_token' \
--data '{
    "company": "REL IND",
    "quantity": 50,
    "price": "260.00"
}'
```

---

## 4. Record SELL Trade

Record a SELL trade for "REL IND" (sell 20 shares at 275.00):

```sh
curl --location 'http://127.0.0.1:8000/api/trades/record/SELL/' \
--header 'Content-Type: application/json' \
--header 'Authorization: Bearer access_token' \
--data '{
    "company": "REL IND",
    "quantity": 20,
    "price": "275.00"
}'
```

---

## 5. Record SPLIT Trade

Record a SPLIT trade for "REL IND" with a split ratio of 5:

```sh
curl --location 'http://127.0.0.1:8000/api/trades/record/SPLIT/' \
--header 'Content-Type: application/json' \
--header 'Authorization: Bearer access_token' \
--data '{
    "company": "REL IND",
    "split_ratio": 5
}'
```

---

## 6. Get Today's Stock Summary

Retrieve today's stock summary for the authenticated user, using the `Asia/Kolkata` time zone:

```sh
curl --location 'http://127.0.0.1:8000/api/trades/summary/?period=today&time_zone=Asia%2FKolkata' \
--header 'Authorization: Bearer access_token'
```

---


