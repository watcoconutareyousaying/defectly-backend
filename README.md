# 🧪 Test Doc Server

A backend system for managing test documentation, including test plans, test cases, coverage, defect tracking, and report generation. Designed to support QA engineers and software teams in maintaining structured and efficient testing workflows.

---

## 🚀 Features

- **📋 Manage Test Plans & Test Cases** – Create, update, and organize testing artifacts.  
- **🧩 Track Test Coverage** – Keep track of which requirements are covered by test cases.  
- **🐞 Record and View Defects** – Log, track, and manage software defects efficiently.  
- **📤 Export Reports** – Generate summary or detailed reports for testing activities.  
- **🔐 Basic User Authentication** – Secure access with login and user management.  

---

## 🛠️ Tech Stack

- **Framework:** FastAPI  
- **Database:** SQLAlchemy + PostgreSQL/MySQL/SQLite (configurable)  
- **Authentication:** JWT tokens  
- **Testing & Validation:** Pydantic schemas  
- **Logging:** Centralized logging with middleware support  

---

## ⚙️ Setup & Installation

### 1. Clone the repository

```bash
git clone https://github.com/pepperthecar/defectly-backend.git
cd defectly-backend
```

### 2. Create a virtual environment

**macOS/Linux**

```bash
python3 -m venv venv
source venv/bin/activate
```

**Windows**

```bash
python -m venv venv
venv\Scripts\activate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure environment variables

```bash
cp .env.example .env
```

Edit the `.env` file with your database URL and secret key.

### 5. Run database migrations

```bash
alembic upgrade head
```

### 6. Start the server

```bash
uvicorn app.main:app --reload
```

API: http://127.0.0.1:8000  
Swagger UI: http://127.0.0.1:8000/docs  

---

## 🧩 Project Structure

```
app/
 ├─ api/v1/         # Route definitions
 ├─ core/           # Config & security utilities
 ├─ crud/           # Database operations
 ├─ db/             # Database configuration
 ├─ models/         # Database models
 ├─ schemas/        # Pydantic validation schemas
 ├─ services/       # Business logic
 ├─ middleware/     # Logging, timing, and error handler middleware
 ├─ utils/          # Logger, helpers
 └─ main.py         # Application entry point
migration/           # Alembic migration scripts
tests/               # Unit and integration tests
```

---

## 📝 Logging & Middleware

- **LoggingMiddleware:** Logs each request with method, path, IP, and processing time.  
- **TimingMiddleware:** Adds `X-Process-Time` header for each request.  
- **ErrorHandlerMiddleware:** Catches unhandled exceptions and returns standardized JSON error responses.  
- **User-specific logging:** Use `log_user_action(user_email, request_path)` to log authenticated user actions.

---

## 🔐 Authentication

- JWT-based authentication is implemented.  
- Use `get_current_user` dependency in routes to access the authenticated user.  
- Only authenticated and active users can access protected endpoints.

---

## 📦 Usage Examples

**Get current user info**

```python
@router.get("/me", response_model=UserResponse)
def read_users_me(current_user: User = Depends(get_current_user)):
    log_user_action(current_user.email, "/me")
    return current_user
```

**Create a new test plan**

```python
@router.post("/plans")
def create_plan(plan: PlanCreate, current_user: User = Depends(get_current_user)):
    return plan_service.create_plan(plan, current_user)
```

---

## 🧪 Testing
Run tests with:
```bash
pytest tests/
```
Includes unit tests for CRUD, services, and routes.

---

## 📂 Logs

All logs are written to:
```
logs/app.log
```
Middleware automatically logs requests, errors, and timing.

---

## 👨‍💻 Contributing
Fork the repository.
Create a feature branch:
```bash
git checkout -b feature/your-feature-name
```
Make changes, commit, and push:
```
git push origin feature/your-feature-name
```
Open a pull request.

---

## ⚡ License

MIT License © 2025
