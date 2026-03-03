# 📚 NextRead – Library Management System (Flask)

A full-featured library web application built with **Flask**, implementing all requirements of Lab 2.

---

## ✅ Features Implemented

| Feature | Level |
|---------|-------|
| Flask Blueprints + Application Factory | Extended |
| Jinja2 templates | ✅ |
| WTForms for all forms | ✅ |
| Cookies & Sessions | ✅ |
| JWT-style auth (Flask-Login) | ✅ |
| CRUD for all entities (role-based) | ✅ |
| One-to-Many: User → Borrowings, Book → Borrowings | ✅ |
| One-to-One: User ↔ UserProfile | Extended |
| Many-to-Many: Books ↔ Genres, Users ↔ FavoriteGenres | Extended |
| Flask-Migrate (automatic migrations) | Extended |
| Admin panel with full access | ✅ |
| Admin email sending (Flask-Mail) | Extended |

---

## 🚀 Setup & Run

### 1. Clone / unzip the project

```bash
cd library_flask
```

### 2. Create and activate virtual environment

```bash
# Windows
python -m venv venv
venv\Scripts\activate

# macOS / Linux
python3 -m venv venv
source venv/bin/activate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure environment

Edit `.env` file (already created with defaults):
```
SECRET_KEY=your-very-secret-key-change-in-production
DATABASE_URL=sqlite:///library.db
```

For email sending (optional), configure SMTP:
```
MAIL_SERVER=smtp.gmail.com
MAIL_PORT=587
MAIL_USE_TLS=True
MAIL_USERNAME=your-email@gmail.com
MAIL_PASSWORD=your-app-password
MAIL_DEFAULT_SENDER=your-email@gmail.com
```

### 5. Initialize database with migrations

```bash
# Initialize migration folder (first time only)
flask db init

# Create migration
flask db migrate -m "Initial migration"

# Apply migration
flask db upgrade
```

Or skip migrations and create tables directly:
```bash
python seed.py   # creates tables AND seeds sample data
```

### 6. Run the application

```bash
python run.py
```

Open: **http://localhost:5000**

---

## 👤 Default Accounts

After running `seed.py`:

| Username | Password | Role |
|----------|----------|------|
| `admin` | `admin123` | Administrator |
| `john_doe` | `user123` | Regular user |
| `jane_smith` | `user123` | Regular user |

---

## 🗂️ Project Structure

```
library_flask/
├── app/
│   ├── __init__.py          # Application Factory
│   ├── models.py            # SQLAlchemy models (User, Book, Borrowing, Genre, UserProfile)
│   ├── auth/                # Blueprint: login, register, profile
│   │   ├── __init__.py
│   │   ├── forms.py
│   │   └── routes.py
│   ├── books/               # Blueprint: CRUD for books
│   │   ├── __init__.py
│   │   ├── forms.py
│   │   └── routes.py
│   ├── borrowings/          # Blueprint: borrow & return books
│   │   ├── __init__.py
│   │   ├── forms.py
│   │   └── routes.py
│   ├── admin/               # Blueprint: admin panel
│   │   ├── __init__.py
│   │   ├── forms.py
│   │   └── routes.py
│   ├── main/                # Blueprint: homepage, error handlers
│   │   ├── __init__.py
│   │   └── routes.py
│   └── templates/           # Jinja2 HTML templates
│       ├── base.html
│       ├── main/
│       ├── auth/
│       ├── books/
│       ├── borrowings/
│       ├── admin/
│       └── errors/
├── config.py                # Config classes (Dev, Prod, Test)
├── run.py                   # Entry point
├── seed.py                  # Database seeding script
├── requirements.txt
└── .env                     # Environment variables
```

---

## 📊 Database Schema

### Relationships
- **User → UserProfile**: One-to-One
- **User → Borrowings**: One-to-Many
- **Book → Borrowings**: One-to-Many
- **Books ↔ Genres**: Many-to-Many (via `book_genres` table)
- **Users ↔ Genres** (favorites): Many-to-Many (via `user_favorite_genres` table)

---

## 🔑 Roles & Permissions

### Administrator
- Full CRUD on books, genres, users
- View all borrowings, return any book
- Send emails to users
- Admin panel at `/admin`

### Regular User
- Browse book catalog
- Borrow and return own books
- View personal borrowing history
- Edit own profile

---

## 🔒 Sessions & Cookies

- **Session**: stores `user_role` and `username` on login
- **Cookie**: `last_login_user` cookie set on login (30 days)
- **Flask-Login**: manages secure session-based authentication

---

## 🔄 Migrations

Manual mode (basic):
```bash
flask db init       # only once
flask db migrate -m "description"
flask db upgrade
flask db downgrade  # rollback
```

Auto mode (Alembic tracks model changes automatically on each `migrate`).

---

## 📧 Email (Extended Level)

1. Configure SMTP in `.env`
2. Go to Admin → Users → any user → Send Email
3. Fill in subject and body, click Send

> For Gmail: create an App Password at https://myaccount.google.com/apppasswords

---

## 🛠️ Tech Stack

- **Flask 3.0** – web framework
- **Flask-SQLAlchemy** – ORM
- **Flask-Migrate** (Alembic) – database migrations
- **Flask-Login** – authentication
- **Flask-WTF / WTForms** – forms with CSRF protection
- **Flask-Mail** – email sending
- **bcrypt** – password hashing
- **SQLite** – database
- **Jinja2** – templating
- **Bootstrap 5** – frontend UI
