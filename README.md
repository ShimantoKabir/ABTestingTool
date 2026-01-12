# ABTestingTool

ABTestingTool is a **user, role, menu, and API access management system** built with **FastAPI**.
It also includes an **experimentation and decision engine** supporting A/B testing,
personalization, Redis caching, and PostgreSQL.

---

## 🚀 Features

- JWT-based Authentication & Refresh Tokens
- User & Organization Management
- Role & Permission System
- Menu & Menu Template Management
- API Access Control
- Experimentation Platform (A/B Testing, Personalization)
- Targeting Conditions & Variations
- Metrics Tracking
- Decision Engine with Bucketing
- Redis-based Caching
- Fully Dockerize Setup
- Alembic Database Migrations
- Email-based OTP & Notifications (Mailmug for development)

---

## 🛠 Tech Stack

- Backend: FastAPI
- Database: PostgreSQL (SQLModel + SQLAlchemy)
- Cache: Redis
- Authentication: JWT (Access & Refresh Tokens)
- Migrations: Alembic
- Containerization: Docker & Docker Compose
- Python Version: 3.12+

---

## 📂 Project Structure (High Level)

    ABTestingTool/
    ├── src/                 Application source code
    ├── migrations/          Alembic migrations
    ├── main.py              Application entry point
    ├── core.py              FastAPI app instance
    ├── db.py                Database session & engine
    ├── di.py                Dependency injection
    ├── Dockerfile
    ├── docker-compose.yml
    ├── requirements.txt
    ├── .env.dev
    └── README.md

---

## 🐳 Run With Docker (Recommended)

### Build & Start Services

    docker-compose up --build

Services started:

- FastAPI: http://localhost:8000
- PostgreSQL: localhost:5433
- Redis: localhost:6379

### Generate migration:

    docker-compose exec web alembic revision --autogenerate -m "init"

### Run Database Migrations

    docker-compose exec web alembic upgrade head

### API Documentation

- Swagger UI: http://localhost:8000/docs
- OpenAPI JSON: http://localhost:8000/openapi.json

---

## 🧑‍💻 Run Without Docker (Local Development)

### 1️⃣ Create Virtual Environment

    python -m venv venv

Activate it:

Windows:
venv\Scripts\activate

Linux / macOS:
source venv/bin/activate

---

### 2️⃣ Install Dependencies

    pip install -r requirements.txt

---

### 3️⃣ Configure Environment

Create `.env.dev`

SQLite (local testing):

    DB_URL=sqlite:///db.sqlite

---

### 4️⃣ Database Migration Commands

Initialize migrations (first time only):

    alembic init migrations

Generate migration:

    alembic revision --autogenerate -m "init"

Apply migrations:

    alembic upgrade head

---

### 5️⃣ Start Development Server

Using Uvicorn:

    uvicorn main:app --reload

Or using FastAPI CLI:

    fastapi dev main.py

Server URL:
http://127.0.0.1:8000

---

## 🔐 Authentication Notes

Most endpoints require these headers:

    Authorization: Bearer <access_token>
    email: user@example.com

Public endpoints include:

- /
- /auth/login
- /auth/refresh
- /users/registration
- /users/verify

---

## 🧪 Decision Engine Flow

1. Client calls /decision
2. Active experiments fetched (Redis → DB fallback)
3. Targeting rules evaluated
4. Bucketing ensures consistent variation assignment
5. Response includes:
   - Experiment
   - Variation
   - Conditions
   - Metrics

---

## 📧 Mail Service

For development purposes, **Mailmug/MailHog** is used to send:

- Account verification OTP
- Forgot password OTP
- Open the MailHog Web UI at http://localhost:8025

Mail configuration is controlled via environment variables.

---

## Local Storage

Industry-standard tool for local object storage (like Google Cloud Storage or AWS S3) in Docker is MinIO.

- Open the UI: Go to http://localhost:9001
- Login:

  - User: minioadmin
  - Pass: minioadmin

- Create a Bucket: You must create the bucket (e.g., ab-bucket) in the UI before your code tries to upload to it.

---

## 🧹 Useful Commands

Stop Docker containers:

    docker-compose down

Remove containers and volumes (WARNING: deletes DB data):

    docker-compose down -v

Start fresh

    docker-compose up -d --build

Create a new migration:

    alembic revision --autogenerate -m "your message"

View Backend Logs

    docker-compose logs -f web

View Database Logs

    docker-compose logs -f db

---

## 📄 License

This project is intended for **personal or internal use**.
