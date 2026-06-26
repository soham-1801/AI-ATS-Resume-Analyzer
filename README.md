# AI Resume ATS 🚀

[![FastAPI](https://img.shields.io/badge/FastAPI-005571?style=for-the-badge&logo=fastapi)](https://fastapi.tiangolo.com/)
[![React](https://img.shields.io/badge/React-20232A?style=for-the-badge&logo=react&logoColor=61DAFB)](https://react.dev/)
[![Tailwind CSS v4](https://img.shields.io/badge/Tailwind_CSS-38B2AC?style=for-the-badge&logo=tailwind-css&logoColor=white)](https://tailwindcss.com/)
[![PostgreSQL](https://img.shields.io/badge/PostgreSQL-316192?style=for-the-badge&logo=postgresql&logoColor=white)](https://www.postgresql.org/)
[![spaCy](https://img.shields.io/badge/spaCy-09A3D5?style=for-the-badge&logo=spacy&logoColor=white)](https://spacy.io/)
[![Gemini](https://img.shields.io/badge/Gemini_AI-8E75C2?style=for-the-badge&logo=google&logoColor=white)](https://deepmind.google/technologies/gemini/)
[![Docker](https://img.shields.io/badge/Docker-2496ED?style=for-the-badge&logo=docker&logoColor=white)](https://www.docker.com/)

An intelligent, AI-powered Applicant Tracking System (ATS) platform designed to parse resumes, validate alignments against target job descriptions using advanced Natural Language Processing (NLP) math models, generate STAR-method optimizations using Gemini 1.5 Flash, and stream scored PDF matching evaluation reports.

---

## 📖 Table of Contents
1. [Project Overview](#-project-overview)
2. [Key Features](#-key-features)
3. [System Architecture](#-system-architecture)
4. [Tech Stack](#-tech-stack)
5. [Environment Variables](#-environment-variables)
6. [API Endpoints](#-api-endpoints)
7. [Installation & Setup](#-installation--setup)
8. [Docker & Containerized Launch](#-docker--containerized-launch)
9. [Production Cloud Deployment](#-production-cloud-deployment)
10. [Screenshots & Visuals](#-screenshots--visuals)
11. [Future Roadmap & Security](#-future-roadmap--security)

---

## 🌟 Project Overview

Traditional Applicant Tracking Systems filter out candidates based on strict keyword matches, often ignoring relevant context, synonyms, and semantic alignments. 

**AI Resume ATS** bridges this gap:
* **Hybrid Score Math**: It evaluates resumes against job descriptions using both **TF-IDF + Cosine Similarity** (for keyword overlap) and **spaCy Natural Language Processing** (for contextual semantic similarity).
* **Gemini suggestions**: Leverages Google Generative AI (`gemini-1.5-flash`) to generate structured recommendations highlighting summary improvements, missing keywords, and profile formatting tips.
* **STAR Rewrite assistant**: Integrates a section rewriter (summary, experience, projects, skills) that generates polished, metric-driven achievements.

---

## ✨ Key Features

* **Secure Authentication**: JWT token-based authentication with "Remember Me" options (caching tokens in `localStorage` or `sessionStorage`).
* **Resume Document Parser**: PDF/DOCX upload parser (`pdfplumber` & `python-docx`) with strict size limits (5MB) and type validations.
* **Axios Upload Progress**: Visual SVG circular loaders indicating real-time file upload percentages.
* **Interactive Score Dashboard**: Circular SVG ATS match gauges, animated keyword/semantic progress bars, and recent match trends using Recharts.
* **AI Optimization Suite**: Dynamic suggestions split into Summary Enhancements, checklists of Project Roadmaps, and General Formatting recommendations.
* **STAR Method Rewriter**: In-app AI drawer assisting candidates in rewriting bullet points to showcase business impact.
* **Premium PDF Report Generator**: Generates scored, colored assessment reports using ReportLab, streamed as secure authenticated byte-streams.

---

## 📐 System Architecture

The diagram below outlines the flow of data across the client interface, API gateway, NLP evaluation pipeline, and AI service providers:

```text
┌────────────────────────┐
│   React Single-Page    │ ◄─── Auth Token interceptor
│   Vite Frontend Client  │ ─── Authenticated Axios Requests ──┐
└────────────────────────┘                                     │
                                                               ▼
┌────────────────────────────────────────────────────────────────┐
│                   FastAPI Backend API Gateway                  │
└────────────────────────────────────────────────────────────────┘
    │           │                      │                  │
    ▼           ▼                      ▼                  ▼
┌───────┐ ┌───────────┐         ┌───────────────┐ ┌──────────────┐
│  SQL  │ │    NLP    │         │    Report     │ │  Gemini 1.5  │
│  ORM  │ │  Matcher  │         │   Generator   │ │  Flash API   │
└───────┘ └───────────┘         └───────────────┘ └──────────────┘
    │           │                      │                  │
    │     - TF-IDF Cosine        - ReportLab PDF    - Recommendations
    │     - spaCy Semantic         Byte-stream      - STAR rewrites
    ▼           ▼                      ▼                  ▼
┌───────┐ ┌───────────┐         ┌───────────────┐ ┌──────────────┐
│ Post- │ │ en_core_  │         │  Persistent   │ │   Google     │
│ greSQL│ │  web_sm   │         │ Volume Disk   │ │ Generative   │
│  DB   │ │  spaCy    │         │ (Local Files) │ │   AI Cloud   │
└───────┘ └───────────┘         └───────────────┘ └──────────────┘
```

---

## 🛠️ Tech Stack

### Frontend
* **Core**: React 18, Vite
* **Styling**: Tailwind CSS v4, Lucide Icons, Custom Glassmorphic layouts
* **Libraries**: React Router DOM (v7 SPA routing), React Hook Form, Axios, Recharts (Data Visualizations)

### Backend
* **Core**: FastAPI (v0.110), Uvicorn (v0.28)
* **NLP & Parsing**: spaCy (`en_core_web_sm`), Scikit-Learn (`TfidfVectorizer`), `pdfplumber`, `python-docx`
* **AI & Suggestions**: Google Generative AI API (`gemini-1.5-flash`)
* **Reports & DB**: ReportLab (PDF Generation), SQLAlchemy (ORM), Psycopg2 (PostgreSQL Connector)

---

## 🔑 Environment Variables

### Backend Configuration (`backend/.env`)
```env
DATABASE_URL=postgresql://postgres:password@localhost:5432/ats_db
GEMINI_API_KEY=AIzaSyD-Your-Gemini-Key-Here
SECRET_KEY=your_super_secret_jwt_signature_key
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=60
CORS_ALLOWED_ORIGINS=https://your-app.vercel.app,http://localhost:5173
```

### Frontend Configuration (`frontend/.env`)
```env
VITE_API_BASE_URL=https://your-backend.onrender.com/api
```

---

## 📡 API Endpoints

### 🔐 Authentication (`/api/auth`)
| Method | Endpoint | Description | Auth Required |
| :--- | :--- | :--- | :---: |
| `POST` | `/auth/register` | Registers a new candidate user profile. | No |
| `POST` | `/auth/login` | Authenticates details and returns a JWT access token. | No |
| `GET` | `/auth/me` | Retrieves details of the logged-in user session. | **Yes** |

### 📄 Resumes (`/api/resume`)
| Method | Endpoint | Description | Auth Required |
| :--- | :--- | :--- | :---: |
| `POST` | `/resume/upload` | Uploads and extracts text from a PDF/DOCX file. | **Yes** |
| `GET` | `/resume/all` | Lists all resumes uploaded by the current user. | **Yes** |
| `GET` | `/resume/{id}` | Retrieves parsed details of a specific resume. | **Yes** |
| `DELETE` | `/resume/{id}` | Deletes a resume record and its physical storage file. | **Yes** |

### 💼 Job Descriptions (`/api/job-description`)
| Method | Endpoint | Description | Auth Required |
| :--- | :--- | :--- | :---: |
| `POST` | `/job-description/` | Saves a new target job description. | **Yes** |
| `GET` | `/job-description/all` | Lists all job descriptions saved by the user. | **Yes** |
| `DELETE` | `/job-description/{id}` | Deletes a job description. | **Yes** |

### 📊 ATS Engine & AI (`/api/ats` & `/api/ai`)
| Method | Endpoint | Description | Auth Required |
| :--- | :--- | :--- | :---: |
| `POST` | `/ats/analyze` | Executes NLP score comparison & generates AI recommendations. | **Yes** |
| `GET` | `/ats/results/{resume_id}` | Lists past comparison results for a specific resume. | **Yes** |
| `GET` | `/ats/results/{result_id}/pdf` | Generates and streams the PDF evaluation report file. | **Yes** |
| `POST` | `/ai/rewrite` | Rewrites a resume section using STAR methodologies. | **Yes** |

---

## 🚀 Installation & Setup

### Prerequisites
* Python 3.11+
* Node.js 20+
* PostgreSQL DB running locally or hosted

### 1. Backend Setup
Navigate to the backend folder, configure virtual environments, and install libraries:
```bash
# Clone the repository
git clone https://github.com/your-username/AI-Resume-ATS.git
cd AI-Resume-ATS

# Configure virtual environment
cd backend
python -m venv venv
source venv/Scripts/activate  # On macOS/Linux: source venv/bin/activate

# Install requirements (includes FastAPI, SQLAlchemy, spaCy, ReportLab)
pip install -r ../requirements.txt

# Download required spaCy NLP model
python -m spacy download en_core_web_sm

# Configure environment variables
# Copy or create a .env file based on the table in Section 5
```
Run development server:
```bash
uvicorn app.main:app --reload
```
*Backend runs locally at [http://localhost:8000](http://localhost:8000). Interactive Swagger documentation is available at `/docs`.*

### 2. Frontend Setup
Navigate to the frontend folder, install packages, and spin up Vite:
```bash
cd ../frontend
npm install
npm run dev
```
*Frontend runs locally at [http://localhost:5173](http://localhost:5173).*

---

## 🐳 Docker & Containerized Launch

Run the database database server, backend API gateway, and static assets Nginx web server in a single command using Docker Compose:

1. Create a root `.env` file containing your `GEMINI_API_KEY`.
2. Launch the services:
   ```bash
   docker-compose up --build -d
   ```
3. Access points:
   * **Frontend Client**: [http://localhost:3000](http://localhost:3000) (Nginx with client fallbacks)
   * **Backend API Gateway**: [http://localhost:8000](http://localhost:8000) (Linked PostgreSQL db container)
   * **Swagger Docs**: [http://localhost:8000/docs](http://localhost:8000/docs)

---

## 🌐 Production Cloud Deployment

### Backend (Render Deployment)
1. Commit and push the project to a GitHub repository.
2. Go to [Render Dashboard](https://dashboard.render.com) and create a new **Blueprint** project.
3. Import the repository. Render will parse the `render.yaml` config file.
4. Input your `GEMINI_API_KEY` when prompted and click deploy.
5. Render will automatically launch a PostgreSQL database and host the FastAPI application, mounting a persistent volume disk at `/workspace/backend/uploads` to store resume documents.

### Frontend (Vercel Deployment)
1. Go to [Vercel Dashboard](https://vercel.com) and create a **New Project**.
2. Import the repository and select `frontend` as the root directory.
3. Configure the build commands:
   * **Framework Preset**: Vite
   * **Build Command**: `npm run build`
   * **Output Directory**: `dist`
4. Define the Environment Variable:
   * `VITE_API_BASE_URL` = `<your-render-backend-url>/api`
5. Click **Deploy**. Vercel will bundle the SPA assets and configure path routing fallbacks automatically using the `vercel.json` rules.
6. Return to Render and update `CORS_ALLOWED_ORIGINS` to match your active Vercel URL.

---

## 📸 Screenshots & Visuals

### 1. Login Workspace
> *Clean form interfaces supporting authentication tokens, jwt storage, validation, and session remember-me toggles.*
`![Login Workspace](https://via.placeholder.com/800x450/0b0f19/a5b4fc?text=ATS+Login+Portal)`

### 2. Resume Upload & Progress
> *Interactive drag-and-drop workspace using react-dropzone. Supports DOCX/PDF validations, size checks, and Axios-based SVG radial loader percentages.*
`![Resume Upload Workspace](https://via.placeholder.com/800x450/0b0f19/a5b4fc?text=Drag-and-Drop+Upload+Zone)`

### 3. ATS Score Dashboard
> *Dashboard containing circular SVG score gauge, animated progress metrics (Keyword vs Semantic), skill maps, and parsed Gemini recommendations.*
`![ATS Score Dashboard](https://via.placeholder.com/800x450/0b0f19/a5b4fc?text=ATS+Analysis+Results)`

### 4. STAR Rewrite Drawer
> *AI assistant drawer matching Gemini content generation models, letting users paste and rewrite resume achievements in-app.*
`![STAR Rewrite Drawer](https://via.placeholder.com/800x450/0b0f19/a5b4fc?text=Gemini+AI+STAR+Rewriter)`

---

## 🚀 Future Roadmap & Security

1. **Alembic Database Migrations**: Move away from startup `metadata.create_all` database seeding to protect candidate data structures during backend updates.
2. **API Rate Limiting**: Introduce `slowapi` throttling limits on auth endpoints and analysis routes to prevent script flooding and limit model token expenditures.
3. **Cloud Storage Adapter (AWS S3)**: Move physical resume uploads to AWS S3 to support stateless container scaling.
