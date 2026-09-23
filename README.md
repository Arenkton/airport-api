# Airport API

REST API service for airport management, flight scheduling, and ticket booking built with Django REST Framework.

## Technologies

* Python 3.14
* Django
* Django REST Framework
* PostgreSQL
* Docker and Docker Compose
* Token Authentication
* drf-spectacular (Swagger / OpenAPI)

## Features

* Airport and route management
* Airplane and airplane type management
* Crew and flight management
* Flight filtering by source airport, destination airport, and departure date
* Flight seat availability tracking
* Ticket booking with seat availability validation
* Prevention of duplicate seat bookings
* User registration and token authentication
* User profile management
* Admin-only access for modifying airport and flight data
* Paginated API responses
* Interactive API documentation using Swagger

## Installation

The project can be run using Docker or installed locally.

### Run with Docker

Make sure Docker and Docker Compose are installed and running.

1. Clone the repository:

```bash
git clone https://github.com/YOUR_USERNAME/airport-api.git
cd airport-api
```

2. Create a `.env` file in the project root using `.env.example` as a template:

```env
DB_NAME=airport
DB_USER=airport
DB_PASSWORD=your_secure_password
```

3. Build and start the containers:

```bash
docker compose up -d --build
```

Docker Compose will start PostgreSQL, apply database migrations, and launch the Django server.

4. Open the API:

http://127.0.0.1:8000/api/airport/

Swagger documentation:

http://127.0.0.1:8000/api/docs/

To stop the containers:

```bash
docker compose down
```

### Run locally

Requirements:

* Python 3.14
* Git

By default, the project uses SQLite for local development when `DB_HOST` is not configured.

1. Clone the repository:

```bash
git clone https://github.com/Arenkton/airport-api.git
cd airport-api
```

2. Create and activate a virtual environment.

Windows:

```bash
python -m venv .venv
.venv\Scripts\activate
```

Linux / macOS:

```bash
python -m venv .venv
source .venv/bin/activate
```

3. Install dependencies:

```bash
pip install -r requirements.txt
```

4. Apply database migrations:

```bash
python manage.py migrate
```

5. Start the development server:

```bash
python manage.py runserver
```

The API will be available at:

http://127.0.0.1:8000/api/airport/

## Authentication

The API uses Django REST Framework Token Authentication.

Register a new user:

`POST /api/user/register/`

Example request:

```json
{
    "username": "airport_user",
    "email": "user@example.com",
    "password": "YourSecurePassword123!"
}
```

Obtain an authentication token:

`POST /api/user/token/`

Example request:

```json
{
    "username": "airport_user",
    "password": "YourSecurePassword123!"
}
```

Include the received token in the Authorization header when accessing protected endpoints:

```http
Authorization: Token YOUR_AUTHENTICATION_TOKEN
```

View or update your profile:

`GET /api/user/me/`

`PATCH /api/user/me/`

## API Endpoints

### Airport Management

| Method      | Endpoint                      | Description         |
| ----------- | ----------------------------- | ------------------- |
| GET         | `/api/airport/airports/`      | List all airports   |
| POST        | `/api/airport/airports/`      | Create an airport   |
| GET         | `/api/airport/airports/{id}/` | Retrieve an airport |
| PUT / PATCH | `/api/airport/airports/{id}/` | Update an airport   |
| DELETE      | `/api/airport/airports/{id}/` | Delete an airport   |

### Routes

| Method      | Endpoint                    | Description            |
| ----------- | --------------------------- | ---------------------- |
| GET         | `/api/airport/routes/`      | List routes            |
| POST        | `/api/airport/routes/`      | Create a route         |
| GET         | `/api/airport/routes/{id}/` | Retrieve route details |
| PUT / PATCH | `/api/airport/routes/{id}/` | Update a route         |
| DELETE      | `/api/airport/routes/{id}/` | Delete a route         |

Routes connect two different airports and include the distance between them.

### Airplanes and Airplane Types

| Method                     | Endpoint                            | Description                                  |
| -------------------------- | ----------------------------------- | -------------------------------------------- |
| GET / POST                 | `/api/airport/airplane-types/`      | List or create airplane types                |
| GET / PUT / PATCH / DELETE | `/api/airport/airplane-types/{id}/` | Retrieve, update, or delete an airplane type |
| GET / POST                 | `/api/airport/airplanes/`           | List or create airplanes                     |
| GET / PUT / PATCH / DELETE | `/api/airport/airplanes/{id}/`      | Retrieve, update, or delete an airplane      |

Each airplane has a type, number of rows, and number of seats per row.

### Crew

