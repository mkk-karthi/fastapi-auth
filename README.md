# FastAPI Auth Scaffolding 🚀

A production-ready FastAPI authentication scaffolding project with user management, secure authentication, caching, rate limiting, and logging — built using clean architecture and modern Python tooling.

---

## 📌 Features

* 📦 Poetry for Dependency Management
* 👤 User CRUD APIs
* 📁 File Upload Support
* 🗃️ SQLAlchemy ORM with Alembic Migrations
* 📧 Email Notifications (OTP / Verification / Reset)
* ⚡ Redis Cache Server Integration
* 🔐 Authentication & Authorization (JWT-based)
* 🔑 Change Password & Forgot Password Flow
* 🛡️ Rate Limiting using SlowAPI
* 📊 Structured Logging with Loguru
* 🧩 Modular and Scalable Project Structure
* 📑 Standardized API Responses & Validation Schemas

---

## 🏗️ Tech Stack

* FastAPI
* SQLAlchemy (ORM)
* Alembic (Database Migrations)
* Redis (Caching)
* SlowAPI (Rate Limiting)
* Loguru (Logging)
* Poetry (Dependency Management)
* Pydantic (Validation)
* JWT (Authentication)
* SMTP (Email Service)

---

## 📁 Project Structure

```
fastapi-auth/
│
├── app/
│   ├── api/                # API routes
│   │   ├── auth.py
│   │   ├── users.py
│   │   └── router.py
│   │
│   ├── core/               # Core configurations
│   │   ├── config.py
│   │   ├── auth.py
│   │   ├── database.py
│   │   └── logger.py
│   │
│   ├── models/             # SQLAlchemy models
│   ├── schemas/            # Pydantic schemas
│   ├── services/           # Business logic layer
│   └── main.py             # App entry point
│
├── alembic/                # Migration folder
├── tests/                  # Test cases (optional)
├── .env                    # Environment variables
├── pyproject.toml          # Poetry dependencies
└── README.md
```

---

## ⚙️ Installation

### 1. Clone the Repository

```bash
git clone https://github.com/mkk-karthi/fastapi-auth.git
cd fastapi-auth
```

### 2. Install Dependencies (Poetry)

```bash
poetry install
```

### 3. Activate Virtual Environment

```bash
poetry shell
```

---

## 🔧 Environment Configuration

Create a `.env` file in the root directory:

```
APP_NAME=FastAPI Auth
DEBUG=True

# Database
DB_HOST=127.0.0.1
DB_PORT=3306
DB_DATABASE=db_name
DB_USERNAME=root
DB_PASSWORD=password

# JWT
SECRET_KEY=your_secret_key
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE=60

# Redis
REDIS_HOST=127.0.0.1
REDIS_PORT=6379
REDIS_PASSWORD=

# Mail
MAIL_HOST=smtp.gmail.com
MAIL_PORT=587
MAIL_USERNAME=your_email
MAIL_PASSWORD=your_password
MAIL_TLS=True
MAIL_FROM=your_email
```

---

## 🗄️ Database Migration (Alembic)

### Initialize Migration

```bash
poetry run alembic init alembic
```

### Create Migration

```bash
poetry run alembic revision --autogenerate -m "initial migration"
```

### Apply Migration

```bash
poetry run alembic upgrade head
```

---

## 🚀 Running the Application

```bash
poetry run python -m app.server
```

API Docs:

* Swagger UI: http://127.0.0.1:8000/api/docs
* ReDoc: http://127.0.0.1:8000/api/redoc

---

## 🔐 Authentication Flow

* User Registration
* Email Verification (Optional)
* Login with JWT Access Token
* Token-based Protected Routes
* Change Password (Authenticated)
* Forgot Password (OTP / Email Reset)

---

## 📡 API Modules

### Auth APIs

* Register User
* Login
* Forgot Password
* Reset Password
* Change Password

### User APIs

* Create User
* Get User List (Pagination)
* Get User by ID
* Update User
* Delete User

---

## 📁 File Upload

Supports multipart file uploads with validation and storage handling.

Example:

```http
POST /users/upload-avatar
Content-Type: multipart/form-data
```

---

## ⚡ Redis Caching

* Used for OTP storage
* Token blacklisting (optional)
* Frequently accessed data caching
* Session management support

---

## 🛡️ Rate Limiting (SlowAPI)

Configured to prevent abuse:

* Login endpoint protection
* OTP request limits
* Public API throttling

Example:

```
5 requests per minute per IP
```

---

## 📊 Logging (Loguru)

* Structured logs
* Error tracking
* Request/Response logging
* File & console logging support

Log file location:

```
logs/app.log
```

---

## 📦 Dependency Management (Poetry)

Add new package:

```bash
poetry add package_name
```

Update dependencies:

```bash
poetry update
```

---

## ✅ Standard API Response Format

```json
{
  "code": 200,
  "message": "Success",
  "data": []
}
```

Error Response:

```json
{
  "code": 400,
  "message": "Validation Error",
  "errors": []
}
```
