# GitHub Dev Card Generator

Generate shareable developer profile cards from public GitHub usernames. The app fetches GitHub profile and repository data, analyzes the developer profile with Gemini when available, and renders a polished HTML card.

Live app: https://github-card-generator-one.vercel.app

## Tech Stack

- FastAPI backend
- Static HTML/CSS/JavaScript frontend
- GitHub REST API
- Google Gemini API with a local fallback analysis path
- Docker Compose for local container runs
- Vercel deployment config

## Local Setup

1. Copy `.env.example` to `.env`.
2. Add your `GOOGLE_API_KEY` and optional `GITHUB_TOKEN`.
3. Start with Docker Compose:

```powershell
docker compose up --build
```

The app runs on:

- Frontend: `http://localhost`
- Backend: `http://localhost:8080`

## API

- `GET /health` checks backend status.
- `POST /generate` accepts `{ "username": "octocat" }` and returns a card URL plus HTML.
- `GET /card/{username}` renders a generated card.

## Deployment

The repo includes `vercel.json`, `api/index.py`, and root `requirements.txt` for Vercel. Add the required environment variables in Vercel before deploying:

- `GOOGLE_API_KEY`
- `GITHUB_TOKEN` optional, but recommended for higher GitHub API limits
