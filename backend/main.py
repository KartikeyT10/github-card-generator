from fastapi import FastAPI, HTTPException, Body
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
import uvicorn
import json
import re
import os
from pathlib import Path
from dotenv import load_dotenv
from mcp_server import analyze_profile, generate_card_html, scrape_github

load_dotenv()

app = FastAPI(title="GitHub Dev Card Generator")

# 7. Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Ensure card directory exists. Vercel-style serverless deployments only allow
# writes under /tmp, so generated cards can be recreated by /card/{username}.
STATIC_DIR = Path(os.getenv("CARD_DIR") or ("/tmp/cards" if os.getenv("VERCEL") else "static/cards"))
STATIC_DIR.mkdir(parents=True, exist_ok=True)
FRONTEND_INDEX = Path(__file__).resolve().parent.parent / "frontend" / "index.html"

USERNAME_RE = re.compile(r"^[A-Za-z0-9](?:[A-Za-z0-9-]{0,37}[A-Za-z0-9])?$")


def build_fallback_analysis(github_data: str) -> str:
    """Create a useful card analysis when the Gemini API is unavailable."""
    data = json.loads(github_data)
    languages = data.get("languages") or []
    top_repos = data.get("top_repos") or []
    repo_names = [repo.get("name", "") for repo in top_repos[:3] if repo.get("name")]

    top_skills = languages[:3]
    while len(top_skills) < 3:
        top_skills.append(["GitHub Projects", "Repository Design", "Problem Solving"][len(top_skills)])

    if any(lang in {"TypeScript", "JavaScript"} for lang in languages):
        theme = "builder"
    elif any(lang in {"Python", "Jupyter Notebook", "R"} for lang in languages):
        theme = "researcher"
    elif any(lang in {"C++", "C", "Rust", "Go"} for lang in languages):
        theme = "hacker"
    else:
        theme = "open-source-hero"

    repo_text = ", ".join(repo_names) if repo_names else "their public repositories"
    return json.dumps({
        "developer_vibe": f"{data.get('name') or 'This developer'} builds across {', '.join(languages[:2]) if languages else 'multiple technologies'} with a practical, project-first style.",
        "top_skills": top_skills,
        "fun_fact": f"Their profile highlights {repo_text}, giving the card a clear snapshot of what they like to build.",
        "card_theme": theme,
    })

@app.get("/health")
async def health():
    """6. Cloud Run health check."""
    return {"status": "ok"}

@app.get("/")
async def frontend():
    """Serve the app locally from the same origin as the API."""
    if FRONTEND_INDEX.exists():
        return FileResponse(FRONTEND_INDEX)
    raise HTTPException(status_code=404, detail="Frontend not found")

@app.post("/generate")
async def generate_card(payload: dict = Body(...)):
    """4. POST /generate endpoint."""
    username = (payload.get("username") or "").strip()
    if not username:
        raise HTTPException(status_code=400, detail="Username is required")
    if not USERNAME_RE.match(username):
        raise HTTPException(status_code=400, detail="Enter a valid GitHub username")

    try:
        card_url, html_content = await create_card(username)

        return {
            "card_url": card_url,
            "html": html_content
        }
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))

async def create_card(username: str) -> tuple[str, str]:
    github_data = await scrape_github(username)

    try:
        analysis = await analyze_profile(github_data)
    except Exception as analysis_error:
        print(f"Gemini analysis unavailable, using fallback analysis: {analysis_error}")
        analysis = build_fallback_analysis(github_data)

    await generate_card_html(username, github_data, analysis)

    generated_path = Path("static/cards") / f"{username}.html"
    file_path = STATIC_DIR / f"{username}.html"
    if generated_path.exists() and generated_path.resolve() != file_path.resolve():
        file_path.write_text(generated_path.read_text(encoding="utf-8"), encoding="utf-8")

    html_content = file_path.read_text(encoding="utf-8") if file_path.exists() else ""
    return f"/card/{username}", html_content

@app.get("/card/{username}")
async def get_card(username: str):
    """5. GET /card/{username} to serve saved cards."""
    if not USERNAME_RE.match(username):
        raise HTTPException(status_code=400, detail="Enter a valid GitHub username")

    file_path = STATIC_DIR / f"{username}.html"
    if not file_path.exists():
        await create_card(username)

    if not file_path.exists():
        raise HTTPException(status_code=500, detail="Card could not be generated")
    return FileResponse(file_path)

# Mount generated card files for local/docker use and legacy card URLs.
app.mount("/static", StaticFiles(directory=str(STATIC_DIR.parent)), name="static")

if __name__ == "__main__":
    # Run on 8080 as requested
    uvicorn.run(app, host="0.0.0.0", port=8080)
