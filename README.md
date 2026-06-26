# Blogging Platform API

A backend REST API for a blogging platform built with Django, Django REST Framework, PostgreSQL, JWT authentication, Swagger/OpenAPI documentation, automated tests, and Docker.

The project includes user registration, JWT login, user profiles, blog posts, categories, comments, permissions, pagination, search, filtering, ordering, API documentation, automated tests, and Docker Compose setup.

---

## Tech Stack

* Python 3.12
* Django 6
* Django REST Framework
* PostgreSQL
* Simple JWT
* Django Filter
* drf-spectacular
* Docker
* Docker Compose

---

## Features

### Authentication and Users

* User registration
* JWT authentication
* JWT token refresh
* Current authenticated user endpoint
* User profile endpoint
* Profile update
* Change password
* Password validation
* Email validation during registration 
* Like and unlike posts 
* Likes count for posts 
* Current user like status
* Current user posts endpoint 
* Current user drafts endpoint 
* Publish and unpublish posts 
* Draft visibility logic
* Current user dashboard with activity statistics

### Blog Functionality

* Create, read, update, and delete blog posts
* Create and manage categories
* Create, read, update, and delete comments
* Automatic assignment of post author
* Automatic assignment of comment author

### Permissions

* Anonymous users can read public data
* Only authenticated users can create posts and comments
* Only the author can update or delete their own posts
* Only the author can update or delete their own comments

### API Improvements

* Pagination for posts
* Search by post title, content, and author username
* Filtering by category, author, and publication status
* Ordering by title, creation date, and update date

### Documentation and Testing

* Swagger UI documentation
* ReDoc documentation
* OpenAPI schema
* Automated API tests

### Docker

* Dockerized Django application
* Dockerized PostgreSQL database
* Docker Compose setup
* Automatic database migrations on container startup

### Markdown
* Bookmark and unbookmark posts 
* Current user bookmarks endpoint 
* Bookmark count and bookmark status for posts
---

## Project Structure

```text
DjangoProject/
├── accounts/
│   ├── admin.py
│   ├── models.py
│   ├── serializers.py
│   ├── tests.py
│   ├── urls.py
│   └── views.py
│
├── blog/
│   ├── admin.py
│   ├── models.py
│   ├── permissions.py
│   ├── serializers.py
│   ├── tests.py
│   ├── urls.py
│   └── views.py
│
├── djangoproject/
│   ├── settings.py
│   ├── urls.py
│   ├── asgi.py
│   └── wsgi.py
│
├── Dockerfile
├── docker-compose.yml
├── entrypoint.sh
├── .dockerignore
├── .env.example
├── requirements.txt
├── manage.py
├── requests.http
└── README.md
```

---

## API Endpoints

### Authentication and Accounts

| Method | Endpoint                         | Description                       |
|--------|----------------------------------|-----------------------------------|
| POST   | `/api/accounts/register/`        | Register a new user               |
| POST   | `/api/token/`                    | Get JWT access and refresh tokens |
| POST   | `/api/token/refresh/`            | Refresh JWT access token          |
| GET    | `/api/accounts/me/`              | Get current authenticated user    |
| GET    | `/api/accounts/profile/`         | Get current user profile          |
| GET    | `/api/accounts/me/posts/`        | Get all of user's posts           |
| GET    | `/api/accounts/me/dashboard/`    | Get user's dashboard              |
| GET    | `/api/accounts/me/drafts/`       | Get all of user's drafts          |
| PATCH  | `/api/accounts/profile/`         | Update current user profile       |
| POST   | `/api/accounts/change-password/` | Change user password              |

### Posts

