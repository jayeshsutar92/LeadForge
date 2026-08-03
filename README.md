# LeadForge — Signal Layer (v1.0)

LeadForge is a B2B SaaS lead discovery and conversion intelligence platform built for agency owners, freelance web developers, and sales teams. It surfaces social-first businesses (Instagram/Facebook) that lack dedicated websites or direct online ordering channels, calculates rule-based Opportunity Scores (0–100), provides category-tailored design recommendations, and generates client-ready proposal drafts.

---

## Key Features

- 🎯 **Lead Discovery & Multi-Filter Search**: Search by business name, city, country, or category. Filter by website status (`Missing` / `Has`), follower counts, minimum opportunity scores, and sort by relevance or metrics.
- 📊 **Signal Layer & Opportunity Score Gauge**: Automated scoring engine assessing social audience size, engagement rate, post frequency, and missing online ordering capabilities.
- 🎨 **Category Design Themes & Budget Estimates**: Pre-configured palettes, suggested site sections, and estimated price ranges customized per business category.
- 📄 **Client Proposal Preview**: Generate instant proposal drafts complete with executive summaries, scope deliverables, color palettes, and browser print-to-PDF support.
- 📈 **Platform KPIs & Insights**: Interactive dashboard displaying missing website percentages, high-opportunity lead counts, top weekly opportunities, and category breakdown charts.
- 📜 **Search History Trail**: Automatically tracks user search queries and filter parameters with one-click query re-run and trail clearing options.
- 🔐 **Dual-Mode Authentication**: JWT authentication with HTTP-only cookie support and Bearer token headers, backed by `bcrypt` password encryption and a brute-force lockout guard.

---

## Tech Stack

### Frontend
- **Framework & Runtime**: React 18, React Router v6
- **Build Tool**: Vite 5
- **Styling**: Tailwind CSS v3, PostCSS, Autoprefixer
- **UI Components & Icons**: Lucide React, Sonner (Toast notifications), Google Fonts (*Outfit*, *IBM Plex Sans*, *IBM Plex Mono*)
- **HTTP Client**: Axios with Bearer token interceptor

### Backend
- **Framework**: Python 3.13, FastAPI 0.110, Uvicorn
- **Database & Driver**: MongoDB, Motor (Async driver), PyMongo
- **In-Memory Fallback**: `mongomock-motor` (Automatic database fallback if local MongoDB service is offline)
- **Security & Validation**: PyJWT, bcrypt, Pydantic v2, python-dotenv

---

## Directory Structure

```text
Lead-gen2/
├── backend/
│   ├── .env                   # Backend environment variables
│   ├── .env.example           # Environment template
│   ├── requirements.txt       # Python dependencies
│   ├── server.py             # FastAPI entrypoint & database lifespan
│   ├── routers/
│   │   ├── auth.py            # Auth routes (/api/auth)
│   │   ├── businesses.py      # Lead discovery & stats (/api/businesses)
│   │   └── search_history.py  # User search history (/api/history)
│   └── services/
│       ├── auth_service.py    # JWT, password hashing, brute-force guard
│       ├── scoring.py         # Opportunity Score algorithm & proposal engine
│       └── seed.py            # Database catalog seeder (30 mock businesses)
├── frontend/
│   ├── .env.example           # Frontend environment template
│   ├── index.html             # Vite HTML root
│   ├── package.json           # Frontend dependencies & scripts
│   ├── postcss.config.js      # PostCSS config
│   ├── tailwind.config.js     # Tailwind CSS config
│   ├── vite.config.js         # Vite bundler, @ path alias & proxy config
│   └── src/
│       ├── App.jsx            # Main app router & providers
│       ├── main.jsx           # React DOM render entry
│       ├── index.css          # Global styling & Tailwind directives
│       ├── components/        # Reusable UI components & layouts
│       ├── context/           # AuthContext & ThemeContext
│       ├── lib/               # Axios API client
│       └── pages/             # Dashboard, Search, Detail, History, Login, Register
├── .gitignore                 # Workspace git exclusion rules
└── README.md                  # Project documentation (this file)
```

---

## Environment Variables

### Backend (`backend/.env`)

| Variable | Default Value | Description |
| :--- | :--- | :--- |
| `MONGO_URL` | `mongodb://localhost:27017` | MongoDB connection URI |
| `DB_NAME` | `leadforge` | MongoDB database name |
| `JWT_SECRET` | `leadforge-local-secret-key-2026` | Secret key for signing JWT tokens |
| `ADMIN_EMAIL` | `jayeshsutar76@gmail.com` | Default admin email seed |
| `ADMIN_PASSWORD` | `admin123` | Default admin password seed |
| `FRONTEND_URL` | `http://localhost:3000` | Allowed CORS origin |

### Frontend (`frontend/.env.example`)

| Variable | Default Value | Description |
| :--- | :--- | :--- |
| `VITE_BACKEND_URL` | `http://localhost:8000` | Backend API base URL |

---

## Local Setup & Execution Guide

### Prerequisites

- **Node.js**: v18.x or higher
- **Python**: v3.10 or higher
- **MongoDB** *(Optional)*: If MongoDB daemon (`mongod`) is not running locally, the backend automatically initializes an in-memory database fallback (`mongomock-motor`).

---

### 1. Backend Setup

1. Open a terminal and navigate to the `backend/` directory:
   ```bash
   cd backend
   ```

2. Install Python dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Ensure `backend/.env` exists (or copy from `backend/.env.example`):
   ```bash
   cp .env.example .env
   ```

4. Start the FastAPI server:
   ```bash
   python -m uvicorn server:app --reload --port 8000
   ```
   The backend API will be available at: `http://localhost:8000/api`

---

### 2. Frontend Setup

1. Open a new terminal and navigate to the `frontend/` directory:
   ```bash
   cd frontend
   ```

2. Install Node.js dependencies:
   ```bash
   npm install
   ```

3. Start the Vite development server:
   ```bash
   npm run dev
   ```
   The application will be accessible at: `http://localhost:3000` (or `http://localhost:5173`)

---

## Default Login Credentials

You can sign in immediately using the pre-seeded admin credentials:

- **Email**: `jayeshsutar76@gmail.com`
- **Password**: `admin123`

---

## API Summary

- `POST /api/auth/login` — Sign in and receive JWT token
- `POST /api/auth/register` — Create new account
- `GET /api/auth/me` — Fetch current user profile
- `GET /api/businesses` — Search & filter leads
- `GET /api/businesses/stats` — Fetch dashboard KPIs & top leads
- `GET /api/businesses/{slug}` — Fetch lead details & recommendations
- `GET /api/businesses/{slug}/proposal` — Generate client proposal metadata
- `GET /api/history` — List search history
- `DELETE /api/history` — Clear search history
