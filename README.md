# Expense Tracker Backend

A FastAPI-based backend for managing users, budgets, and expenses with JWT authentication and PostgreSQL support.
This project uses **uv** for dependency management and **Docker** for containerization.

---

## 🚀 Features

* User registration and authentication (JWT-based)
* Add, update, and fetch expenses
* Create and manage budgets
* Track balances across bank and cash
* PostgreSQL database with Alembic migrations
* Dockerized setup for both development and production

---

## 🛠 Tech Stack

* **FastAPI** (web framework)
* **PostgreSQL** (database)
* **SQLAlchemy** & **Alembic** (ORM + migrations)
* **Passlib** + **JWT** (authentication & security)
* **Docker** & **Docker Compose** (containerized setup)
* **uv** (dependency management)

---

## 📦 Installation

1.  **Clone the repository**
    ```bash
    git clone https://github.com/your-username/Expense-Tracker.git
    cd Expense-Tracker
    ```

2.  **Install dependencies using uv**
    ```bash
    uv sync --all-extras
    ```

3.  **Run locally**
    ```bash
    uv run uvicorn src.main:app --reload --host 0.0.0.0 --port 8000
    ```

The API will be available at:

👉 **http://localhost:8000**

👉 **Docs**: http://localhost:8000/docs

---

## 🐳 Running with Docker

**Development**
```bash
docker-compose --profile dev up --build
```

**Production**
```bash
docker-compose --profile prod up --build -d
```

---

## 🗄 Database Migrations

Run Alembic migrations with:

```bash
uv run alembic upgrade head
```

Or via Docker:

```bash
docker-compose --profile migrate up --build
```

---

## 🧪 Running Tests

```bash
uv run pytest -v
```

Logs are stored in `logs/tests_output.log`.

---

## ⚙️ Environment Variables

Create a  .env file in the project root:

```bash
SECRET_KEY=your_secret_key
DATABASE_URL=postgresql://username:password@hostname:5432/dbname
ACCESS_TOKEN_EXPIRE_MINUTES=30
ALGORITHM=HS256
```

---

## 📂 Project Structure

```
.
├── src/               # Application source code
├── alembic/           # Database migrations
├── tests/             # Unit and integration tests
├── Dockerfile         # Multi-stage Docker build
├── docker-compose.yml # Docker services
├── pyproject.toml     # Project dependencies
└── README.md          # Project docs
```

---

✅ This backend is fully tested, Dockerized, and ready to deploy.