| Method | Endpoint                      | Description                   |
|--------|-------------------------------|-------------------------------|
| GET    | `/api/posts/`                 | Get paginated list of posts   |
| POST   | `/api/posts/`                 | Create a new post             |
| POST   | `/api/posts/{id}/like/`       | Add a like to a post          |
| POST   | `/api/posts/{id}/unlike/`     | Delete a like from a post     |
| POST   | `/api/posts/{id}/bookmark/`   | Add a bookmark to a post      |
| POST   | `/api/posts/{id}/unbookmark/` | Delete a bookmark from a post |
| POST   | `/api/posts/{id}/publish/`    | Publish post                  |
| POST   | `/api/posts/{id}/unpublish/`  | Unpublish post                |
| GET    | `/api/accounts/me/bookmarks/` | Get user's bookmarks          |
| GET    | `/api/posts/{id}/`            | Get post details              |
| PATCH  | `/api/posts/{id}/`            | Update own post               |
| DELETE | `/api/posts/{id}/`            | Delete own post               |


### Categories

| Method | Endpoint                | Description            |
|--------|-------------------------|------------------------|
| GET    | `/api/categories/`      | Get list of categories |
| POST   | `/api/categories/`      | Create category        |
| GET    | `/api/categories/{id}/` | Get category details   |
| PATCH  | `/api/categories/{id}/` | Update category        |
| DELETE | `/api/categories/{id}/` | Delete category        |

### Comments

| Method | Endpoint              | Description          |
|--------|-----------------------|----------------------|
| GET    | `/api/comments/`      | Get list of comments |
| POST   | `/api/comments/`      | Create a comment     |
| GET    | `/api/comments/{id}/` | Get comment details  |
| PATCH  | `/api/comments/{id}/` | Update own comment   |
| DELETE | `/api/comments/{id}/` | Delete own comment   |

---

## Search, Filtering, Ordering and Pagination

### Search Posts

```http
GET /api/posts/?search=django
```

Search is available by:

* title
* content
* author username

### Filter Posts

```http
GET /api/posts/?category=1
GET /api/posts/?author=2
GET /api/posts/?is_published=true
```

### Order Posts

```http
GET /api/posts/?ordering=title
GET /api/posts/?ordering=-created_at
GET /api/posts/?ordering=updated_at
```

### Pagination

```http
GET /api/posts/?page=1
GET /api/posts/?page=2
```

Example paginated response:

```json
{
  "count": 10,
  "next": "http://127.0.0.1:8000/api/posts/?page=2",
  "previous": null,
  "results": []
}
```

---

## API Documentation

Swagger UI:

```text
http://127.0.0.1:8000/api/docs/
```

ReDoc:

```text
http://127.0.0.1:8000/api/redoc/
```

OpenAPI schema:

```text
http://127.0.0.1:8000/api/schema/
```

---

## Environment Variables

The project uses environment variables for configuration.

Create a `.env` file for local Windows/PyCharm development or `.env.docker` for Docker development.

Example:

```env
SECRET_KEY=your-secret-key-here
DEBUG=True

DB_NAME=blogging_api_db
DB_USER=postgres
DB_PASSWORD=postgres
DB_HOST=db
DB_PORT=5432
```

For local Windows/PyCharm development:

```env
DB_HOST=localhost
DB_PORT=5432
```

For Docker development:

```env
DB_HOST=db
DB_PORT=5432
```

The `.env` and `.env.docker` files should not be committed to Git.

The `.env.example` file is included as a safe template.

---

## Run Locally Without Docker

### 1. Clone the repository

```bash
git clone https://github.com/your-username/your-repository-name.git
cd your-repository-name
```

### 2. Create virtual environment

```bash
python -m venv .venv
```

### 3. Activate virtual environment

Windows:

```bash
.venv\Scripts\activate
```

Linux/macOS:

```bash
source .venv/bin/activate
```

### 4. Install dependencies

```bash
pip install -r requirements.txt
```

### 5. Create `.env`

Create a `.env` file based on `.env.example`.

Example for local PostgreSQL:

```env
SECRET_KEY=your-secret-key-here
DEBUG=True

DB_NAME=blogging_api_db
DB_USER=postgres
DB_PASSWORD=your-local-postgres-password
DB_HOST=localhost
DB_PORT=5432
```

