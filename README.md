# Expense Tracker Backend

[![CI](https://github.com/your-username/Expense-Tracker/actions/workflows/ci.yml/badge.svg)](https://github.com/your-username/Expense-Tracker/actions)

A FastAPI-based backend for managing users, budgets, and expenses with JWT authentication and PostgreSQL support.  
This project uses **uv** for dependency management and Docker for containerization.

---

## 🚀 Features
- User registration and authentication (JWT-based)  
- Add, update, and fetch expenses  
- Create and manage budgets  
- Track balances across bank and cash  
- PostgreSQL database with Alembic migrations  
- Dockerized setup for both development and production  

---

## 🛠 Tech Stack
- **FastAPI** (web framework)  
- **PostgreSQL** (database)  
- **SQLAlchemy & Alembic** (ORM + migrations)  
- **Passlib + JWT** (authentication & security)  
- **Docker & Docker Compose** (containerized setup)  
- **uv** (dependency management)  

---

## 📦 Installation

### 1. Clone the repository
```bash
git clone https://github.com/your-username/Expense-Tracker.git
cd Expense-Tracker
