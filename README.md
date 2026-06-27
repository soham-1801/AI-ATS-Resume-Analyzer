# AI ATS Resume Analyzer

A full-stack Applicant Tracking System (ATS) built with React and FastAPI for resume evaluation, ATS scoring, resume analysis using the Google Gemini API, and PDF report generation.

![Python](https://img.shields.io/badge/Python-3.11+-3776AB?logo=python&logoColor=white)
![FastAPI](https://img.shields.io/badge/FastAPI-009688?logo=fastapi&logoColor=white)
![React](https://img.shields.io/badge/React-61DAFB?logo=react&logoColor=black)
![Vite](https://img.shields.io/badge/Vite-646CFF?logo=vite&logoColor=white)
![Docker](https://img.shields.io/badge/Docker-2496ED?logo=docker&logoColor=white)
![SQLite](https://img.shields.io/badge/SQLite-003B57?logo=sqlite&logoColor=white)
![PostgreSQL](https://img.shields.io/badge/PostgreSQL-4169E1?logo=postgresql&logoColor=white)

## Overview

...

## Key Features

...

## Technology Stack

...

## System Architecture

```text
                    +----------------------+
                    |   React Frontend     |
                    +----------+-----------+
                               |
                         HTTPS / REST API
                               |
                               ▼
                    +----------------------+
                    |   FastAPI Backend    |
                    +----------+-----------+
                               |
              +----------------+----------------+
              |                |                |
              ▼                ▼                ▼
      Authentication     ATS Services     AI Services
              |                |                |
              +--------+-------+----------------+
                       |
                       ▼
             SQLAlchemy ORM Layer
                       |
                       ▼
          SQLite / PostgreSQL Database

                       |
                       ▼
               Google Gemini API
```

The application follows a layered architecture that separates presentation, API routing, business logic, and data persistence. The frontend communicates with the backend through REST APIs, while backend services coordinate resume processing, authentication, ATS evaluation, and AI-assisted recommendations.

---

## Backend Architecture

The backend is organized into modular components, each with a specific responsibility.

| Layer     | Responsibility                                    |
| --------- | ------------------------------------------------- |
| API       | Defines REST endpoints and request handling       |
| Services  | Implements business logic and workflow processing |
| Models    | SQLAlchemy ORM models for database entities       |
| Schemas   | Request and response validation using Pydantic    |
| Database  | Connection management and ORM configuration       |
| Utilities | Security, constants, and shared helper functions  |

### Backend Modules

* **Authentication**

  * User registration
  * User login
  * JWT authentication
  * OAuth authentication
  * Password reset workflow

* **Resume Processing**

  * Resume upload
  * Resume parsing
  * Text extraction
  * File validation

* **ATS Analysis**

  * Resume and job description comparison
  * Similarity scoring
  * Skills analysis
  * Report generation

* **AI Services**

  * Resume analysis
  * Resume improvement suggestions
  * Resume rewriting assistance

---

## Frontend Architecture

The frontend is built as a Single Page Application (SPA) using React and Vite.

Primary responsibilities include:

* User authentication
* Resume upload
* Job description management
* ATS result visualization
* Dashboard analytics
* AI interaction pages
* PDF report downloads

The frontend communicates with the backend using HTTP requests and renders application state through reusable React components.

---

## Database Design

The application stores data using SQLAlchemy ORM models.

| Model              | Purpose                                        |
| ------------------ | ---------------------------------------------- |
| User               | User accounts and authentication information   |
| Resume             | Uploaded resume metadata and extracted content |
| JobDescription     | Job descriptions submitted for analysis        |
| ATSResult          | ATS evaluation results and generated feedback  |
| PasswordResetToken | Password reset tokens with expiration support  |

Database migrations are managed using Alembic.

---

## Project Structure

```text
AI-ATS-Resume-Analyzer/
│
├── backend/
│   ├── alembic/
│   ├── app/
│   │   ├── api/
│   │   ├── database/
│   │   ├── models/
│   │   ├── schemas/
│   │   ├── services/
│   │   └── utils/
│   ├── uploads/
│   ├── requirements.txt
│   ├── Dockerfile
│   └── alembic.ini
│
├── frontend/
│   ├── public/
│   ├── src/
│   │   ├── assets/
│   │   ├── components/
│   │   ├── contexts/
│   │   ├── pages/
│   │   └── utils/
│   ├── package.json
│   ├── Dockerfile
│   └── vite.config.js
│
├── docker-compose.yml
├── render.yaml
└── README.md
```
---

## Prerequisites

Before running the application, ensure the following software is installed:

| Software            | Recommended Version |
| ------------------- | ------------------- |
| Python              | 3.11 or later       |
| Node.js             | 18 or later         |
| npm                 | Latest              |
| Docker *(Optional)* | Latest              |
| Git                 | Latest              |

---

## Installation

### 1. Clone the Repository

```bash
git clone https://github.com/soham-1801/AI-ATS-Resume-Analyzer.git
cd AI-ATS-Resume-Analyzer
```

---

### 2. Backend Setup

```bash
cd backend

python -m venv venv

# Windows
venv\Scripts\activate

# Linux / macOS
source venv/bin/activate

pip install -r requirements.txt
```

---

### 3. Frontend Setup

```bash
cd frontend

npm install
```

---

## Environment Variables

Create a `.env` file inside the **backend** directory.

```env
DATABASE_URL=<YOUR_DATABASE_URL>

SECRET_KEY=<YOUR_SECRET_KEY>

GEMINI_API_KEY=<YOUR_API_KEY>

ENVIRONMENT=development

CORS_ALLOWED_ORIGINS=<YOUR_ALLOWED_ORIGINS>

GOOGLE_CLIENT_ID=<YOUR_GOOGLE_CLIENT_ID>
GOOGLE_CLIENT_SECRET=<YOUR_GOOGLE_CLIENT_SECRET>

GITHUB_CLIENT_ID=<YOUR_GITHUB_CLIENT_ID>
GITHUB_CLIENT_SECRET=<YOUR_GITHUB_CLIENT_SECRET>

APPLE_CLIENT_ID=<YOUR_APPLE_CLIENT_ID>
```

For the frontend, create a `.env` file inside the **frontend** directory.

```env
VITE_API_BASE_URL=<YOUR_API_BASE_URL>
```

---

## Running the Application

### Start the Backend

```bash
cd backend

uvicorn app.main:app --reload
```

The backend server will start on the configured host and port.

---

### Start the Frontend

```bash
cd frontend

npm run dev
```

The frontend development server will connect to the backend using the configured API base URL.

---

## Docker

Build the containers:

```bash
docker-compose build
```

Start the application:

```bash
docker-compose up -d
```

Stop the application:

```bash
docker-compose down
```

---

## REST API Overview

| Module          | Purpose                                                               |
| --------------- | ----------------------------------------------------------------------|
| Authentication  | User registration, login, OAuth, password reset, token management     |
| Resume          | Resume upload, storage, retrieval, and parsing                        |
| Job Description | Create and manage job descriptions                                    |
| ATS             | Resume evaluation, scoring, and report generation                     |
| AI              | Resume analysis, resume improvement suggestions, and resume rewriting |
| Dashboard       | Analytics and historical results                                      |
| Health          | Application health status                                             |

Interactive API documentation is available through the FastAPI documentation endpoints when the backend is running.

---

## Testing

Run the backend test suite:

```bash
cd backend

pytest
```

The project includes tests for authentication and password validation workflows.

---

## Security Features

The application includes multiple security mechanisms implemented across the authentication and file-processing workflows.

* JWT-based authentication
* Access and refresh token support
* Password hashing using bcrypt
* OAuth authentication
* Password reset with expiring hashed tokens
* Secure environment variable configuration
* File type validation for resume uploads
* File size validation
* Rate limiting for API requests
* Database transaction rollback for failed operations

---

## Screenshots

### Login

<!-- Add Screenshot -->

### Dashboard

<!-- Add Screenshot -->

### Resume Upload

<!-- Add Screenshot -->

### ATS Analysis

<!-- Add Screenshot -->

### AI Resume Suggestions

<!-- Add Screenshot -->

---

## Deployment

The repository includes configuration files for multiple deployment approaches.

| Platform | Configuration        |
| -------- | -------------------- |
| Docker   | `docker-compose.yml` |
| Backend  | `render.yaml`        |
| Frontend | `vercel.json`        |

Deployment configuration files are included for Docker, Render, and Vercel.

---

## Future Improvements

Potential enhancements include:

* Expand automated test coverage
* Support additional resume document formats
* Improve analytics and reporting capabilities
* Enhance AI-assisted resume recommendations
* Add continuous integration and deployment workflows

---

## Author

**Soham Mangroliya**

GitHub: https://github.com/soham-1801

---

## License

This project currently does not include an explicit license.