### 6. Apply migrations

```bash
python manage.py migrate
```

### 7. Create superuser

```bash
python manage.py createsuperuser
```

### 8. Run development server

```bash
python manage.py runserver
```

Application will be available at:

```text
http://127.0.0.1:8000/
```

---

## Run With Docker

### 1. Create `.env.docker`

Create a `.env.docker` file in the project root:

```env
SECRET_KEY=your-secret-key-here
DEBUG=True

DB_NAME=blogging_api_db
DB_USER=postgres
DB_PASSWORD=postgres
DB_HOST=db
DB_PORT=5432
```

### 2. Start containers

```bash
docker compose up --build
```

This command starts:

* Django application container
* PostgreSQL database container

The application will be available at:

```text
http://127.0.0.1:8000/
```

Swagger documentation:

```text
http://127.0.0.1:8000/api/docs/
```

### 3. Create superuser inside Docker

```bash
docker compose exec web python manage.py createsuperuser
```

### 4. Run migrations manually if needed

```bash
docker compose exec web python manage.py migrate
```

### 5. Stop containers

```bash
docker compose down
```

### 6. Stop containers and remove database volume

```bash
docker compose down -v
```

Use this command only when you want to delete the Docker PostgreSQL database.

---

## Run Tests

### Without Docker

```bash
python manage.py test
```

### With Docker

```bash
docker compose exec web python manage.py test
```

The project includes tests for:

* user registration
* invalid email validation
* weak password validation
* JWT login
* current user endpoint
* user profile endpoint
* profile update
* post creation
* anonymous access restrictions
* author permissions
* comment creation
* comment permissions
* post search
* post filtering

---

## Authentication Flow

### 1. Register User

```http
POST /api/accounts/register/
Content-Type: application/json

{
  "username": "testuser",
  "email": "testuser@example.com",
  "password": "StrongPassword123!"
}
```

### 2. Get JWT Token

```http
POST /api/token/
Content-Type: application/json

{
  "username": "testuser",
  "password": "StrongPassword123!"
}
```

Example response:

```json
{
  "refresh": "refresh_token_here",
  "access": "access_token_here"
}
```

### 3. Use Access Token

```http
Authorization: Bearer access_token_here
```

Example protected request:

```http
GET /api/accounts/me/
Authorization: Bearer access_token_here
```

---

## Example Post Request

```http
POST /api/posts/
Content-Type: application/json
Authorization: Bearer access_token_here

{
  "title": "My first post",
  "content": "This is the content of my first post.",
  "category": null,
  "is_published": true
}
```

The author is assigned automatically based on the authenticated user.

---

## Docker Architecture

```text
Browser / API Client
        |
        | http://127.0.0.1:8000
        |
Docker web container
Django REST API
        |
        | db:5432
        |
Docker db container
PostgreSQL
```

The Django container connects to PostgreSQL using:

```env
DB_HOST=db
DB_PORT=5432
```

The PostgreSQL container is exposed to the host machine on port:

```text
5433
```

This prevents conflicts with a local PostgreSQL installation on port `5432`.

---

## Current Status

Implemented:

* REST API with Django REST Framework
* PostgreSQL database
* JWT authentication
* User registration
* User profile management
* Password change
* Posts, categories, and comments
* Object-level permissions
* Search, filtering, ordering, and pagination
* Swagger and ReDoc documentation
* Automated API tests
* Docker and Docker Compose setup
* Post likes system 
* Post bookmarks system
* Draft and publish system
* User dashboard statistics endpoint
---

## Future Improvements

Planned improvements:

* Add endpoint for current user's posts
* Add image upload for posts
* Add frontend with Django templates
* Add production setup with Gunicorn
* Add deployment configuration
* Add CI pipeline for automated tests

---

## Author

Created as a backend portfolio project for learning Django REST Framework, PostgreSQL, JWT authentication, testing, Swagger documentation, and Docker.