| Method                     | Endpoint                  | Description                               |
| -------------------------- | ------------------------- | ----------------------------------------- |
| GET / POST                 | `/api/airport/crew/`      | List or create crew members               |
| GET / PUT / PATCH / DELETE | `/api/airport/crew/{id}/` | Retrieve, update, or delete a crew member |

### Flights

| Method      | Endpoint                     | Description             |
| ----------- | ---------------------------- | ----------------------- |
| GET         | `/api/airport/flights/`      | List flights            |
| POST        | `/api/airport/flights/`      | Create a flight         |
| GET         | `/api/airport/flights/{id}/` | Retrieve flight details |
| PUT / PATCH | `/api/airport/flights/{id}/` | Update a flight         |
| DELETE      | `/api/airport/flights/{id}/` | Delete a flight         |

Flight details include the route, airplane, crew, departure and arrival times, and available seats.

### Orders

| Method | Endpoint                    | Description                                           |
| ------ | --------------------------- | ----------------------------------------------------- |
| GET    | `/api/airport/orders/`      | List the authenticated user's orders                  |
| POST   | `/api/airport/orders/`      | Create an order with tickets                          |
| GET    | `/api/airport/orders/{id}/` | Retrieve an order belonging to the authenticated user |

Users cannot access other users' orders.

### User Management

| Method      | Endpoint              | Description                         |
| ----------- | --------------------- | ----------------------------------- |
| POST        | `/api/user/register/` | Register a new user                 |
| POST        | `/api/user/token/`    | Obtain an authentication token      |
| GET         | `/api/user/me/`       | Retrieve the current user's profile |
| PUT / PATCH | `/api/user/me/`       | Update the current user's profile   |

## Permissions

The API uses role-based access control.

| User type          | Read airport and flight data | Modify airport and flight data | Create and view own orders |
| ------------------ | ---------------------------- | ------------------------------ | -------------------------- |
| Unauthenticated    | Yes                          | No                             | No                         |
| Authenticated user | Yes                          | No                             | Yes                        |
| Staff user         | Yes                          | Yes                            | Yes                        |

Only users with `is_staff=True` can create, update, or delete airports, routes, airplanes, airplane types, crew members, and flights.

Authentication is required to create or view orders. Users can only access their own orders.

## Flight Filtering

The flight list supports filtering by source airport, destination airport, and departure date.

| Parameter     | Type    | Description                         |
| ------------- | ------- | ----------------------------------- |
| `source`      | Integer | Source airport ID                   |
| `destination` | Integer | Destination airport ID              |
| `date`        | Date    | Departure date in YYYY-MM-DD format |
| `page`        | Integer | Page number                         |

Example:

```http
GET /api/airport/flights/?source=1&destination=2&date=2026-10-01
```

Filters can be combined in a single request.

Invalid filter values return HTTP 400 Bad Request.

## Pagination

List endpoints use page-number pagination with 10 results per page.

Example:

```http
GET /api/airport/flights/?page=2
```

Paginated responses contain `count`, `next`, `previous`, and `results`.

## Ticket Booking

Authenticated users can create an order containing one or more tickets.

Each ticket specifies the flight, row, and seat number.

Example request:

```http
POST /api/airport/orders/
Authorization: Token YOUR_AUTHENTICATION_TOKEN
Content-Type: application/json
```

```json
{
    "tickets": [
        {
            "flight": 1,
            "row": 5,
            "seat": 3
        },
        {
            "flight": 1,
            "row": 5,
            "seat": 4
        }
    ]
}
```

The order is automatically assigned to the authenticated user.

### Booking Validation

The API validates the following conditions:

* Row and seat numbers must be positive.
* Row numbers cannot exceed the number of rows in the airplane.
* Seat numbers cannot exceed the number of seats per row.
* The same seat cannot be booked twice on the same flight.
* Duplicate seats within a single order are rejected.
* Orders cannot contain an empty ticket list.

Ticket creation is performed inside a database transaction. If ticket creation fails, the entire order creation is rolled back.

A database-level unique constraint prevents duplicate bookings for the same flight, row, and seat.

### Seat Availability

Flight detail responses include an `available_seats` field.

The number of available seats is calculated by subtracting the number of booked tickets from the airplane's total seating capacity.

## Database Diagram

The database consists of airports, routes, airplanes, airplane types, crew members, flights, orders, tickets, and users.

The diagram below illustrates the relationships between these entities.

![Airport API Database Diagram](docs/airport-db-diagram.png)

[View and edit the database diagram](docs/airport-db-diagram.drawio)

## Running tests

Run all automated tests:

```bash
python manage.py test
```

## API Documentation

Interactive Swagger documentation is available at:

http://127.0.0.1:8000/api/docs/

OpenAPI schema:

http://127.0.0.1:8000/api/schema/
