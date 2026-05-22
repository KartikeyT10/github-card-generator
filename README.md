# GitHub Dev Card Generator

Create clean, shareable developer profile cards from any public GitHub username.

[![Live Demo](https://img.shields.io/badge/Live-Demo-238636?style=for-the-badge)](https://github-card-generator-one.vercel.app)
[![FastAPI](https://img.shields.io/badge/Backend-FastAPI-009688?style=for-the-badge)](https://fastapi.tiangolo.com/)
[![Vercel](https://img.shields.io/badge/Deploy-Vercel-000000?style=for-the-badge)](https://vercel.com/)
[![Docker](https://img.shields.io/badge/Local-Docker-2496ED?style=for-the-badge)](https://www.docker.com/)

## Overview

GitHub Dev Card Generator turns a username into a polished profile card by combining public GitHub stats, top repositories, language signals, and an AI-generated developer summary. It is built as a lightweight full-stack project with a static frontend, FastAPI backend, Docker support, and Vercel deployment configuration.

**Live app:** https://github-card-generator-one.vercel.app

## Highlights

- Generate cards for any public GitHub profile.
- Fetch profile metadata, followers, repository count, top repositories, and languages.
- Use Gemini for profile analysis when an API key is available.
- Fall back to a local rule-based analysis if Gemini is unavailable.
- Render self-contained HTML cards with theme-aware styling.
- Copy or download generated card output from the UI.
- Run locally with Docker Compose or deploy serverlessly on Vercel.

## Preview Flow

```text
Username input
     |
     v
FastAPI /generate
     |
     v
GitHub API + Gemini analysis
     |
     v
Generated HTML card
     |
     v
Shareable /card/{username} page
```

## Tech Stack

| Layer | Tools |
| --- | --- |
| Frontend | HTML, CSS, JavaScript |
| Backend | FastAPI, Uvicorn, HTTPX |
| AI | Google Gemini API |
| Data | GitHub REST API |
| Local runtime | Docker Compose |
| Deployment | Vercel Python serverless functions |

## Project Structure

```text
github-card-generator/
|-- api/
|   `-- index.py              # Vercel serverless entrypoint
|-- backend/
|   |-- main.py               # FastAPI routes
|   |-- mcp_server.py         # GitHub scraping, AI analysis, card HTML generation
|   |-- requirements.txt      # Backend dependencies
|   `-- static/cards/         # Runtime card output directory
|-- frontend/
|   |-- index.html            # User interface
|   `-- Dockerfile            # Static frontend container
|-- docker-compose.yml        # Local two-service setup
|-- requirements.txt          # Vercel dependency entrypoint
`-- vercel.json               # Production routing/build config
```

## Workshop Reference

This project was built while following the GeeksforGeeks workshop **Building Personalized Agents With ADK, CP And Memory Bank**.

- Workshop video: https://www.youtube.com/live/mIeMRlWoCf0
- LinkedIn experience post: To be added after publishing
- Post draft: [LINKEDIN_POST.md](LINKEDIN_POST.md)

## Getting Started

Clone the repository:

```powershell
git clone https://github.com/KartikeyT10/github-card-generator.git
cd github-card-generator
```

Create your environment file:

```powershell
Copy-Item .env.example .env
```

Add your keys:

```env
GOOGLE_API_KEY=your_google_api_key_here
GITHUB_TOKEN=your_github_token_here
```

`GITHUB_TOKEN` is optional, but recommended because it increases GitHub API limits.

## Run Locally

Start the full app with Docker Compose:

```powershell
docker compose up --build
```

Open the app:

```text
http://localhost
```

Backend health check:

```text
http://localhost:8080/health
```

## API Reference

### Health Check

```http
GET /health
```

Response:

```json
{
  "status": "ok"
}
```

### Generate Card

```http
POST /generate
Content-Type: application/json
```

Request:

```json
{
  "username": "octocat"
}
```

Response:

```json
{
  "card_url": "/card/octocat",
  "html": "<!DOCTYPE html>..."
}
```

### View Card

```http
GET /card/{username}
```

Example:

```text
https://github-card-generator-one.vercel.app/card/octocat
```

## Deploying To Vercel

The repository includes everything needed for Vercel:

- `api/index.py` exposes the FastAPI app as a serverless function.
- `vercel.json` routes frontend, API, health, and card pages.
- Root `requirements.txt` installs Python dependencies during build.

Add these environment variables in Vercel:

| Variable | Required | Purpose |
| --- | --- | --- |
| `GOOGLE_API_KEY` | Yes | Enables Gemini profile analysis |
| `GITHUB_TOKEN` | No | Raises GitHub API rate limits |

Deploy from the CLI:

```powershell
vercel --prod
```

## Notes

- Generated cards are intentionally ignored by Git because they are runtime output.
- The backend can regenerate card pages on demand.
- If Gemini fails or is unavailable, the app still returns a useful generated card using fallback analysis.

## Author

Built by [KartikeyT10](https://github.com/KartikeyT10).
