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
