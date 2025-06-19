# Book Management with FastAPI

A simple book management system built integrating FastAPI, PostgreSQL, Redis, and Celery.

## Table of Contents

1. [Features](#features)
2. [Getting Started](#getting-started)
3. [Prerequisites](#prerequisites)
4. [Project Setup](#project-setup)
5. [Running the Application](#running-the-application)

## Features

- **Book Management:** Create, read, update, and delete books through a RESTful API.
- **User Authentication:** Secure JWT-based authentication and registration.
- **Role-Based Access Control:** Assign roles and restrict access to certain endpoints.
- **User Reviews:** Users can add and manage reviews for books.
- **Email Verification:** Send verification emails to new users.
- **Password Reset:** Secure password reset functionality via email.
- **Background Tasks:** Use Celery for sending emails and other asynchronous tasks.
- **PostgreSQL Integration:** Store and manage data with PostgreSQL.
- **Redis Integration:** Use Redis for caching and JWT token blocklisting.
- **Dockerized Setup:** Easily run the entire stack with Docker Compose for local development and deployment.

## Getting Started

Follow the instructions below to set up and run your FastAPI project.

### Prerequisites

Ensure you have the following installed:

- Python >= 3.10
- PostgreSQL
- Redis

### Project Setup

1. Clone the project repository:
   ```bash
   git clone https://github.com/krsx/book-fastapi.git
   ```
2. Navigate to the project directory:

   ```bash
   cd book-fastapi/
   ```

3. Create and activate a virtual environment:

   ```bash
   python3 -m venv env
   source env/bin/activate
   ```

4. Install the required dependencies:

   ```bash
   pip install -r requirements.txt
   ```

5. Set up environment variables by copying the example configuration:

   ```bash
   cp .env.example .env
   ```

6. Run database migrations to initialize the database schema:

   ```bash
   alembic upgrade head
   ```

7. Open a new terminal and ensure your virtual environment is active. Start the Celery worker (Linux/Unix shell):
   ```bash
   celery -A src.celery_task.celery_app worker --loglevel=INFO
   ```

## Running the Application

Start the application:

```bash
fastapi dev src/
```

Alternatively, you can run the application using Docker:

```bash
docker compose up -d
```
